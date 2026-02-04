"""
Redis Client Wrapper

Provides a simple in-memory cache interface that can be replaced with
actual Redis when available. Used by M2 AI services for caching.

Task: T-M2-02, T-M2-03 - NLP Search & Summarization caching
"""

from functools import lru_cache
from typing import Any, Optional
import hashlib
import json
import time

# Simple in-memory cache storage
_memory_cache = {}


class RedisClient:
    """
    In-memory Redis-compatible client.
    
    Replace with actual Redis client when Redis is available:
    - Install: pip install redis
    - Uncomment Redis implementation below
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self._connected = False
    
    def connect(self) -> bool:
        """Try to connect to Redis (placeholder)."""
        # For production with Redis, uncomment below:
        # try:
        #     import redis
        #     self._client = redis.Redis(host=self.host, port=self.port, db=self.db)
        #     self._client.ping()
        #     self._connected = True
        #     return True
        # except (ImportError, ConnectionError):
        #     pass
        self._connected = False
        return False
    
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if key in _memory_cache:
            data = _memory_cache[key]
            # Check if expired
            if data.get('expires', float('inf')) > time.time():
                return data.get('value')
            else:
                # Clean up expired entry
                del _memory_cache[key]
        return None
    
    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        _memory_cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in _memory_cache:
            del _memory_cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cached values."""
        _memory_cache.clear()
        return True
    
    def get_many(self, keys: list) -> dict:
        """Get multiple values."""
        result = {}
        for key in keys:
            val = self.get(key)
            if val is not None:
                result[key] = val
        return result
    
    def set_many(self, mapping: dict, ttl: int = 3600) -> bool:
        """Set multiple values."""
        for key, value in mapping.items():
            self.set(key, value, ttl)
        return True
    
    def ping(self) -> bool:
        """Check Redis connection."""
        return self._connected


# Global client instance
redis_client = RedisClient()


def generate_cache_key(prefix: str, **kwargs) -> str:
    """
    Generate a unique cache key from arguments.
    
    Args:
        prefix: Key prefix
        **kwargs: Arguments to include in key
        
    Returns:
        Cache key string
    """
    # Sort kwargs for consistent key generation
    sorted_items = sorted(kwargs.items())
    key_parts = [prefix] + [f"{k}={v}" for k, v in sorted_items]
    key_string = ":".join(key_parts)
    
    # Hash the key if it's too long
    if len(key_string) > 200:
        hash_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:hash:{hash_key}"
    
    return key_string


def cache_result(ttl: int = 3600):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Cache TTL in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = generate_cache_key(
                func.__name__,
                args=str(args),
                kwargs=str(sorted(kwargs.items()))
            )
            
            # Try to get cached result
            cached = redis_client.get(cache_key)
            if cached is not None:
                return json.loads(cached)
            
            # Call function and cache result
            result = func(*args, **kwargs)
            redis_client.set(cache_key, json.dumps(result), ttl=ttl)
            return result
        return wrapper
    return decorator


# Connection helper
def connect_redis(host: str = "localhost", port: int = 6379) -> bool:
    """
    Connect to Redis server.
    
    Args:
        host: Redis host
        port: Redis port
        
    Returns:
        True if connected successfully
    """
    global redis_client
    redis_client = RedisClient(host=host, port=port)
    return redis_client.connect()
