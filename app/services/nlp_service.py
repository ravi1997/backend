"""
NLP Search Service

Provides natural language search capabilities for form responses:
- Query parsing and intent extraction
- Sentiment-based filtering
- Topic extraction
- Semantic search using Ollama embeddings

Task: T-M2-02 - NLP Search Enhancement
"""

import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from flask import current_app
from app.services.ollama_service import OllamaService


class NLPSearchService:
    """Service for natural language search across form responses."""
    
    # Sentiment keywords for pattern matching
    SENTIMENT_POSITIVE = [
        "happy", "satisfied", "good", "great", "excellent", "amazing",
        "love", "best", "perfect", "pleased", "thank", "thanks", "awesome"
    ]
    
    SENTIMENT_NEGATIVE = [
        "unhappy", "dissatisfied", "bad", "terrible", "awful", "hate",
        "worst", "poor", "disappointed", "frustrated", "angry", "issue",
        "problem", "complaint", "slow", "late", "broken"
    ]
    
    # Time-related keywords
    TIME_KEYWORDS = [
        "today", "yesterday", "last week", "last month", "last year",
        "recent", "ago", "before", "after", "since", "until"
    ]
    
    @classmethod
    def parse_query(cls, query: str) -> Dict[str, Any]:
        """
        Parse natural language query to extract intent and filters.
        
        Args:
            query: Natural language search query
            
        Returns:
            Dict with 'sentiment_filter', 'topic', 'time_filter', 'raw_query' keys
        """
        query_lower = query.lower()
        
        # Extract sentiment filter
        sentiment_filter = None
        positive_match = any(kw in query_lower for kw in cls.SENTIMENT_POSITIVE)
        negative_match = any(kw in query_lower for kw in cls.SENTIMENT_NEGATIVE)
        
        if positive_match and not negative_match:
            sentiment_filter = "positive"
        elif negative_match and not positive_match:
            sentiment_filter = "negative"
        elif positive_match and negative_match:
            # Look for negation patterns
            if "not happy" in query_lower or "not satisfied" in query_lower:
                sentiment_filter = "negative"
            elif "not unhappy" in query_lower or "not dissatisfied" in query_lower:
                sentiment_filter = "positive"
            else:
                # Default to negative if unclear
                sentiment_filter = "negative"
        
        # Extract potential topic (simplified - look for preposition phrases)
        topic = None
        topic_match = re.search(r'(?:about|regarding|concerning|related to|on)\s+(\w+)', query_lower)
        if topic_match:
            topic = topic_match.group(1)
        
        # Extract time filter
        time_filter = None
        for time_kw in cls.TIME_KEYWORDS:
            if time_kw in query_lower:
                time_filter = time_kw
                break
        
        # Clean the query for database search
        # Remove sentiment/topic keywords that shouldn't be in search
        search_query = query
        for kw in cls.SENTIMENT_POSITIVE + cls.SENTIMENT_NEGATIVE + (cls.TIME_KEYWORDS if time_filter else []):
            search_query = search_query.replace(kw, "")
        
        search_query = re.sub(r'\s+', ' ', search_query).strip()
        
        return {
            "original_query": query,
            "search_query": search_query,
            "sentiment_filter": sentiment_filter,
            "topic": topic,
            "time_filter": time_filter,
            "requires_semantic": False  # Can be upgraded based on query complexity
        }
    
    @classmethod
    def extract_entities(cls, query: str) -> List[str]:
        """
        Extract named entities from query.
        
        Args:
            query: Search query
            
        Returns:
            List of extracted entity strings
        """
        # Simplified entity extraction - looks for capitalized words or specific patterns
        entities = []
        
        # Look for quoted phrases
        quoted = re.findall(r'"([^"]+)"', query)
        entities.extend(quoted)
        
        # Look for common entity patterns
        patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'  # Capitalized phrases
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            entities.extend(matches)
        
        return list(set(entities))
    
    @classmethod
    def semantic_search(cls, query: str, documents: List[Dict[str, Any]], 
                       similarity_threshold: float = 0.7, 
                       max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Perform semantic search using Ollama embeddings.
        
        Args:
            query: Search query
            documents: List of response documents with 'id' and 'text' fields
            similarity_threshold: Minimum similarity score (0-1)
            max_results: Maximum results to return
            
        Returns:
            List of documents with similarity scores
        """
        # Generate query embedding
        try:
            query_embedding = OllamaService.generate_embedding(query)
        except (ConnectionError, TimeoutError):
            # Fallback to keyword search if Ollama unavailable
            current_app.logger.warning("Ollama unavailable, falling back to keyword search")
            return cls._keyword_search(query, documents, max_results)
        
        scored_results = []
        
        for doc in documents:
            doc_text = doc.get('text', '') or doc.get('data', {})
            doc_text = str(doc_text)
            
            try:
                doc_embedding = OllamaService.generate_embedding(doc_text)
                similarity = cls._cosine_similarity(query_embedding, doc_embedding)
                
                if similarity >= similarity_threshold:
                    scored_results.append({
                        **doc,
                        "similarity_score": round(similarity, 4),
                        "highlighted_text": cls._highlight_matches(doc_text, query)
                    })
            except Exception as e:
                current_app.logger.warning(f"Embedding generation failed for doc {doc.get('id')}: {e}")
                continue
        
        # Sort by similarity and limit results
        scored_results.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        
        return scored_results[:max_results]
    
    @classmethod
    def _keyword_search(cls, query: str, documents: List[Dict[str, Any]],
                       max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fallback keyword-based search when semantic search unavailable.
        
        Args:
            query: Search query
            documents: List of response documents
            max_results: Maximum results to return
            
        Returns:
            List of documents with relevance scores
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_results = []
        
        for doc in documents:
            doc_text = doc.get('text', '') or doc.get('data', {})
            doc_text_lower = str(doc_text).lower()
            
            # Count matching words
            matches = sum(1 for word in query_words if word in doc_text_lower)
            
            if matches > 0:
                relevance = matches / len(query_words)
                scored_results.append({
                    **doc,
                    "relevance_score": round(relevance, 4),
                    "highlighted_text": cls._highlight_matches(str(doc_text), query)
                })
        
        scored_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return scored_results[:max_results]
    
    @classmethod
    def _cosine_similarity(cls, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
        """
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 * magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    @classmethod
    def _highlight_matches(cls, text: str, query: str) -> str:
        """
        Highlight matching terms in text.
        
        Args:
            text: Original text
            query: Search query
            
        Returns:
            Text with <mark> tags around matches
        """
        if not text:
            return ""
        
        highlighted = text
        query_words = query.lower().split()
        
        for word in query_words:
            # Case-insensitive replacement with highlighting
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            highlighted = pattern.sub(f"<mark>{word}</mark>", highlighted)
        
        return highlighted
    
    @classmethod
    def generate_cache_key(cls, form_id: str, query: str, 
                           search_type: str = "nlp") -> str:
        """
        Generate cache key for search results.
        
        Args:
            form_id: Form identifier
            query: Search query
            search_type: Type of search (nlp, semantic)
            
        Returns:
            Cache key string
        """
        content = f"{form_id}:{search_type}:{query}"
        return f"search:{hashlib.md5(content.encode()).hexdigest()}"
    
    @classmethod
    def build_mongo_query(cls, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build MongoDB query from parsed NLP query.
        
        Args:
            parsed_query: Parsed query from parse_query
            
        Returns:
            MongoDB query dict
        """
        mongo_query = {}
        
        # Add text search if there's a search query
        search_query = parsed_query.get("search_query", "").strip()
        if search_query:
            mongo_query["$text"] = {"$search": search_query}
        
        # Add sentiment filter
        sentiment = parsed_query.get("sentiment_filter")
        if sentiment:
            mongo_query["ai_results.sentiment.label"] = sentiment
        
        # Add topic filter (simplified - looks in data values)
        topic = parsed_query.get("topic")
        if topic:
            mongo_query["data.values"] = {"$regex": topic, "$options": "i"}
        
        # Time filter would require timestamp field
        time_filter = parsed_query.get("time_filter")
        # Implementation depends on response timestamp availability
        
        return mongo_query
