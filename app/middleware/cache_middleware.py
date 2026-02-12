"""
Cache Middleware - Decorator for automatic API response caching

Provides decorators for caching API responses with support for:
- Cache bypass headers (Cache-Control)
- ETag support for conditional requests
- Custom cache key generation
- Per-endpoint TTL configuration

Task: M4-01 - Redis Integration & Performance
"""

import json
import hashlib
import logging
from functools import wraps
from typing import Callable, Optional, Any, Dict
from flask import request, Response, make_response

from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


def cache_bypass_check() -> bool:
    """
    Check if cache should be bypassed based on request headers.
    
    Returns:
        True if cache should be bypassed
    """
    cache_control = request.headers.get('Cache-Control', '').lower()
    
    # Bypass cache if Cache-Control: no-cache or max-age=0
    if 'no-cache' in cache_control or 'max-age=0' in cache_control:
        logger.debug("Cache bypass requested via Cache-Control header")
        return True
    
    # Bypass cache for non-GET/HEAD requests
    if request.method not in ['GET', 'HEAD']:
        return True
    
    return False


def generate_etag(data: Any) -> str:
    """
    Generate ETag for cached data.
    
    Args:
        data: Data to generate ETag for
        
    Returns:
        ETag string
    """
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    
    return hashlib.md5(data_str.encode()).hexdigest()


def cache_response(ttl: int = 60, key_func: Optional[Callable] = None,
                   include_user: bool = False, cache_bypass: bool = True):
    """
    Decorator to cache API responses.
    
    Args:
        ttl: Cache time-to-live in seconds
        key_func: Optional custom cache key function
        include_user: Include user ID in cache key
        cache_bypass: Respect cache bypass headers
        
    Usage:
        @cache_response(ttl=300)
        def get_form(form_id):
            return form_data
            
        @cache_response(ttl=120, include_user=True)
        def get_dashboard():
            return dashboard_data
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if caching is enabled
            if not cache_service.is_enabled():
                return f(*args, **kwargs)
            
            # Check cache bypass
            if cache_bypass and cache_bypass_check():
                logger.debug(f"Cache bypass for endpoint: {request.endpoint}")
                return f(*args, **kwargs)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                endpoint = request.endpoint or 'unknown'
                path = request.path
                
                # Include query parameters
                query_params = sorted(request.args.items())
                
                # Include user ID if requested
                user_id = ''
                if include_user:
                    from flask import g
                    user_id = getattr(g, 'user_id', '')
                
                # Generate hash for parameters
                params_str = json.dumps(query_params, sort_keys=True)
                params_hash = hashlib.sha256(params_str.encode()).hexdigest()[:16]
                
                cache_key = f"{endpoint}:{path}:{params_hash}:{user_id}"
            
            # Check if-none-match header for conditional request
            if_none_match = request.headers.get('If-None-Match')
            
            # Try to get cached response
            cached = cache_service.get_api_response(endpoint or request.path, cache_key)
            
            if cached:
                # Generate ETag for cached response
                etag = generate_etag(cached)
                
                # Check if ETag matches (conditional request)
                if if_none_match and if_none_match == etag:
                    response = make_response('', 304)
                    response.headers['ETag'] = etag
                    response.headers['X-Cache'] = 'HIT'
                    response.headers['Cache-Control'] = f'public, max-age={ttl}'
                    return response
                
                # Return cached response
                response = make_response(cached)
                response.headers['ETag'] = etag
                response.headers['X-Cache'] = 'HIT'
                response.headers['Cache-Control'] = f'public, max-age={ttl}'
                logger.debug(f"Cache hit for endpoint: {request.endpoint}")
                return response
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for endpoint: {request.endpoint}")
            result = f(*args, **kwargs)
            
            # Cache the result
            try:
                cache_service.cache_api_response(
                    endpoint or request.path,
                    cache_key,
                    result,
                    ttl=ttl
                )
            except Exception as e:
                logger.error(f"Failed to cache response for {request.endpoint}: {e}")
            
            # Generate ETag for new response
            etag = generate_etag(result)
            
            # Return response with cache headers
            response = make_response(result)
            response.headers['ETag'] = etag
            response.headers['X-Cache'] = 'MISS'
            response.headers['Cache-Control'] = f'public, max-age={ttl}'
            
            return response
        
        return decorated_function
    return decorator


def cache_form_schema(ttl: int = 3600):
    """
    Decorator to cache form schema responses.
    
    Args:
        ttl: Cache time-to-live in seconds (default: 1 hour)
        
    Usage:
        @cache_form_schema()
        def get_form_schema(form_id):
            return schema_data
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not cache_service.is_enabled():
                return f(*args, **kwargs)
            
            # Extract form_id from kwargs
            form_id = kwargs.get('form_id') or kwargs.get('id')
            if not form_id and args:
                form_id = args[0]
            
            if not form_id:
                return f(*args, **kwargs)
            
            # Check cache bypass
            if cache_bypass_check():
                logger.debug(f"Cache bypass for form schema: {form_id}")
                return f(*args, **kwargs)
            
            # Try to get cached schema
            cached = cache_service.get_form_schema(form_id)
            
            if cached:
                response = make_response(cached)
                response.headers['X-Cache'] = 'HIT'
                response.headers['Cache-Control'] = f'public, max-age={ttl}'
                logger.debug(f"Cache hit for form schema: {form_id}")
                return response
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for form schema: {form_id}")
            result = f(*args, **kwargs)
            
            # Cache the result
            try:
                cache_service.cache_form_schema(form_id, result)
            except Exception as e:
                logger.error(f"Failed to cache form schema {form_id}: {e}")
            
            # Return response with cache headers
            response = make_response(result)
            response.headers['X-Cache'] = 'MISS'
            response.headers['Cache-Control'] = f'public, max-age={ttl}'
            
            return response
        
        return decorated_function
    return decorator


