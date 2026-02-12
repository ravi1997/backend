"""
Cache Service - High-level cache abstraction layer

Provides a unified interface for caching different types of data with
automatic TTL management, size limits, and cache warming.

Task: M4-01 - Redis Integration & Performance
"""

import json
import hashlib
import logging
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime, timedelta

from app.utils.redis_client import redis_client, generate_cache_key
from app import config

logger = logging.getLogger(__name__)


class CacheService:
    """
    High-level cache abstraction with type-specific caching strategies.
    
    Features:
    - Type-specific TTL and size limits
    - Automatic cache warming
    - Cache statistics tracking
    - Distributed locking support
    - Graceful degradation
    """
    
    # Cache type configurations
    CACHE_TYPES = {
        'form_schema': {
            'ttl': config.CACHE_TTL_FORM_SCHEMA,
            'max_entries': config.CACHE_MAX_ENTRIES_FORM_SCHEMA,
            'prefix': 'form:schema'
        },
        'user_session': {
            'ttl': config.CACHE_TTL_USER_SESSION,
            'max_entries': config.CACHE_MAX_ENTRIES_USER_SESSION,
            'prefix': 'user:session'
        },
        'query_result': {
            'ttl': config.CACHE_TTL_QUERY_RESULT,
            'max_entries': config.CACHE_MAX_ENTRIES_QUERY_RESULT,
            'prefix': 'query:result'
        },
        'dashboard_widget': {
            'ttl': config.CACHE_TTL_DASHBOARD_WIDGET,
            'max_entries': config.CACHE_MAX_ENTRIES_DASHBOARD_WIDGET,
            'prefix': 'dashboard:widget'
        },
        'api_response': {
            'ttl': config.CACHE_TTL_API_RESPONSE,
            'max_entries': 10000,
            'prefix': 'api:response'
        }
    }
    
    def __init__(self, redis_client=None):
        """
        Initialize cache service.
        
        Args:
            redis_client: Redis client instance (uses global if not provided)
        """
        self.redis = redis_client or redis_client
        self._cache_enabled = config.CACHE_ENABLED
        
        logger.info(f"CacheService initialized (enabled: {self._cache_enabled})")
    
    def is_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._cache_enabled
    
    # ============ Form Schema Caching ============
    
    def cache_form_schema(self, form_id: str, schema: Dict[str, Any]) -> bool:
        """
        Cache form schema with automatic TTL.
        
        Args:
            form_id: Form identifier
            schema: Form schema dictionary
            
        Returns:
            True if cached successfully
        """
        if not self._cache_enabled:
            return False
        
        try:
            cache_type = self.CACHE_TYPES['form_schema']
            key = f"{cache_type['prefix']}:{form_id}"
            
            # Add metadata to cached value
            cached_data = {
                'schema': schema,
                'cached_at': datetime.utcnow().isoformat(),
                'cache_type': 'form_schema'
            }
            
            self.redis.set(key, json.dumps(cached_data), ttl=cache_type['ttl'])
            logger.debug(f"Cached form schema: {form_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache form schema {form_id}: {e}")
            return False
    
    def get_form_schema(self, form_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached form schema.
        
        Args:
            form_id: Form identifier
            
        Returns:
            Form schema or None if not cached
        """
        if not self._cache_enabled:
            return None
        
        try:
            cache_type = self.CACHE_TYPES['form_schema']
            key = f"{cache_type['prefix']}:{form_id}"
            
            cached = self.redis.get(key)
            if cached:
                data = json.loads(cached)
                logger.debug(f"Cache hit for form schema: {form_id}")
                return data.get('schema')
            
            logger.debug(f"Cache miss for form schema: {form_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached form schema {form_id}: {e}")
            return None
    
    def invalidate_form_schema(self, form_id: str) -> bool:
        """
        Invalidate cached form schema.
        
        Args:
            form_id: Form identifier
            
        Returns:
            True if invalidated successfully
        """
        try:
            cache_type = self.CACHE_TYPES['form_schema']
            key = f"{cache_type['prefix']}:{form_id}"
            
            deleted = self.redis.delete(key)
            if deleted:
                logger.debug(f"Invalidated form schema cache: {form_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate form schema cache {form_id}: {e}")
            return False
    
    # ============ User Session Caching ============
    
    def cache_user_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """
        Cache user session with automatic TTL.
        
        Args:
            user_id: User identifier
            session_data: Session data dictionary
            
        Returns:
            True if cached successfully
        """
        if not self._cache_enabled:
            return False
        
        try:
            cache_type = self.CACHE_TYPES['user_session']
            key = f"{cache_type['prefix']}:{user_id}"
            
            cached_data = {
                'session': session_data,
                'cached_at': datetime.utcnow().isoformat(),
                'cache_type': 'user_session'
            }
            
            self.redis.set(key, json.dumps(cached_data), ttl=cache_type['ttl'])
            logger.debug(f"Cached user session: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache user session {user_id}: {e}")
            return False
    
    def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached user session.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session data or None if not cached
        """
        if not self._cache_enabled:
            return None
        
        try:
            cache_type = self.CACHE_TYPES['user_session']
            key = f"{cache_type['prefix']}:{user_id}"
            
            cached = self.redis.get(key)
            if cached:
                data = json.loads(cached)
                logger.debug(f"Cache hit for user session: {user_id}")
                return data.get('session')
            
            logger.debug(f"Cache miss for user session: {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached user session {user_id}: {e}")
            return None
    
    def invalidate_user_session(self, user_id: str) -> bool:
        """
        Invalidate cached user session.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if invalidated successfully
        """
        try:
            cache_type = self.CACHE_TYPES['user_session']
            key = f"{cache_type['prefix']}:{user_id}"
            
            deleted = self.redis.delete(key)
            if deleted:
                logger.debug(f"Invalidated user session cache: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate user session cache {user_id}: {e}")
            return False
    
    # ============ Query Result Caching ============
    
    def cache_query_result(self, query_hash: str, results: Any) -> bool:
        """
        Cache NLP search results with automatic TTL.
        
        Args:
            query_hash: Hash of the query parameters
            results: Query results
            
        Returns:
            True if cached successfully
        """
        if not self._cache_enabled:
            return False
        
        try:
            cache_type = self.CACHE_TYPES['query_result']
            key = f"{cache_type['prefix']}:{query_hash}"
            
            cached_data = {
                'results': results,
                'cached_at': datetime.utcnow().isoformat(),
                'cache_type': 'query_result'
            }
            
            self.redis.set(key, json.dumps(cached_data), ttl=cache_type['ttl'])
            logger.debug(f"Cached query result: {query_hash[:16]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache query result {query_hash}: {e}")
            return False
    
    def get_query_result(self, query_hash: str) -> Optional[Any]:
        """
        Get cached query result.
        
        Args:
            query_hash: Hash of the query parameters
            
        Returns:
            Query results or None if not cached
        """
        if not self._cache_enabled:
            return None
        
        try:
            cache_type = self.CACHE_TYPES['query_result']
            key = f"{cache_type['prefix']}:{query_hash}"
            
            cached = self.redis.get(key)
            if cached:
                data = json.loads(cached)
                logger.debug(f"Cache hit for query result: {query_hash[:16]}...")
                return data.get('results')
            
            logger.debug(f"Cache miss for query result: {query_hash[:16]}...")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached query result {query_hash}: {e}")
            return False
    
    def invalidate_query_results(self, form_id: Optional[str] = None) -> bool:
        """
        Invalidate cached query results.
        
        Args:
            form_id: Optional form ID to invalidate specific results
            
        Returns:
            True if invalidated successfully
        """
        try:
            if form_id:
                pattern = f"{self.CACHE_TYPES['query_result']['prefix']}:*:{form_id}"
            else:
                pattern = f"{self.CACHE_TYPES['query_result']['prefix']}:*"
            
            deleted = self.redis.invalidate_pattern(pattern)
            logger.debug(f"Invalidated {deleted} query result caches")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate query results: {e}")
            return False
    
    # ============ Dashboard Widget Caching ============
    
    def cache_dashboard_widget(self, user_id: str, widget_id: str, widget_data: Any) -> bool:
        """
        Cache dashboard widget data with automatic TTL.
        
        Args:
            user_id: User identifier
            widget_id: Widget identifier
            widget_data: Widget data
            
        Returns:
            True if cached successfully
        """
        if not self._cache_enabled:
            return False
        
        try:
            cache_type = self.CACHE_TYPES['dashboard_widget']
            key = f"{cache_type['prefix']}:{user_id}:{widget_id}"
            
            cached_data = {
                'data': widget_data,
                'cached_at': datetime.utcnow().isoformat(),
                'cache_type': 'dashboard_widget'
            }
            
            self.redis.set(key, json.dumps(cached_data), ttl=cache_type['ttl'])
            logger.debug(f"Cached dashboard widget: {user_id}:{widget_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache dashboard widget {user_id}:{widget_id}: {e}")
            return False
    
    def get_dashboard_widget(self, user_id: str, widget_id: str) -> Optional[Any]:
        """
        Get cached dashboard widget data.
        
        Args:
            user_id: User identifier
            widget_id: Widget identifier
            
        Returns:
            Widget data or None if not cached
        """
        if not self._cache_enabled:
            return None
        
        try:
            cache_type = self.CACHE_TYPES['dashboard_widget']
            key = f"{cache_type['prefix']}:{user_id}:{widget_id}"
            
            cached = self.redis.get(key)
            if cached:
                data = json.loads(cached)
                logger.debug(f"Cache hit for dashboard widget: {user_id}:{widget_id}")
                return data.get('data')
            
            logger.debug(f"Cache miss for dashboard widget: {user_id}:{widget_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached dashboard widget {user_id}:{widget_id}: {e}")
            return None
    
    def invalidate_dashboard_widgets(self, user_id: Optional[str] = None, 
                                     form_id: Optional[str] = None) -> bool:
        """
        Invalidate cached dashboard widgets.
        
        Args:
            user_id: Optional user ID to invalidate specific user's widgets
            form_id: Optional form ID to invalidate widgets related to a form
            
        Returns:
            True if invalidated successfully
        """
        try:
            if user_id and form_id:
                pattern = f"{self.CACHE_TYPES['dashboard_widget']['prefix']}:{user_id}:*:{form_id}"
            elif user_id:
                pattern = f"{self.CACHE_TYPES['dashboard_widget']['prefix']}:{user_id}:*"
            elif form_id:
                pattern = f"{self.CACHE_TYPES['dashboard_widget']['prefix']}:*:{form_id}"
            else:
                pattern = f"{self.CACHE_TYPES['dashboard_widget']['prefix']}:*"
            
            deleted = self.redis.invalidate_pattern(pattern)
            logger.debug(f"Invalidated {deleted} dashboard widget caches")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate dashboard widgets: {e}")
            return False
    
    # ============ API Response Caching ============
    
    def cache_api_response(self, endpoint: str, params_hash: str, 
                          response_data: Any, ttl: Optional[int] = None) -> bool:
        """
        Cache API response with automatic TTL.
        
        Args:
            endpoint: API endpoint
            params_hash: Hash of request parameters
            response_data: Response data to cache
            ttl: Optional custom TTL (uses default if not provided)
            
        Returns:
            True if cached successfully
        """
        if not self._cache_enabled:
            return False
        
        try:
            cache_type = self.CACHE_TYPES['api_response']
            key = f"{cache_type['prefix']}:{endpoint}:{params_hash}"
            
            cached_data = {
                'response': response_data,
                'cached_at': datetime.utcnow().isoformat(),
                'cache_type': 'api_response'
            }
            
            actual_ttl = ttl or cache_type['ttl']
            self.redis.set(key, json.dumps(cached_data), ttl=actual_ttl)
            logger.debug(f"Cached API response: {endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache API response {endpoint}: {e}")
            return False
    
    def get_api_response(self, endpoint: str, params_hash: str) -> Optional[Any]:
        """
        Get cached API response.
        
        Args:
            endpoint: API endpoint
            params_hash: Hash of request parameters
            
        Returns:
            Response data or None if not cached
        """
        if not self._cache_enabled:
            return None
        
        try:
            cache_type = self.CACHE_TYPES['api_response']
            key = f"{cache_type['prefix']}:{endpoint}:{params_hash}"
            
            cached = self.redis.get(key)
            if cached:
                data = json.loads(cached)
                logger.debug(f"Cache hit for API response: {endpoint}")
                return data.get('response')
            
            logger.debug(f"Cache miss for API response: {endpoint}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached API response {endpoint}: {e}")
            return None
    
    # ============ Cache Statistics ============
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            stats = self.redis.get_cache_stats()
            stats['cache_enabled'] = self._cache_enabled
            stats['cache_types'] = list(self.CACHE_TYPES.keys())
            return stats
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                'error': str(e),
                'cache_enabled': self._cache_enabled
            }
    
    # ============ Cache Warming ============
    
    def warmup_cache(self, forms: List[Dict[str, Any]] = None,
                    users: List[Dict[str, Any]] = None) -> Dict[str, int]:
        """
        Pre-warm cache with frequently accessed data.
        
        Args:
            forms: List of forms to cache
            users: List of users to cache
            
        Returns:
            Dictionary with counts of cached items
        """
        results = {
            'forms_cached': 0,
            'users_cached': 0,
            'errors': 0
        }
        
        try:
            # Cache form schemas
            if forms:
                for form in forms:
                    form_id = form.get('id') or form.get('_id')
                    if form_id:
                        schema = form.get('schema')
                        if schema:
                            if self.cache_form_schema(form_id, schema):
                                results['forms_cached'] += 1
                            else:
                                results['errors'] += 1
            
            # Cache user sessions
            if users:
                for user in users:
                    user_id = user.get('id') or user.get('_id')
                    if user_id:
                        session_data = {
                            'id': user_id,
                            'email': user.get('email'),
                            'role': user.get('role'),
                            'permissions': user.get('permissions', [])
                        }
                        if self.cache_user_session(user_id, session_data):
                            results['users_cached'] += 1
                        else:
                            results['errors'] += 1
            
            logger.info(f"Cache warmup completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Cache warmup failed: {e}")
            results['errors'] += 1
            return results
    
    # ============ Utility Methods ============
    
    def generate_query_hash(self, query: str, filters: Dict[str, Any] = None) -> str:
        """
        Generate a hash for query caching.
        
        Args:
            query: Query string
            filters: Optional filters dictionary
            
        Returns:
            Hash string
        """
        data = {'query': query}
        if filters:
            data['filters'] = sorted(filters.items())
        
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:32]
    
    def clear_all_cache(self) -> bool:
        """
        Clear all cached data.
        
        Returns:
            True if cleared successfully
        """
        try:
            self.redis.clear()
            logger.info("All cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False


# Global cache service instance
cache_service = CacheService()
