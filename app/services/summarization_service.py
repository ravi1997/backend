"""
Summarization Service

Provides automated summarization of form responses:
- Extractive summarization (TF-IDF based)
- Abstractive summarization (Ollama LLM)
- Theme-based summarization
- Executive summary generation
- Summary snapshots and trend comparison

Task: T-M2-03 - Automated Summarization
Task: M2-EXT-03c - Add summary comparison across time periods
"""

import hashlib
import re
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta
from flask import current_app
from app.services.ollama_service import OllamaService
from app.models.Form import SummarySnapshot


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
                        config: Optional[Dict] = None,
                        max_points: Optional[int] = None,
                        detail_level: str = "standard",
                        include_examples: bool = True) -> Dict[str, Any]:
        """
        Generate summary using hybrid approach (extractive + abstractive).
        
        Args:
            texts: List of response dicts with 'id', 'text', 'sentiment'
            strategy: Summarization strategy (extractive, abstractive, hybrid)
            format_type: Output format (bullet_points, themes, executive)
            config: Configuration options
            max_points: Override default max bullet points (3-10)
            detail_level: Detail level ("brief", "standard", "detailed")
            include_examples: Whether to include example quotes
            
        Returns:
            Summary result dict with custom_config and points_generated
        """
        config = config or {}
        
        # Apply detail level presets if max_points not explicitly provided
        if max_points is None:
            detail_presets = {
                "brief": 3,
                "standard": 5,
                "detailed": 10
            }
            max_points = detail_presets.get(detail_level, 5)
        
        # Apply detail level to include_examples if not in config
        if 'include_examples' not in config:
            config['include_examples'] = include_examples
        
        focus_area = config.get('focus_area', 'all')
        include_sentiment = config.get('include_sentiment', True)
        include_quotes = config.get('include_quotes', True)
        
        # Track custom configuration
        custom_config = {
            "max_points": max_points,
            "detail_level": detail_level,
            "include_examples": include_examples,
            "focus_area": focus_area,
            "strategy": strategy
        }
        
        # Extract text and group by sentiment
        all_texts = [str(t.get('text', t.get('data', {}))) for t in texts]
        sentiment_groups = defaultdict(list)
        
        for i, t in enumerate(texts):
            sentiment = t.get('sentiment', {}).get('label', 'neutral') if include_sentiment else 'all'
            sentiment_groups[sentiment].append(all_texts[i])
        
        if strategy == "extractive":
            bullet_points = cls.extractive_summarize(all_texts, max_points, focus_area)
            theme_analysis = cls._analyze_themes(all_texts, detail_level, include_examples)
            
        elif strategy == "abstractive":
            prompt = f"""
            Summarize the following {len(texts)} feedback responses into {max_points} key bullet points.
            Focus on: {focus_area}
            
            Responses:
            """
            
            try:
                abstract_summary = cls.abstractive_summarize(all_texts, prompt)
                bullet_points = [{'point': abstract_summary, 'supporting_count': len(texts), 'confidence': 0.8}]
                theme_analysis = cls._analyze_themes(all_texts, detail_level, include_examples)
            except (ConnectionError, TimeoutError):
                # Fallback to extractive
                bullet_points = cls.extractive_summarize(all_texts, max_points, focus_area)
                theme_analysis = cls._analyze_themes(all_texts, detail_level, include_examples)
        
        else:  # hybrid
            # Get extractive bullet points
            bullet_points = cls.extractive_summarize(all_texts, max_points, focus_area)
            
            # Generate abstractive theme analysis
            try:
                theme_analysis = cls._generate_theme_analysis(all_texts, focus_area, detail_level, include_examples)
            except (ConnectionError, TimeoutError):
                theme_analysis = cls._analyze_themes(all_texts, detail_level, include_examples)
        
        # Apply detail level logic for examples
        examples_count = 0
        if include_examples:
            example_presets = {
                "brief": 0,
                "standard": 2,
                "detailed": 5
            }
            examples_count = example_presets.get(detail_level, 2)
            
            # Add examples to bullet points if requested
            if examples_count > 0 and bullet_points:
                # Add example quotes to some bullet points
                for i in range(min(examples_count, len(bullet_points))):
                    if i < len(texts):
                        bullet_points[i]['example'] = texts[i].get('text', '')[:200]
        
        return {
            "format": format_type,
            "bullet_points": bullet_points,
            "theme_analysis": theme_analysis,
            "sentiment_breakdown": {
                s: len(t) for s, t in sentiment_groups.items()
            },
            "custom_config": custom_config,
            "points_generated": len(bullet_points)
        }
    
    @classmethod
    def _analyze_themes(cls, texts: List[str], detail_level: str = "standard",
                       include_examples: bool = True) -> Dict[str, Any]:
        """
        Analyze themes in text collection.
        
        Args:
            texts: List of text documents
            detail_level: Detail level ("brief", "standard", "detailed")
            include_examples: Whether to include example quotes
            
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
        theme_examples = defaultdict(list)
        
        for text in texts:
            text_lower = text.lower()
            for theme, keywords in theme_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    theme_counts[theme] += 1
                    # Collect examples for each theme
                    if include_examples and len(theme_examples[theme]) < 5:
                        theme_examples[theme].append(text[:150])
        
        # Apply detail level logic
        result = {}
        for theme, count in theme_counts.items():
            theme_data = {
                "mentions": count,
                "sentiment": "mixed"  # Would need sentiment analysis per theme
            }
            
            # Add examples if requested and detail level allows
            if include_examples and detail_level != "brief":
                example_presets = {
                    "standard": 2,
                    "detailed": 5
                }
                examples_count = example_presets.get(detail_level, 2)
                if theme_examples[theme]:
                    theme_data["examples"] = theme_examples[theme][:examples_count]
            
            result[theme] = theme_data
        
        return result
    
    @classmethod
    def _generate_theme_analysis(cls, texts: List[str], focus_area: str,
                                detail_level: str = "standard",
                                include_examples: bool = True) -> Dict[str, Any]:
        """
        Generate theme analysis using LLM.
        
        Args:
            texts: List of text documents
            focus_area: Focus area for analysis
            detail_level: Detail level ("brief", "standard", "detailed")
            include_examples: Whether to include example quotes
            
        Returns:
            Theme analysis dict
        """
        combined = " ".join(texts[:50])[:4000]
        
        # Adjust prompt based on detail level
        examples_instruction = ""
        if include_examples and detail_level != "brief":
            examples_instruction = "- Include 2-5 example quotes for each theme" if detail_level == "detailed" else "- Include 2 example quotes for each theme"
        
        prompt = f"""
        Analyze the following feedback responses and identify main themes.
        Focus on: {focus_area}
        
        {examples_instruction}
        
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
            return cls._analyze_themes(texts, detail_level, include_examples)
    
    @classmethod
    def generate_executive_summary(cls, texts: List[str], audience: str = "leadership",
                                  tone: str = "formal", max_points: Optional[int] = None,
                                  detail_level: str = "standard",
                                  include_examples: bool = True) -> Dict[str, Any]:
        """
        Generate executive summary for leadership.
        
        Args:
            texts: List of response texts
            audience: Target audience (leadership, operations, product)
            tone: Summary tone (formal, concise)
            max_points: Override default max bullet points (3-10)
            detail_level: Detail level ("brief", "standard", "detailed")
            include_examples: Whether to include example quotes
            
        Returns:
            Executive summary dict with custom_config and points_generated
        """
        # Apply detail level presets if max_points not explicitly provided
        if max_points is None:
            detail_presets = {
                "brief": 3,
                "standard": 5,
                "detailed": 10
            }
            max_points = detail_presets.get(detail_level, 5)
        
        # Track custom configuration
        custom_config = {
            "max_points": max_points,
            "detail_level": detail_level,
            "include_examples": include_examples,
            "audience": audience,
            "tone": tone
        }
        
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
            
            # Apply detail level logic for key findings
            findings_count = max_points
            key_findings = key_findings[:findings_count]
            
            # Add examples if requested
            if include_examples:
                example_presets = {
                    "brief": 0,
                    "standard": 2,
                    "detailed": 5
                }
                examples_count = example_presets.get(detail_level, 2)
                if examples_count > 0 and texts:
                    # Add example quotes to key findings
                    for i in range(min(examples_count, len(key_findings))):
                        if i < len(texts):
                            key_findings[i] = f"{key_findings[i]} Example: \"{texts[i][:100]}...\""
            
            return {
                "overview": response_text.split('\n')[0] if '\n' in response_text else response_text,
                "key_findings": key_findings,
                "recommendations": recommendations[:3],
                "metrics": {
                    "total_responses": len(texts),
                    "response_rate": 0.78  # Would be calculated from actual data
                },
                "custom_config": custom_config,
                "points_generated": len(key_findings)
            }
            
        except (ConnectionError, TimeoutError):
            return {
                "overview": f"Analysis of {len(texts)} responses shows mixed sentiment.",
                "key_findings": ["Unable to generate detailed findings - Ollama unavailable"],
                "recommendations": ["Retry when Ollama service is available"],
                "metrics": {
                    "total_responses": len(texts),
                    "response_rate": 0.78
                },
                "custom_config": custom_config,
                "points_generated": 1
            }
    
    @classmethod
    def save_summary_snapshot(cls, form_id: str, summary_data: Dict[str, Any],
                             period_start: datetime, period_end: datetime,
                             period_label: str, created_by: str,
                             strategy: str = "hybrid", response_count: int = 0) -> str:
        """
        Save a summary snapshot for trend analysis.
        
        Args:
            form_id: The form ID
            summary_data: Complete summary data from summarization
            period_start: Start of the period
            period_end: End of the period
            period_label: Human-readable period label (e.g., "last 7 days")
            created_by: User ID who created the snapshot
            strategy: Summarization strategy used
            response_count: Number of responses analyzed
            
        Returns:
            Snapshot ID
        """
        try:
            snapshot = SummarySnapshot(
                form_id=form_id,
                timestamp=datetime.utcnow(),
                period_start=period_start,
                period_end=period_end,
                period_label=period_label,
                summary_data=summary_data,
                created_by=created_by,
                response_count=response_count,
                strategy_used=strategy
            )
            snapshot.save()
            current_app.logger.info(f"Saved summary snapshot {snapshot.id} for form {form_id}")
            return str(snapshot.id)
        except Exception as e:
            current_app.logger.error(f"Failed to save summary snapshot: {str(e)}")
            raise
    
    @classmethod
    def compare_summaries(cls, form_id: str, period_ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare summaries across multiple time periods.
        
        Args:
            form_id: The form ID
            period_ranges: List of period dicts with 'start' and 'end' datetime strings
            
        Returns:
            Comparison dict with trend analysis
        """
        from datetime import datetime as dt
        
        # Retrieve snapshots for each period
        snapshots = []
        for period in period_ranges:
            period_start = dt.fromisoformat(period['start'].replace('Z', '+00:00'))
            period_end = dt.fromisoformat(period['end'].replace('Z', '+00:00'))
            
            # Find snapshot matching this period
            snapshot = SummarySnapshot.objects(
                form_id=form_id,
                period_start__gte=period_start,
                period_end__lte=period_end
            ).order_by('-timestamp').first()
            
            if snapshot:
                snapshots.append({
                    'period': period.get('label', f"{period['start']} to {period['end']}"),
                    'snapshot_id': str(snapshot.id),
                    'data': snapshot.summary_data,
                    'response_count': snapshot.response_count,
                    'timestamp': snapshot.timestamp.isoformat()
                })
        
        if len(snapshots) < 2:
            return {
                'form_id': form_id,
                'snapshots_found': len(snapshots),
                'message': 'Need at least 2 snapshots for comparison',
                'snapshots': snapshots
            }
        
        # Compare key metrics
        comparison = {
            'form_id': form_id,
            'snapshots_count': len(snapshots),
            'snapshots': snapshots,
            'trend_analysis': {}
        }
        
        # Sentiment trend comparison
        sentiment_trends = []
        for snap in snapshots:
            sentiment_breakdown = snap['data'].get('sentiment_breakdown', {})
            total = sum(sentiment_breakdown.values()) if sentiment_breakdown else 1
            positive_pct = (sentiment_breakdown.get('positive', 0) / total) * 100 if total > 0 else 0
            negative_pct = (sentiment_breakdown.get('negative', 0) / total) * 100 if total > 0 else 0
            neutral_pct = (sentiment_breakdown.get('neutral', 0) / total) * 100 if total > 0 else 0
            
            sentiment_trends.append({
                'period': snap['period'],
                'positive_pct': round(positive_pct, 2),
                'negative_pct': round(negative_pct, 2),
                'neutral_pct': round(neutral_pct, 2),
                'total_responses': snap['response_count']
            })
        
        comparison['trend_analysis']['sentiment'] = sentiment_trends
        
        # Calculate sentiment change between first and last period
        if len(sentiment_trends) >= 2:
            first = sentiment_trends[0]
            last = sentiment_trends[-1]
            comparison['trend_analysis']['sentiment_change'] = {
                'positive_change': round(last['positive_pct'] - first['positive_pct'], 2),
                'negative_change': round(last['negative_pct'] - first['negative_pct'], 2),
                'neutral_change': round(last['neutral_pct'] - first['neutral_pct'], 2)
            }
        
        # Theme comparison
        theme_trends = {}
        for snap in snapshots:
            theme_analysis = snap['data'].get('theme_analysis', {})
            for theme, theme_data in theme_analysis.items():
                if theme not in theme_trends:
                    theme_trends[theme] = []
                theme_trends[theme].append({
                    'period': snap['period'],
                    'mentions': theme_data.get('mentions', 0)
                })
        
        comparison['trend_analysis']['themes'] = theme_trends
        
        # Response count trend
        response_counts = [{'period': snap['period'], 'count': snap['response_count']} for snap in snapshots]
        comparison['trend_analysis']['response_counts'] = response_counts
        
        if len(response_counts) >= 2:
            comparison['trend_analysis']['response_change'] = {
                'absolute': response_counts[-1]['count'] - response_counts[0]['count'],
                'percentage': round(
                    ((response_counts[-1]['count'] - response_counts[0]['count']) /
                     response_counts[0]['count']) * 100, 2
                ) if response_counts[0]['count'] > 0 else 0
            }
        
        # Generate trend insights
        insights = []
        if 'sentiment_change' in comparison['trend_analysis']:
            change = comparison['trend_analysis']['sentiment_change']
            if change['positive_change'] > 5:
                insights.append("Positive sentiment has improved significantly.")
            elif change['negative_change'] > 5:
                insights.append("Negative sentiment has increased - attention may be needed.")
        
        if 'response_change' in comparison['trend_analysis']:
            resp_change = comparison['trend_analysis']['response_change']
            if resp_change['percentage'] > 10:
                insights.append(f"Response volume increased by {resp_change['percentage']}%.")
            elif resp_change['percentage'] < -10:
                insights.append(f"Response volume decreased by {abs(resp_change['percentage'])}%.")
        
        comparison['trend_analysis']['insights'] = insights
        
        return comparison
    
    @classmethod
    def get_summary_trends(cls, form_id: str, metric: str = "sentiment",
                          limit: int = 10) -> Dict[str, Any]:
        """
        Get trend data for a specific metric over time.
        
        Args:
            form_id: The form ID
            metric: Metric to track (sentiment, theme, response_count)
            limit: Maximum number of snapshots to include
            
        Returns:
            Trend data dict
        """
        # Get recent snapshots
        snapshots = SummarySnapshot.objects(
            form_id=form_id
        ).order_by('-timestamp').limit(limit)
        
        if not snapshots:
            return {
                'form_id': form_id,
                'metric': metric,
                'message': 'No snapshots found for this form',
                'data': []
            }
        
        # Reverse to get chronological order
        snapshots = list(snapshots)[::-1]
        
        trend_data = {
            'form_id': form_id,
            'metric': metric,
            'snapshots_count': len(snapshots),
            'data': []
        }
        
        for snapshot in snapshots:
            data_point = {
                'snapshot_id': str(snapshot.id),
                'timestamp': snapshot.timestamp.isoformat(),
                'period_label': snapshot.period_label,
                'period_start': snapshot.period_start.isoformat(),
                'period_end': snapshot.period_end.isoformat(),
                'response_count': snapshot.response_count
            }
            
            # Add metric-specific data
            if metric == "sentiment":
                sentiment_breakdown = snapshot.summary_data.get('sentiment_breakdown', {})
                total = sum(sentiment_breakdown.values()) if sentiment_breakdown else 1
                data_point['positive_pct'] = round((sentiment_breakdown.get('positive', 0) / total) * 100, 2) if total > 0 else 0
                data_point['negative_pct'] = round((sentiment_breakdown.get('negative', 0) / total) * 100, 2) if total > 0 else 0
                data_point['neutral_pct'] = round((sentiment_breakdown.get('neutral', 0) / total) * 100, 2) if total > 0 else 0
            
            elif metric == "theme":
                theme_analysis = snapshot.summary_data.get('theme_analysis', {})
                data_point['themes'] = [
                    {'name': theme, 'mentions': data.get('mentions', 0)}
                    for theme, data in theme_analysis.items()
                ]
            
            elif metric == "response_count":
                data_point['count'] = snapshot.response_count
            
            trend_data['data'].append(data_point)
        
        # Calculate trend direction
        if len(trend_data['data']) >= 2 and metric == "response_count":
            first_count = trend_data['data'][0].get('count', 0)
            last_count = trend_data['data'][-1].get('count', 0)
            trend_data['trend_direction'] = 'increasing' if last_count > first_count else 'decreasing' if last_count < first_count else 'stable'
            trend_data['trend_percentage'] = round(((last_count - first_count) / first_count) * 100, 2) if first_count > 0 else 0
        
        return trend_data
    
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
    
    # --- Cache Invalidation Methods ---
    # Task: M2-INT-01b - Add cache invalidation rules
    
    @classmethod
    def invalidate_cache(cls, form_id: str = None, user_id: str = None,
                       pattern: str = "all", response_ids: List[str] = None) -> int:
        """
        Invalidate cache keys for summarization results.
        
        Supports pattern-based invalidation:
        - all: Invalidate all summary cache
        - by_form: Invalidate all cache for specific form
        - by_user: Invalidate all cache for specific user
        - by_responses: Invalidate cache for specific response IDs
        
        Args:
            form_id: Form identifier (optional)
            user_id: User identifier (optional)
            pattern: Invalidation pattern (all, by_form, by_user, by_responses)
            response_ids: List of response IDs (required for by_responses pattern)
            
        Returns:
            Number of cache keys invalidated
        """
        from app.utils.redis_client import redis_client
        
        keys_invalidated = 0
        
        # Pattern: Invalidate all summary cache
        if pattern == "all":
            # Clear all summary:* keys from memory cache
            keys_to_delete = [
                k for k in redis_client._memory_cache.keys()
                if k.startswith('summary:')
            ]
            for key in keys_to_delete:
                redis_client.delete(key)
                keys_invalidated += 1
            
            # Also clear executive summary cache
            exec_keys = [
                k for k in redis_client._memory_cache.keys()
                if 'executive' in k
            ]
            for key in exec_keys:
                redis_client.delete(key)
                keys_invalidated += 1
            
            current_app.logger.info(f"Invalidated all summary cache: {keys_invalidated} keys")
            return keys_invalidated
        
        # Pattern: Invalidate all cache for specific form
        elif pattern == "by_form":
            if not form_id:
                current_app.logger.warning("by_form pattern requires form_id parameter")
                return 0
            
            # Clear all summary keys for this form
            keys_to_delete = [
                k for k in redis_client._memory_cache.keys()
                if k.startswith(f'summary:{form_id}:')
            ]
            
            # Clear executive summary cache for this form
            exec_keys = [
                k for k in redis_client._memory_cache.keys()
                if f'executive:{form_id}' in k
            ]
            
            keys_to_delete.extend(exec_keys)
            
            for key in keys_to_delete:
                redis_client.delete(key)
                keys_invalidated += 1
            
            current_app.logger.info(f"Invalidated cache for form {form_id}: {keys_invalidated} keys")
            return keys_invalidated
        
        # Pattern: Invalidate all cache for specific user
        elif pattern == "by_user":
            if not user_id:
                current_app.logger.warning("by_user pattern requires user_id parameter")
                return 0
            
            # Clear user-specific summary cache
            # Note: Summaries are typically form-scoped, not user-scoped
            # This clears any user-specific trend analysis cache
            keys_to_delete = [
                k for k in redis_client._memory_cache.keys()
                if 'trends' in k and user_id in k
            ]
            
            for key in keys_to_delete:
                redis_client.delete(key)
                keys_invalidated += 1
            
            current_app.logger.info(f"Invalidated cache for user {user_id}: {keys_invalidated} keys")
            return keys_invalidated
        
        # Pattern: Invalidate cache for specific response IDs
        elif pattern == "by_responses":
            if not response_ids:
                current_app.logger.warning("by_responses pattern requires response_ids parameter")
                return 0
            
            # Find and delete cache keys that include these response IDs
            # Since we can't easily match without storing metadata,
            # we'll clear all summary cache for the form if form_id is provided
            if form_id:
                keys_to_delete = [
                    k for k in redis_client._memory_cache.keys()
                    if k.startswith(f'summary:{form_id}:')
                ]
                
                for key in keys_to_delete:
                    redis_client.delete(key)
                    keys_invalidated += 1
            
            current_app.logger.info(f"Invalidated cache for {len(response_ids)} responses: {keys_invalidated} keys")
            return keys_invalidated
        
        else:
            current_app.logger.warning(f"Unknown invalidation pattern: {pattern}")
            return 0