def cache_dashboard_widget(ttl: int = 120, include_user: bool = True):
    """
    Decorator to cache dashboard widget responses.
    
    Args:
        ttl: Cache time-to-live in seconds (default: 2 minutes)
        include_user: Include user ID in cache key (default: True)
        
    Usage:
        @cache_dashboard_widget()
        def get_widget_data(widget_id):
            return widget_data
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not cache_service.is_enabled():
                return f(*args, **kwargs)
            
            # Extract widget_id from kwargs
            widget_id = kwargs.get('widget_id') or kwargs.get('id')
            if not widget_id and args:
                widget_id = args[0]
            
            if not widget_id:
                return f(*args, **kwargs)
            
            # Get user ID
            from flask import g
            user_id = getattr(g, 'user_id', '') if include_user else ''
            
            # Check cache bypass
            if cache_bypass_check():
                logger.debug(f"Cache bypass for dashboard widget: {user_id}:{widget_id}")
                return f(*args, **kwargs)
            
            # Try to get cached widget data
            cached = cache_service.get_dashboard_widget(user_id, widget_id)
            
            if cached:
                response = make_response(cached)
                response.headers['X-Cache'] = 'HIT'
                response.headers['Cache-Control'] = f'public, max-age={ttl}'
                logger.debug(f"Cache hit for dashboard widget: {user_id}:{widget_id}")
                return response
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for dashboard widget: {user_id}:{widget_id}")
            result = f(*args, **kwargs)
            
            # Cache the result
            try:
                cache_service.cache_dashboard_widget(user_id, widget_id, result)
            except Exception as e:
                logger.error(f"Failed to cache dashboard widget {user_id}:{widget_id}: {e}")
            
            # Return response with cache headers
            response = make_response(result)
            response.headers['X-Cache'] = 'MISS'
            response.headers['Cache-Control'] = f'public, max-age={ttl}'
            
            return response
        
        return decorated_function
    return decorator


def cache_query_result(ttl: int = 300):
    """
    Decorator to cache NLP query results.
    
    Args:
        ttl: Cache time-to-live in seconds (default: 5 minutes)
        
    Usage:
        @cache_query_result()
        def search_forms(query, filters=None):
            return search_results
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not cache_service.is_enabled():
                return f(*args, **kwargs)
            
            # Extract query and filters
            query = kwargs.get('query') or (args[0] if args else None)
            filters = kwargs.get('filters') or (args[1] if len(args) > 1 else None)
            
            if not query:
                return f(*args, **kwargs)
            
            # Check cache bypass
            if cache_bypass_check():
                logger.debug(f"Cache bypass for query: {query[:50]}...")
                return f(*args, **kwargs)
            
            # Generate query hash
            query_hash = cache_service.generate_query_hash(query, filters)
            
            # Try to get cached result
            cached = cache_service.get_query_result(query_hash)
            
            if cached:
                response = make_response(cached)
                response.headers['X-Cache'] = 'HIT'
                response.headers['Cache-Control'] = f'public, max-age={ttl}'
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return response
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for query: {query[:50]}...")
            result = f(*args, **kwargs)
            
            # Cache the result
            try:
                cache_service.cache_query_result(query_hash, result)
            except Exception as e:
                logger.error(f"Failed to cache query result: {e}")
            
            # Return response with cache headers
            response = make_response(result)
            response.headers['X-Cache'] = 'MISS'
            response.headers['Cache-Control'] = f'public, max-age={ttl}'
            
            return response
        
        return decorated_function
    return decorator
