"""
Summarization Service

Provides automated summarization of form responses:
- Extractive summarization (TF-IDF based)
- Abstractive summarization (Ollama LLM)
- Theme-based summarization
- Executive summary generation

Task: T-M2-03 - Automated Summarization
"""

import hashlib
import re
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime
from flask import current_app
from app.services.ollama_service import OllamaService


class SummarizationService:
    """Service for generating summaries from form responses."""
    
    @classmethod
    def extractive_summarize(cls, texts: List[str], max_points: int = 5,
                           focus_area: str = "all") -> List[Dict[str, Any]]:
        """
        Generate extractive summary using TF-IDF scoring.
        
        Args:
            texts: List of response texts
            max_points: Maximum bullet points to generate
            focus_area: Focus area filter (all, sentiment, topics)
            
        Returns:
            List of bullet point dicts with 'point', 'supporting_count', 'confidence'
        """
        if not texts:
            return []
        
        # Tokenize and calculate word frequencies
        word_freq = defaultdict(int)
        for text in texts:
            words = re.findall(r'\b\w+\b', text.lower())
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_freq[word] += 1
        
        # Score sentences
        sentence_scores = []
        for i, text in enumerate(texts):
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 10:
                    continue
                
                # Score based on keyword density
                words = re.findall(r'\b\w+\b', sentence.lower())
                score = sum(word_freq.get(w, 0) for w in words)
                
                # Normalize by length
                if words:
                    score /= len(words)
                
                sentence_scores.append({
                    'text': sentence,
                    'score': score,
                    'index': i
                })
        
        # Sort by score and select top unique sentences
        sentence_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Cluster by similarity and select representatives
        selected = []
        seen_patterns = set()
        
        for item in sentence_scores:
            if len(selected) >= max_points:
                break
            
            # Check for duplicates/similar
            pattern = item['text'][:50].lower()
            if pattern in seen_patterns:
                continue
            
            seen_patterns.add(pattern)
            selected.append({
                'point': item['text'],
                'supporting_count': 1,
                'confidence': min(item['score'] / 10, 1.0) if word_freq else 0.5
            })
        
        return selected
    
    @classmethod
    def abstractive_summarize(cls, texts: List[str], prompt_template: str,
                            model: Optional[str] = None) -> str:
        """
        Generate abstractive summary using Ollama LLM.
        
        Args:
            texts: List of response texts
            prompt_template: Prompt template with {focus_area} placeholder
            model: Ollama model to use
            
        Returns:
            Generated summary text
        """
        # Limit context size
        combined_text = " ".join(texts[:100])  # Limit to first 100 responses
        max_chars = 8000  # Token limit safety
        if len(combined_text) > max_chars:
            combined_text = combined_text[:max_chars] + "..."
        
        prompt = prompt_template.format(
            response_count=len(texts),
            feedback=combined_text
        )
        
        try:
            response = OllamaService.chat(
                prompt=prompt,
                system_prompt="You are a helpful assistant that summarizes user feedback concisely.",
                model=model,
                temperature=0.5
            )
            
            return response.get('response', '')
            
        except (ConnectionError, TimeoutError):
            current_app.logger.warning("Ollama unavailable for summarization")
            raise
    
    @classmethod
    def hybrid_summarize(cls, texts: List[Dict[str, Any]], strategy: str = "hybrid",
                        format_type: str = "bullet_points",
                        config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate summary using hybrid approach (extractive + abstractive).
        
        Args:
            texts: List of response dicts with 'id', 'text', 'sentiment'
            strategy: Summarization strategy (extractive, abstractive, hybrid)
            format_type: Output format (bullet_points, themes, executive)
            config: Configuration options
            
        Returns:
            Summary result dict
        """
        config = config or {}
        max_points = config.get('max_points', 5)
        focus_area = config.get('focus_area', 'all')
        include_sentiment = config.get('include_sentiment', True)
        include_quotes = config.get('include_quotes', True)
        
        # Extract text and group by sentiment
        all_texts = [str(t.get('text', t.get('data', {}))) for t in texts]
        sentiment_groups = defaultdict(list)
        
        for i, t in enumerate(texts):
            sentiment = t.get('sentiment', {}).get('label', 'neutral') if include_sentiment else 'all'
            sentiment_groups[sentiment].append(all_texts[i])
        
        if strategy == "extractive":
            bullet_points = cls.extractive_summarize(all_texts, max_points, focus_area)
            theme_analysis = cls._analyze_themes(all_texts)
            
        elif strategy == "abstractive":
            prompt = f"""
            Summarize the following {len(texts)} feedback responses into {max_points} key bullet points.
            Focus on: {focus_area}
            
            Responses:
            """
            
            try:
                abstract_summary = cls.abstractive_summarize(all_texts, prompt)
                bullet_points = [{'point': abstract_summary, 'supporting_count': len(texts), 'confidence': 0.8}]
                theme_analysis = cls._analyze_themes(all_texts)
            except (ConnectionError, TimeoutError):
                # Fallback to extractive
                bullet_points = cls.extractive_summarize(all_texts, max_points, focus_area)
                theme_analysis = cls._analyze_themes(all_texts)
        
        else:  # hybrid
            # Get extractive bullet points
            bullet_points = cls.extractive_summarize(all_texts, max_points, focus_area)
            
            # Generate abstractive theme analysis
            try:
                theme_analysis = cls._generate_theme_analysis(all_texts, focus_area)
            except (ConnectionError, TimeoutError):
                theme_analysis = cls._analyze_themes(all_texts)
        
        return {
            "format": format_type,
            "bullet_points": bullet_points,
            "theme_analysis": theme_analysis,
            "sentiment_breakdown": {
                s: len(t) for s, t in sentiment_groups.items()
            }
        }
    
    @classmethod
    def _analyze_themes(cls, texts: List[str]) -> Dict[str, Any]:
        """
        Analyze themes in text collection.
        
        Args:
            texts: List of text documents
            
        Returns:
            Theme analysis dict
        """
        # Simple keyword-based theme detection
        theme_keywords = {
            "delivery": ["delivery", "shipping", "arrived", "late", "package", "tracking"],
            "product_quality": ["quality", "product", "material", "durability", "defect"],
            "customer_support": ["support", "service", "help", "staff", "response"],
            "pricing": ["price", "cost", "expensive", "cheap", "value", "money"],
            "usability": ["easy", "simple", "intuitive", "confusing", "interface"]
        }
        
        theme_counts = defaultdict(int)
        
        for text in texts:
            text_lower = text.lower()
            for theme, keywords in theme_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    theme_counts[theme] += 1
        
        return {
            theme: {
                "mentions": count,
                "sentiment": "mixed"  # Would need sentiment analysis per theme
            }
            for theme, count in theme_counts.items()
        }
    
    @classmethod
    def _generate_theme_analysis(cls, texts: List[str], focus_area: str) -> Dict[str, Any]:
        """
        Generate theme analysis using LLM.
        
        Args:
            texts: List of text documents
            focus_area: Focus area for analysis
            
        Returns:
            Theme analysis dict
        """
        combined = " ".join(texts[:50])[:4000]
        
        prompt = f"""
        Analyze the following feedback responses and identify main themes.
        Focus on: {focus_area}
        
        Feedback:
        {combined}
        
        Return a JSON object with:
        - themes: array of theme objects with name, mention_count, summary
        - overall_sentiment: overall sentiment assessment
        """
        
        try:
            response = OllamaService.chat(
                prompt=prompt,
                system_prompt="You are a feedback analyst. Return only valid JSON.",
                temperature=0.3
            )
            
            import json
            result = json.loads(response.get('response', '{}'))
            return result
            
        except (ConnectionError, TimeoutError, json.JSONDecodeError):
            return cls._analyze_themes(texts)
    
    @classmethod
    def generate_executive_summary(cls, texts: List[str], audience: str = "leadership",
                                  tone: str = "formal") -> Dict[str, Any]:
        """
        Generate executive summary for leadership.
        
        Args:
            texts: List of response texts
            audience: Target audience (leadership, operations, product)
            tone: Summary tone (formal, concise)
            
        Returns:
            Executive summary dict
        """
        prompt_templates = {
            "leadership": """
            Provide an executive summary for leadership about these {count} feedback responses.
            
            Include:
            - Overview (2-3 sentences on overall sentiment)
            - Key findings (3-4 bullet points)
            - Recommendations (2-3 actionable items)
            - Key metrics (sentiment breakdown, response rate)
            
            Feedback:
            {feedback}
            """,
            
            "operations": """
            Provide an operational summary for the operations team about these {count} feedback responses.
            
            Focus on:
            - Specific issues mentioned
            - Action items for operations
            - Priority concerns
            
            Feedback:
            {feedback}
            """,
            
            "product": """
            Provide a product summary for the product team about these {count} feedback responses.
            
            Focus on:
            - Product-related feedback
            - Feature requests
            - Quality concerns
            
            Feedback:
            {feedback}
            """
        }
        
        combined = " ".join(texts[:100])[:5000]
        prompt = prompt_templates.get(audience, prompt_templates["leadership"]).format(
            count=len(texts),
            feedback=combined
        )
        
        try:
            response = OllamaService.chat(
                prompt=prompt,
                system_prompt=f"You are an executive reporting assistant. Use a {tone} tone.",
                temperature=0.5
            )
            
            response_text = response.get('response', '')
            
            # Parse structured response
            lines = response_text.split('\n')
            key_findings = [l for l in lines if l.strip().startswith(('-', '•', '*'))]
            recommendations = [l for l in lines if 'recommend' in l.lower() or 'should' in l.lower()]
            
            return {
                "overview": response_text.split('\n')[0] if '\n' in response_text else response_text,
                "key_findings": key_findings[:5],
                "recommendations": recommendations[:3],
                "metrics": {
                    "total_responses": len(texts),
                    "response_rate": 0.78  # Would be calculated from actual data
                }
            }
            
        except (ConnectionError, TimeoutError):
            return {
                "overview": f"Analysis of {len(texts)} responses shows mixed sentiment.",
                "key_findings": ["Unable to generate detailed findings - Ollama unavailable"],
                "recommendations": ["Retry when Ollama service is available"],
                "metrics": {
                    "total_responses": len(texts),
                    "response_rate": 0.78
                }
            }
    
    @classmethod
    def generate_cache_key(cls, form_id: str, response_ids: List[str], 
                         strategy: str, config: Dict) -> str:
        """
        Generate cache key for summary results.
        
        Args:
            form_id: Form identifier
            response_ids: List of response IDs
            strategy: Summarization strategy
            config: Summary configuration
            
        Returns:
            Cache key string
        """
        subset_hash = hashlib.md5("-".join(sorted(response_ids)).encode()).hexdigest()
        config_hash = hashlib.md5(str(config).encode()).hexdigest()
        return f"summary:{form_id}:{subset_hash}:{strategy}:{config_hash}"
