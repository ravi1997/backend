"""
Redis Client Wrapper

Provides a simple in-memory cache interface that can be replaced with
actual Redis when available. Used by M2 AI services for caching.

Task: T-M2-02, T-M2-03 - NLP Search & Summarization caching
Task: M2-INT-01c - Add distributed locking for concurrent access
"""

from functools import lru_cache
from typing import Any, Optional
import hashlib
import json
import time
import threading

# Simple in-memory cache storage
_memory_cache = {}

# In-memory lock storage for distributed locking simulation
_lock_storage = {}
_lock_mutex = threading.Lock()


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
        # Distributed locking configuration
        self._locks = {}  # Track active locks for this instance
        self._lock_timeout = 30  # Default lock timeout in seconds
        self._lock_retry_max_attempts = 3  # Max retry attempts for lock acquisition
        self._lock_retry_backoff = 0.1  # Initial backoff in seconds
        self._lock_retry_backoff_multiplier = 2.0  # Backoff multiplier
    
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
    
    # ============ Distributed Locking Methods ============
    
    def acquire_lock(self, key: str, timeout: Optional[int] = None) -> bool:
        """
        Acquire a distributed lock for a cache key.
        
        Args:
            key: Lock key (typically cache key with :lock suffix)
            timeout: Lock timeout in seconds (uses default if None)
            
        Returns:
            True if lock acquired successfully, False otherwise
        """
        lock_key = f"{key}:lock"
        lock_timeout = timeout or self._lock_timeout
        lock_value = f"{threading.current_thread().ident}:{time.time()}"
        
        with _lock_mutex:
            # Check if lock exists and is not expired
            if lock_key in _lock_storage:
                existing_lock = _lock_storage[lock_key]
                if existing_lock['expires'] > time.time():
                    # Lock is still held by another thread
                    return False
                else:
                    # Lock expired, remove it
                    del _lock_storage[lock_key]
            
            # Acquire the lock
            _lock_storage[lock_key] = {
                'value': lock_value,
                'expires': time.time() + lock_timeout,
                'thread_id': threading.current_thread().ident
            }
            self._locks[lock_key] = lock_value
            
            return True
    
    def release_lock(self, key: str) -> bool:
        """
        Release a distributed lock for a cache key.
        
        Args:
            key: Lock key (typically cache key with :lock suffix)
            
        Returns:
            True if lock released successfully, False otherwise
        """
        lock_key = f"{key}:lock"
        lock_value = self._locks.get(lock_key)
        
        with _lock_mutex:
            if lock_key in _lock_storage:
                # Verify we own the lock
                if _lock_storage[lock_key]['value'] == lock_value:
                    del _lock_storage[lock_key]
                    if lock_key in self._locks:
                        del self._locks[lock_key]
                    return True
                else:
                    # Lock held by another thread
                    return False
            return False
    
    def acquire_lock_with_retry(self, key: str, timeout: Optional[int] = None,
                               max_attempts: Optional[int] = None) -> bool:
        """
        Acquire a lock with retry logic and exponential backoff.
        
        Args:
            key: Lock key
            timeout: Lock timeout in seconds (uses default if None)
            max_attempts: Maximum retry attempts (uses default if None)
            
        Returns:
            True if lock acquired successfully, False otherwise
        """
        max_attempts = max_attempts or self._lock_retry_max_attempts
        backoff = self._lock_retry_backoff
        
        for attempt in range(max_attempts):
            if self.acquire_lock(key, timeout):
                return True
            
            # Wait with exponential backoff
            if attempt < max_attempts - 1:
                time.sleep(backoff)
                backoff *= self._lock_retry_backoff_multiplier
        
        return False
    
    def set_with_lock(self, key: str, value: str, ttl: int = 3600,
                     lock_timeout: Optional[int] = None) -> bool:
        """
        Set a cache value with distributed locking.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            lock_timeout: Lock timeout in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        lock_acquired = self.acquire_lock_with_retry(key, lock_timeout)
        
        if not lock_acquired:
            return False
        
        try:
            self.set(key, value, ttl)
            return True
        finally:
            self.release_lock(key)
    
    def get_with_lock(self, key: str, lock_timeout: Optional[int] = None) -> Optional[str]:
        """
        Get a cache value with distributed locking.
        
        Args:
            key: Cache key
            lock_timeout: Lock timeout in seconds (uses default if None)
            
        Returns:
            Cached value or None
        """
        lock_acquired = self.acquire_lock_with_retry(key, lock_timeout)
        
        if not lock_acquired:
            return None
        
        try:
            return self.get(key)
        finally:
            self.release_lock(key)
    
    def delete_lock(self, key: str) -> bool:
        """
        Delete a lock (not the cache key).
        
        Args:
            key: Lock key to delete
            
        Returns:
            True if lock deleted successfully, False otherwise
        """
        return self.release_lock(key)
    
    def get_lock_status(self) -> dict[str, Any]:
        """
        Get the status of all locks for health monitoring.
        
        Returns:
            Dict with lock status information including:
            - total_locks: Total number of locks
            - active_locks: Number of non-expired locks
            - expired_locks: Number of expired locks
            - locks: List of lock details
        """
        with _lock_mutex:
            current_time = time.time()
            active_locks = []
            expired_locks = []
            
            for lock_key, lock_data in _lock_storage.items():
                lock_info = {
                    'key': lock_key,
                    'thread_id': lock_data['thread_id'],
                    'expires': lock_data['expires'],
                    'expires_in': max(0, lock_data['expires'] - current_time),
                    'is_expired': lock_data['expires'] <= current_time
                }
                
                if lock_info['is_expired']:
                    expired_locks.append(lock_info)
                else:
                    active_locks.append(lock_info)
            
            return {
                'total_locks': len(_lock_storage),
                'active_locks': len(active_locks),
                'expired_locks': len(expired_locks),
                'instance_locks': len(self._locks),
                'locks': active_locks + expired_locks
            }
    
    def cleanup_expired_locks(self) -> int:
        """
        Clean up expired locks from the lock storage.
        
        Returns:
            Number of locks cleaned up
        """
        with _lock_mutex:
            current_time = time.time()
            expired_keys = [
                key for key, data in _lock_storage.items()
                if data['expires'] <= current_time
            ]
            
            for key in expired_keys:
                del _lock_storage[key]
                if key in self._locks:
                    del self._locks[key]
            
            return len(expired_keys)


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
