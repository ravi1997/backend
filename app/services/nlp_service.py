"""
NLP Search Service

Provides natural language search capabilities for form responses:
- Query parsing and intent extraction
- Sentiment-based filtering
- Topic extraction
- Semantic search using Ollama embeddings
- Advanced filtering (date range, field-specific)

Task: T-M2-02 - NLP Search Enhancement
Task: M2-EXT-02c - Add advanced filters (date range, field-specific)
"""

import re
import hashlib
from datetime import datetime, timedelta
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
            Dict with 'sentiment_filter', 'topic', 'time_filter', 'raw_query',
            'date_range', 'field_filters' keys
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
        
        # Extract date range from natural language
        date_range = cls._parse_date_range(query)
        
        # Extract field-specific filters
        field_filters = cls._extract_field_filters(query)
        
        # Clean the query for database search
        # Remove sentiment/topic/time/field keywords that shouldn't be in search
        search_query = query
        for kw in cls.SENTIMENT_POSITIVE + cls.SENTIMENT_NEGATIVE + (cls.TIME_KEYWORDS if time_filter else []):
            search_query = search_query.replace(kw, "")
        
        # Remove date range expressions from search query
        if date_range:
            for pattern in cls._get_date_patterns():
                search_query = re.sub(pattern, '', search_query, flags=re.IGNORECASE)
        
        # Remove field filter expressions from search query
        if field_filters:
            for field_filter in field_filters:
                field_expr = f"{field_filter['field']}\\s*{field_filter['operator']}\\s*{field_filter['value']}"
                search_query = re.sub(field_expr, '', search_query, flags=re.IGNORECASE)
        
        search_query = re.sub(r'\s+', ' ', search_query).strip()
        
        return {
            "original_query": query,
            "search_query": search_query,
            "sentiment_filter": sentiment_filter,
            "topic": topic,
            "time_filter": time_filter,
            "date_range": date_range,
            "field_filters": field_filters,
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
    
    @classmethod
    def get_query_suggestions(cls, form_id: str, partial_query: str,
                              max_suggestions: int = 10) -> List[Dict[str, Any]]:
        """
        Get query suggestions based on partial input.
        
        Extracts suggestions from:
        - Existing response data (most common terms)
        - Form question labels/field names
        
        Args:
            form_id: Form identifier
            partial_query: Partial query string to match against
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of suggestions with text, count, and match_score
        """
        from app.models.Form import Form, FormResponse
        
        partial_query_lower = partial_query.lower().strip()
        suggestions = []
        
        # Skip if partial query is too short
        if len(partial_query_lower) < 2:
            return []
        
        # 1. Extract terms from existing responses
        response_terms = defaultdict(int)
        response_recency = {}  # Track most recent submission for each term
        
        try:
            # Fetch recent responses (limit to 500 for performance)
            responses = FormResponse.objects(form_id=form_id).limit(500)
            
            for resp in responses:
                resp_data_str = str(resp.data).lower()
                # Extract words from response data
                words = re.findall(r'\b[a-z]{3,}\b', resp_data_str)
                
                # Filter out common stop words
                stop_words = {
                    "the", "and", "for", "are", "but", "not", "you", "all", "can", "her",
                    "was", "one", "our", "out", "has", "have", "had", "this", "that",
                    "with", "they", "from", "what", "when", "where", "which", "will",
                    "there", "their", "about", "would", "could", "should", "into",
                    "than", "then", "them", "these", "those", "been", "being", "have"
                }
                
                for word in words:
                    if word not in stop_words:
                        response_terms[word] += 1
                        # Track recency (higher timestamp = more recent)
                        if resp.submitted_at:
                            current_recency = response_recency.get(word, 0)
                            if resp.submitted_at > current_recency:
                                response_recency[word] = resp.submitted_at
        except Exception as e:
            current_app.logger.warning(f"Error fetching response terms: {e}")
        
        # 2. Extract terms from form structure (question labels, field names)
        form_terms = set()
        try:
            form = Form.objects.get(id=form_id)
            
            # Extract from question labels
            if hasattr(form, 'sections'):
                for section in form.sections:
                    if 'questions' in section:
                        for question in section.questions:
                            # Add label words
                            label = question.get('label', '').lower()
                            label_words = re.findall(r'\b[a-z]{3,}\b', label)
                            form_terms.update(label_words)
                            
                            # Add field name if exists
                            field_name = question.get('field_name', '').lower()
                            if field_name:
                                form_terms.update([field_name])
                            
                            # Add option labels for select/radio fields
                            if 'options' in question:
                                for option in question.options:
                                    option_label = option.get('option_label', '').lower()
                                    option_words = re.findall(r'\b[a-z]{3,}\b', option_label)
                                    form_terms.update(option_words)
        except Exception as e:
            current_app.logger.warning(f"Error fetching form terms: {e}")
        
        # 3. Combine and score suggestions
        combined_terms = {}
        
        # Add response terms with frequency and recency weighting
        for term, count in response_terms.items():
            recency_score = 0
            if term in response_recency:
                # Normalize recency (more recent = higher score)
                # Use a simple approach: recent submissions get boost
                recency_score = 1.0
            combined_terms[term] = {
                'count': count,
                'recency_score': recency_score,
                'is_form_term': False
            }
        
        # Add form terms with high base score
        for term in form_terms:
            if term in combined_terms:
                combined_terms[term]['is_form_term'] = True
            else:
                combined_terms[term] = {
                    'count': 1,
                    'recency_score': 0.5,
                    'is_form_term': True
                }
        
        # 4. Filter and rank by fuzzy matching
        for term, data in combined_terms.items():
            match_score = cls._fuzzy_match_score(partial_query_lower, term)
            
            if match_score > 0.3:  # Minimum similarity threshold
                # Calculate final score combining match, frequency, recency, and form term bonus
                final_score = (
                    match_score * 0.5 +  # Fuzzy match weight
                    min(data['count'] / 50, 1.0) * 0.3 +  # Frequency weight (capped)
                    data['recency_score'] * 0.1 +  # Recency weight
                    (1.0 if data['is_form_term'] else 0.0) * 0.1  # Form term bonus
                )
                
                suggestions.append({
                    'text': term,
                    'count': data['count'],
                    'match_score': round(final_score, 4),
                    'is_form_term': data['is_form_term']
                })
        
        # Sort by match score and limit
        suggestions.sort(key=lambda x: x['match_score'], reverse=True)
        
        return suggestions[:max_suggestions]
    
    @classmethod
    def _fuzzy_match_score(cls, query: str, candidate: str) -> float:
        """
        Calculate fuzzy match score between query and candidate.
        
        Uses a combination of:
        - Prefix matching (starts with query)
        - Contains matching (query appears anywhere)
        - Levenshtein-like character similarity
        
        Args:
            query: Partial query string
            candidate: Candidate term to match against
            
        Returns:
            Match score between 0.0 and 1.0
        """
        if not query or not candidate:
            return 0.0
        
        query_lower = query.lower()
        candidate_lower = candidate.lower()
        
        # Exact match
        if query_lower == candidate_lower:
            return 1.0
        
        # Prefix match (high weight)
        if candidate_lower.startswith(query_lower):
            prefix_ratio = len(query_lower) / len(candidate_lower)
            return 0.8 + (prefix_ratio * 0.2)
        
        # Contains match (medium weight)
        if query_lower in candidate_lower:
            contains_ratio = len(query_lower) / len(candidate_lower)
            return 0.6 + (contains_ratio * 0.2)
        
        # Calculate character overlap similarity
        # Simple approach: count common characters in sequence
        common_chars = 0
    
    @classmethod
    def save_search(cls, user_id: str, form_id: str, query: str, 
                   results_count: int = 0, parsed_intent: Dict[str, Any] = None,
                   search_type: str = 'nlp', cached: bool = False) -> str:
        """
        Save search query to database for analytics and personalization.
        
        Args:
            user_id: User identifier
            form_id: Form identifier (UUID)
            query: Search query text
            results_count: Number of results returned
            parsed_intent: Parsed query details (optional)
            search_type: Type of search ('nlp', 'semantic', 'keyword')
            cached: Whether result was from cache
            
        Returns:
            Search history record ID as string
        """
        from app.models.Form import SearchHistory
        from uuid import UUID
        
        # Convert form_id to UUID if it's a string
        if isinstance(form_id, str):
            try:
                form_id = UUID(form_id)
            except ValueError:
                current_app.logger.warning(f"Invalid form_id format: {form_id}")
                return ""
        
        # Create search history record
        search_record = SearchHistory(
            user_id=user_id,
            form_id=form_id,
            query=query,
            results_count=results_count,
            parsed_intent=parsed_intent or {},
            search_type=search_type,
            cached=cached
        )
        
        try:
            search_record.save()
            return str(search_record.id)
        except Exception as e:
            current_app.logger.error(f"Failed to save search history: {e}")
            return ""
    
    @classmethod
    def get_user_search_history(cls, user_id: str, form_id: str = None,
                                limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieve recent searches for a user.
        
        Args:
            user_id: User identifier
            form_id: Optional form identifier to filter by
            limit: Maximum number of results (default: 50)
            offset: Number of results to skip (default: 0)
            
        Returns:
            List of search history records with timestamps
        """
        from app.models.Form import SearchHistory
        from uuid import UUID
        
        # Build query
        query = SearchHistory.objects(user_id=user_id)
        
        if form_id:
            if isinstance(form_id, str):
                try:
                    form_id = UUID(form_id)
                except ValueError:
                    current_app.logger.warning(f"Invalid form_id format: {form_id}")
                    return []
            query = query.filter(form_id=form_id)
        
        # Order by timestamp descending (most recent first)
        query = query.order_by('-timestamp')
        
        # Apply pagination
        results = query.skip(offset).limit(limit)
        
        # Convert to list of dicts
        history = []
        for record in results:
            history.append({
                "id": str(record.id),
                "query": record.query,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                "results_count": record.results_count,
                "form_id": str(record.form_id),
                "search_type": record.search_type,
                "cached": record.cached,
                "parsed_intent": record.parsed_intent or {}
            })
        
        return history
    
    @classmethod
    def clear_user_search_history(cls, user_id: str, form_id: str = None) -> int:
        """
        Clear search history for a user.
        
        Args:
            user_id: User identifier
            form_id: Optional form identifier to filter by (if None, clears all)
            
        Returns:
            Number of records deleted
        """
        from app.models.Form import SearchHistory
        from uuid import UUID
        
        # Build query
        query = SearchHistory.objects(user_id=user_id)
        
        if form_id:
            if isinstance(form_id, str):
                try:
                    form_id = UUID(form_id)
                except ValueError:
                    current_app.logger.warning(f"Invalid form_id format: {form_id}")
                    return 0
            query = query.filter(form_id=form_id)
        
        # Delete matching records
        count = query.count()
        query.delete()
        
        return count
    
    @classmethod
    def get_popular_queries(cls, form_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular search queries across all users or for a specific form.
        
        Args:
            form_id: Optional form identifier to filter by
            limit: Maximum number of results (default: 10)
            
        Returns:
            List of popular queries with search counts
        """
        from app.models.Form import SearchHistory
        from uuid import UUID
        from collections import Counter
        
        # Build query
        query = SearchHistory.objects()
        
        if form_id:
            if isinstance(form_id, str):
                try:
                    form_id = UUID(form_id)
                except ValueError:
                    current_app.logger.warning(f"Invalid form_id format: {form_id}")
                    return []
            query = query.filter(form_id=form_id)
        
        # Aggregate queries by count
        query_counter = Counter()
        
        for record in query:
            query_counter[record.query] += 1
        
        # Get top queries
        popular_queries = []
        for query_text, count in query_counter.most_common(limit):
            popular_queries.append({
                "query": query_text,
                "count": count
            })
        
        return popular_queries
    
    @classmethod
    def get_popular_queries_cached(cls, form_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular search queries with caching (1 hour TTL).
        
        Args:
            form_id: Optional form identifier to filter by
            limit: Maximum number of results (default: 10)
            
        Returns:
            List of popular queries with search counts
        """
        from app.utils.redis_client import redis_client
        import json
        
        # Generate cache key
        cache_key = f"popular_queries:{form_id or 'all'}:{limit}"
        
        # Try to get from cache with locking
        cached = redis_client.get_with_lock(cache_key)
        if cached:
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                pass
        
        # Get fresh data
        popular_queries = cls.get_popular_queries(form_id, limit)
        
        # Cache for 1 hour with locking
        redis_client.set_with_lock(cache_key, json.dumps(popular_queries), ttl=3600)
        
        return popular_queries
        i = j = 0
        
        while i < len(query_lower) and j < len(candidate_lower):
            if query_lower[i] == candidate_lower[j]:
                common_chars += 1
                i += 1
                j += 1
            else:
                j += 1
        
        if common_chars > 0:
            # Ratio of common chars to query length
            char_ratio = common_chars / len(query_lower)
            # Penalize based on length difference
            length_penalty = abs(len(query_lower) - len(candidate_lower)) / max(len(query_lower), len(candidate_lower))
            return max(0.0, char_ratio * 0.5 - length_penalty * 0.2)
        
        return 0.0
    
    # --- Date Range Parsing Methods ---
    # Task: M2-EXT-02c - Add advanced filters (date range, field-specific)
    
    @classmethod
    def _get_date_patterns(cls) -> List[str]:
        """
        Get regex patterns for matching date expressions in queries.
        
        Returns:
            List of regex patterns for date matching
        """
        return [
            r'last\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)',
            r'past\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)',
            r'previous\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)',
            r'today',
            r'yesterday',
            r'this\s+(week|month|year)',
            r'last\s+(week|month|year)',
            r'(\d{4}-\d{1,2})\s+to\s+(\d{4}-\d{1,2})',
            r'(\d{4}-\d{1,2}-\d{1,2})\s+to\s+(\d{4}-\d{1,2}-\d{1,2})',
            r'from\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)\s+to\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)',
            r'between\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)\s+and\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)',
            r'after\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)',
            r'before\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)',
            r'since\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)',
            r'until\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)',
        ]
    
    @classmethod
    def _parse_date_range(cls, query: str) -> Optional[Dict[str, str]]:
        """
        Parse date range from natural language query.
        
        Args:
            query: Search query string
            
        Returns:
            Dict with 'start_date' and 'end_date' in ISO format, or None
        """
        query_lower = query.lower()
        now = datetime.utcnow()
        
        # Pattern: "last N days/weeks/months/years"
        match = re.search(r'last\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)', query_lower)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            
            if unit.startswith('day'):
                start_date = now - timedelta(days=num)
            elif unit.startswith('week'):
                start_date = now - timedelta(weeks=num)
            elif unit.startswith('month'):
                start_date = now - timedelta(days=num * 30)
            elif unit.startswith('year'):
                start_date = now - timedelta(days=num * 365)
            else:
                start_date = now - timedelta(days=num)
            
            return {
                "start_date": start_date.isoformat(),
                "end_date": now.isoformat(),
                "expression": match.group(0)
            }
        
        # Pattern: "past N days/weeks/months/years"
        match = re.search(r'past\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)', query_lower)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            
            if unit.startswith('day'):
                start_date = now - timedelta(days=num)
            elif unit.startswith('week'):
                start_date = now - timedelta(weeks=num)
            elif unit.startswith('month'):
                start_date = now - timedelta(days=num * 30)
            elif unit.startswith('year'):
                start_date = now - timedelta(days=num * 365)
            else:
                start_date = now - timedelta(days=num)
            
            return {
                "start_date": start_date.isoformat(),
                "end_date": now.isoformat(),
                "expression": match.group(0)
            }
        
        # Pattern: "today"
        if 'today' in query_lower:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "expression": "today"
            }
        
        # Pattern: "yesterday"
        if 'yesterday' in query_lower:
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "expression": "yesterday"
            }
        
        # Pattern: "this week/month/year"
        if 'this week' in query_lower:
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(weeks=1)
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "expression": "this week"
            }
        
        if 'this month' in query_lower:
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end_date = start_date.replace(year=now.year + 1, month=1)
            else:
                end_date = start_date.replace(month=now.month + 1)
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "expression": "this month"
            }
        
        if 'this year' in query_lower:
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=now.year + 1)
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "expression": "this year"
            }
        
        # Pattern: "last week/month/year"
        if 'last week' in query_lower:
            last_week_start = now - timedelta(days=now.weekday() + 7)
            start_date = last_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(weeks=1)
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "expression": "last week"
            }
        
        if 'last month' in query_lower:
            if now.month == 1:
                start_date = now.replace(year=now.year - 1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = now.replace(month=now.month - 1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "expression": "last month"
            }
        
        if 'last year' in query_lower:
            start_date = now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "expression": "last year"
            }
        
        # Pattern: "YYYY-MM to YYYY-MM" or "YYYY-MM-DD to YYYY-MM-DD"
        match = re.search(r'(\d{4}-\d{1,2}(?:-\d{1,2})?)\s+to\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)', query_lower)
        if match:
            start_date_str = match.group(1)
            end_date_str = match.group(2)
            
            # Validate and parse dates
            try:
                start_date = cls._parse_date_string(start_date_str)
                end_date = cls._parse_date_string(end_date_str)
                
                if start_date and end_date:
                    return {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "expression": match.group(0)
                    }
            except Exception:
                pass
        
        # Pattern: "from YYYY-MM to YYYY-MM" or "between YYYY-MM and YYYY-MM"
        match = re.search(r'(?:from|between)\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)\s+(?:to|and)\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)', query_lower)
        if match:
            start_date_str = match.group(1)
            end_date_str = match.group(2)
            
            # Validate and parse dates
            try:
                start_date = cls._parse_date_string(start_date_str)
                end_date = cls._parse_date_string(end_date_str)
                
                if start_date and end_date:
                    return {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "expression": match.group(0)
                    }
            except Exception:
                pass
        
        # Pattern: "after/before/since/until YYYY-MM-DD"
        match = re.search(r'(after|before|since|until)\s+(\d{4}-\d{1,2}(?:-\d{1,2})?)', query_lower)
        if match:
            direction = match.group(1)
            date_str = match.group(2)
            
            try:
                date = cls._parse_date_string(date_str)
                if date:
                    if direction == 'after' or direction == 'since':
                        return {
                            "start_date": date.isoformat(),
                            "end_date": None,
                            "expression": match.group(0)
                        }
                    else:  # before or until
                        return {
                            "start_date": None,
                            "end_date": date.isoformat(),
                            "expression": match.group(0)
                        }
            except Exception:
                pass
        
        return None
    
    @classmethod
    def _parse_date_string(cls, date_str: str) -> Optional[datetime]:
        """
        Parse date string in various formats.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime object or None
        """
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m',
            '%Y/%m/%d',
            '%Y/%m',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    # --- Field Filter Extraction Methods ---
    # Task: M2-EXT-02c - Add advanced filters (date range, field-specific)
    
    @classmethod
    def _extract_field_filters(cls, query: str) -> List[Dict[str, Any]]:
        """
        Extract field-specific filters from query.
        
        Supports patterns like:
        - "q_satisfaction: positive"
        - "q_rating > 3"
        - "q_rating >= 3"
        - "q_rating < 5"
        - "q_rating <= 5"
        - "q_name contains John"
        - "q_status = approved"
        
        Args:
            query: Search query string
            
        Returns:
            List of field filter dicts with 'field', 'operator', 'value' keys
        """
        filters = []
        
        # Pattern 1: field: value (contains/equals)
        pattern1 = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([^\s]+(?:\s+[^\s]+)*)'
        for match in re.finditer(pattern1, query):
            field = match.group(1)
            value = match.group(2).strip()
            filters.append({
                "field": field,
                "operator": "contains",
                "value": value
            })
        
        # Pattern 2: field > value
        pattern2 = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*>\s*([^\s]+)'
        for match in re.finditer(pattern2, query):
            field = match.group(1)
            value = match.group(2)
            filters.append({
                "field": field,
                "operator": ">",
                "value": value
            })
        
        # Pattern 3: field >= value
        pattern3 = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*>=\s*([^\s]+)'
        for match in re.finditer(pattern3, query):
            field = match.group(1)
            value = match.group(2)
            filters.append({
                "field": field,
                "operator": ">=",
                "value": value
            })
        
        # Pattern 4: field < value
        pattern4 = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*<\s*([^\s]+)'
        for match in re.finditer(pattern4, query):
            field = match.group(1)
            value = match.group(2)
            filters.append({
                "field": field,
                "operator": "<",
                "value": value
            })
        
        # Pattern 5: field <= value
        pattern5 = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*<=\s*([^\s]+)'
        for match in re.finditer(pattern5, query):
            field = match.group(1)
            value = match.group(2)
            filters.append({
                "field": field,
                "operator": "<=",
                "value": value
            })
        
        # Pattern 6: field = value
        pattern6 = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^\s]+)'
        for match in re.finditer(pattern6, query):
            field = match.group(1)
            value = match.group(2)
            filters.append({
                "field": field,
                "operator": "=",
                "value": value
            })
        
        # Pattern 7: field contains value
        pattern7 = r'([a-zA-Z_][a-zA-Z0-9_]*)\s+contains\s+([^\s]+(?:\s+[^\s]+)*)'
        for match in re.finditer(pattern7, query):
            field = match.group(1)
            value = match.group(2).strip()
            filters.append({
                "field": field,
                "operator": "contains",
                "value": value
            })
        
        return filters
    
    # --- Main Filtering Method ---
    # Task: M2-EXT-02c - Add advanced filters (date range, field-specific)
    
    @classmethod
    def filter_by_criteria(cls, documents: List[Dict[str, Any]], 
                          filters: Dict[str, Any],
                          filter_mode: str = "and") -> List[Dict[str, Any]]:
        """
        Filter documents by date range, field criteria, and metadata.
        
        Args:
            documents: List of document dicts to filter
            filters: Dict with filter criteria:
                - date_range: {'start_date': 'ISO date', 'end_date': 'ISO date'}
                - field_filters: [{'field': 'name', 'operator': '>', 'value': '5'}]
                - submitted_by: List of user IDs
                - source: List of sources
            filter_mode: "and" (all filters must match) or "or" (any filter can match)
            
        Returns:
            Filtered list of documents
        """
        if not filters:
            return documents
        
        filtered_docs = []
        
        for doc in documents:
            matches = []
            
            # Date range filter
            date_range = filters.get('date_range')
            if date_range:
                matches.append(cls._matches_date_range(doc, date_range))
            
            # Field filters
            field_filters = filters.get('field_filters', [])
            if field_filters:
                field_matches = []
                for field_filter in field_filters:
                    field_matches.append(cls._matches_field_filter(doc, field_filter))
                # For field filters, all must match within the group
                if field_matches:
                    matches.append(all(field_matches))
            
            # Submitted by filter
            submitted_by = filters.get('submitted_by')
            if submitted_by:
                doc_submitted_by = doc.get('submitted_by')
                matches.append(doc_submitted_by in submitted_by)
            
            # Source filter
            source = filters.get('source')
            if source:
                doc_source = doc.get('metadata', {}).get('source')
                matches.append(doc_source in source)
            
            # Apply filter mode
            if not matches:
                # No filters applied, include document
                filtered_docs.append(doc)
            elif filter_mode == "and":
                if all(matches):
                    filtered_docs.append(doc)
            else:  # filter_mode == "or"
                if any(matches):
                    filtered_docs.append(doc)
        
        return filtered_docs
    
    @classmethod
    def _matches_date_range(cls, doc: Dict[str, Any], date_range: Dict[str, str]) -> bool:
        """
        Check if document matches date range criteria.
        
        Args:
            doc: Document dict
            date_range: Dict with 'start_date' and/or 'end_date' in ISO format
            
        Returns:
            True if document matches date range
        """
        doc_date_str = doc.get('submitted_at')
        if not doc_date_str:
            return False
        
        try:
            doc_date = datetime.fromisoformat(doc_date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return False
        
        start_date_str = date_range.get('start_date')
        end_date_str = date_range.get('end_date')
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                if doc_date < start_date:
                    return False
            except ValueError:
                pass
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                if doc_date > end_date:
                    return False
            except ValueError:
                pass
        
        return True
    
    @classmethod
    def _matches_field_filter(cls, doc: Dict[str, Any], field_filter: Dict[str, Any]) -> bool:
        """
        Check if document matches a field filter.
        
        Args:
            doc: Document dict
            field_filter: Dict with 'field', 'operator', 'value' keys
            
        Returns:
            True if document matches field filter
        """
        field_name = field_filter.get('field')
        operator = field_filter.get('operator')
        filter_value = field_filter.get('value')
        
        # Get field value from document
        # Try data.values first (form response data), then data directly
        doc_data = doc.get('data', {})
        if isinstance(doc_data, dict):
            doc_value = doc_data.get('values', {}).get(field_name)
            if doc_value is None:
                doc_value = doc_data.get(field_name)
        else:
            doc_value = None
        
        if doc_value is None:
            return False
        
        # Try to convert filter value to appropriate type
        try:
            # Try numeric comparison
            if operator in ['>', '>=', '<', '<=']:
                filter_num = float(filter_value)
                doc_num = float(doc_value)
                
                if operator == '>':
                    return doc_num > filter_num
                elif operator == '>=':
                    return doc_num >= filter_num
                elif operator == '<':
                    return doc_num < filter_num
                elif operator == '<=':
                    return doc_num <= filter_num
            elif operator == '=':
                filter_num = float(filter_value)
                doc_num = float(doc_value)
                return doc_num == filter_num
        except (ValueError, TypeError):
            # Fall back to string comparison
            pass
        
        # String comparison
        doc_str = str(doc_value).lower()
        filter_str = str(filter_value).lower()
        
        if operator == '=':
            return doc_str == filter_str
        elif operator == 'contains':
            return filter_str in doc_str
        else:
            # For numeric operators with non-numeric values, try to compare as strings
            if operator == '>':
                return doc_str > filter_str
            elif operator == '>=':
                return doc_str >= filter_str
            elif operator == '<':
                return doc_str < filter_str
            elif operator == '<=':
                return doc_str <= filter_str
        
        return False
    
    # --- Validation Methods ---
    # Task: M2-EXT-02c - Add advanced filters (date range, field-specific)
    
    @classmethod
    def validate_date_range(cls, date_range: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """
        Validate date range filter.
        
        Args:
            date_range: Dict with 'start_date' and/or 'end_date' in ISO format
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not date_range:
            return True, None
        
        start_date_str = date_range.get('start_date')
        end_date_str = date_range.get('end_date')
        
        if not start_date_str and not end_date_str:
            return False, "Date range must have at least start_date or end_date"
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                return False, f"Invalid start_date format: {start_date_str}"
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except ValueError:
                return False, f"Invalid end_date format: {end_date_str}"
        
        if start_date_str and end_date_str:
            if start_date > end_date:
                return False, "start_date must be before end_date"
        
        return True, None
    
    @classmethod
    def validate_field_names(cls, field_filters: List[Dict[str, Any]], 
                           form_schema: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str]]:
        """
        Validate field names exist in form schema.
        
        Args:
            field_filters: List of field filter dicts
            form_schema: Optional form schema dict with field definitions
            
        Returns:
            Tuple of (is_valid, list_of_invalid_fields)
        """
        if not field_filters:
            return True, []
        
        if not form_schema:
            # If no schema provided, skip validation
            return True, []
        
        # Extract valid field names from schema
        valid_fields = set()
        if 'sections' in form_schema:
            for section in form_schema['sections']:
                if 'questions' in section:
                    for question in section['questions']:
                        field_name = question.get('field_name')
                        if field_name:
                            valid_fields.add(field_name)
        
        # Check field filters
        invalid_fields = []
        for field_filter in field_filters:
            field_name = field_filter.get('field')
            if field_name and field_name not in valid_fields:
                invalid_fields.append(field_name)
        
        return len(invalid_fields) == 0, invalid_fields
    
    # --- Cache Invalidation Methods ---
    # Task: M2-INT-01b - Add cache invalidation rules
    
    @classmethod
    def invalidate_cache(cls, form_id: str = None, user_id: str = None,
                       pattern: str = "all", query: str = None) -> int:
        """
        Invalidate cache keys for NLP search results.
        
        Supports pattern-based invalidation:
        - all: Invalidate all NLP search cache
        - by_query: Invalidate cache for specific query
        - by_form: Invalidate all cache for specific form
        - by_user: Invalidate all cache for specific user
        
        Args:
            form_id: Form identifier (optional)
            user_id: User identifier (optional)
            pattern: Invalidation pattern (all, by_query, by_form, by_user)
            query: Specific query string (required for by_query pattern)
            
        Returns:
            Number of cache keys invalidated
        """
        from app.utils.redis_client import redis_client
        import re
        
        keys_invalidated = 0
        
        # Pattern: Invalidate all NLP search cache
        if pattern == "all":
            # Clear all search:* keys from memory cache
            keys_to_delete = [
                k for k in redis_client._memory_cache.keys()
                if k.startswith('search:')
            ]
            for key in keys_to_delete:
                redis_client.delete(key)
                keys_invalidated += 1
            
            # Also clear popular queries cache
            popular_keys = [
                k for k in redis_client._memory_cache.keys()
                if k.startswith('popular_queries:')
            ]
            for key in popular_keys:
                redis_client.delete(key)
                keys_invalidated += 1
            
            current_app.logger.info(f"Invalidated all NLP search cache: {keys_invalidated} keys")
            return keys_invalidated
        
        # Pattern: Invalidate cache for specific query
        elif pattern == "by_query":
            if not query:
                current_app.logger.warning("by_query pattern requires query parameter")
                return 0
            
            # Generate cache key for the query
            cache_key = cls.generate_cache_key(form_id or "unknown", query, "nlp")
            if redis_client.delete(cache_key):
                keys_invalidated += 1
            
            # Also invalidate semantic search cache for the same query
            semantic_key = cls.generate_cache_key(form_id or "unknown", query, "semantic")
            if redis_client.delete(semantic_key):
                keys_invalidated += 1
            
            current_app.logger.info(f"Invalidated cache for query '{query}': {keys_invalidated} keys")
            return keys_invalidated
        
        # Pattern: Invalidate all cache for specific form
        elif pattern == "by_form":
            if not form_id:
                current_app.logger.warning("by_form pattern requires form_id parameter")
                return 0
            
            # Clear all search keys for this form
            keys_to_delete = []
            for key in redis_client._memory_cache.keys():
                if key.startswith('search:'):
                    # The key format is search:{hash}, so we need to check if it matches
                    # We can't easily check without storing metadata, so we'll clear all
                    # and let them be regenerated
                    keys_to_delete.append(key)
            
            # Clear popular queries for this form
            popular_key = f"popular_queries:{form_id}:*"
            keys_to_delete.extend([
                k for k in redis_client._memory_cache.keys()
                if k.startswith(f'popular_queries:{form_id}')
            ])
            
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
            
            # Clear search history cache for this user
            # Note: Search history is stored in MongoDB, not Redis
            # This clears any user-specific query suggestions cache
            keys_to_delete = [
                k for k in redis_client._memory_cache.keys()
                if 'suggestions' in k
            ]
            
            for key in keys_to_delete:
                redis_client.delete(key)
                keys_invalidated += 1
            
            current_app.logger.info(f"Invalidated cache for user {user_id}: {keys_invalidated} keys")
            return keys_invalidated
        
        else:
            current_app.logger.warning(f"Unknown invalidation pattern: {pattern}")
            return 0
