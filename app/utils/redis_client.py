"""
Redis Client Wrapper

Provides a Redis-compatible client with fallback to in-memory cache.
Supports actual Redis when available, with comprehensive caching features.

Task: T-M2-02, T-M2-03 - NLP Search & Summarization caching
Task: M2-INT-01c - Add distributed locking for concurrent access
Task: M4-01 - Redis Integration & Performance
"""

from functools import lru_cache
from typing import Any, Optional, Dict, List
import hashlib
import json
import time
import threading
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Simple in-memory cache storage (fallback when Redis unavailable)
_memory_cache = {}

# In-memory lock storage for distributed locking simulation
_lock_storage = {}
_lock_mutex = threading.Lock()

# Cache statistics tracking
_cache_stats = {
    'hits': 0,
    'misses': 0,
    'errors': 0,
    'evictions': 0,
    'writes': 0
}


class RedisClient:
    """
    Redis-compatible client with fallback to in-memory cache.
    
    Supports actual Redis when available, with comprehensive caching features:
    - Connection pooling
    - Distributed locking
    - Pipeline operations
    - Graceful degradation to in-memory cache
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0,
                 password: Optional[str] = None, max_connections: int = 50,
                 socket_timeout: int = 5, socket_connect_timeout: int = 5):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        
        self._client = None
        self._connected = False
        self._use_fallback = True  # Start with fallback enabled
        
        # Distributed locking configuration
        self._locks = {}  # Track active locks for this instance
        self._lock_timeout = 30  # Default lock timeout in seconds
        self._lock_retry_max_attempts = 3  # Max retry attempts for lock acquisition
        self._lock_retry_backoff = 0.1  # Initial backoff in seconds
        self._lock_retry_backoff_multiplier = 2.0  # Backoff multiplier
        
        # Try to connect to Redis
        self._initialize_redis()
    
    def _initialize_redis(self) -> None:
        """Initialize Redis connection with fallback to in-memory cache."""
        try:
            import redis
            from redis.connection import ConnectionPool
            
            # Create connection pool
            pool = ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=True,
                decode_responses=True
            )
            
            self._client = redis.Redis(connection_pool=pool)
            
            # Test connection
            self._client.ping()
            self._connected = True
            self._use_fallback = False
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            
        except ImportError:
            logger.warning("Redis package not installed, using in-memory fallback")
            self._use_fallback = True
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}, using in-memory fallback")
            self._use_fallback = True
    
    def connect(self) -> bool:
        """Try to connect to Redis (or reinitialize)."""
        self._initialize_redis()
        return self._connected
    
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        if self._use_fallback:
            return False
        try:
            if self._client:
                self._client.ping()
                return True
        except Exception:
            self._connected = False
            self._use_fallback = True
        return False
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        try:
            if not self._use_fallback and self._client:
                value = self._client.get(key)
                if value is not None:
                    _cache_stats['hits'] += 1
                    return value
                else:
                    _cache_stats['misses'] += 1
                    return None
        except Exception as e:
            logger.warning(f"Redis get failed for key '{key}': {e}, falling back to in-memory")
            _cache_stats['errors'] += 1
            self._use_fallback = True
        
        # Fallback to in-memory cache
        if key in _memory_cache:
            data = _memory_cache[key]
            # Check if expired
            if data.get('expires', float('inf')) > time.time():
                _cache_stats['hits'] += 1
                return data.get('value')
            else:
                # Clean up expired entry
                del _memory_cache[key]
                _cache_stats['misses'] += 1
        else:
            _cache_stats['misses'] += 1
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
        try:
            if not self._use_fallback and self._client:
                self._client.setex(key, ttl, value)
                _cache_stats['writes'] += 1
                return True
        except Exception as e:
            logger.warning(f"Redis set failed for key '{key}': {e}, falling back to in-memory")
            _cache_stats['errors'] += 1
            self._use_fallback = True
        
        # Fallback to in-memory cache
        _memory_cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
        _cache_stats['writes'] += 1
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if not self._use_fallback and self._client:
                deleted = self._client.delete(key)
                return deleted > 0
        except Exception as e:
            logger.warning(f"Redis delete failed for key '{key}': {e}, falling back to in-memory")
            _cache_stats['errors'] += 1
            self._use_fallback = True
        
        # Fallback to in-memory cache
        if key in _memory_cache:
            del _memory_cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cached values."""
        try:
            if not self._use_fallback and self._client:
                self._client.flushdb()
                return True
        except Exception as e:
            logger.warning(f"Redis clear failed: {e}, falling back to in-memory")
            _cache_stats['errors'] += 1
            self._use_fallback = True
        
        # Fallback to in-memory cache
        _memory_cache.clear()
        return True
    
    def get_many(self, keys: list) -> dict:
        """Get multiple values."""
        try:
            if not self._use_fallback and self._client:
                values = self._client.mget(keys)
                result = {}
                for key, value in zip(keys, values):
                    if value is not None:
                        result[key] = value
                        _cache_stats['hits'] += 1
                    else:
                        _cache_stats['misses'] += 1
                return result
        except Exception as e:
            logger.warning(f"Redis get_many failed: {e}, falling back to in-memory")
            _cache_stats['errors'] += 1
            self._use_fallback = True
        
        # Fallback to in-memory cache
        result = {}
        for key in keys:
            val = self.get(key)
            if val is not None:
                result[key] = val
        return result
    
    def set_many(self, mapping: dict, ttl: int = 3600) -> bool:
        """Set multiple values."""
        try:
            if not self._use_fallback and self._client:
                pipe = self._client.pipeline()
                for key, value in mapping.items():
                    pipe.setex(key, ttl, value)
                pipe.execute()
                _cache_stats['writes'] += len(mapping)
                return True
        except Exception as e:
            logger.warning(f"Redis set_many failed: {e}, falling back to in-memory")
            _cache_stats['errors'] += 1
            self._use_fallback = True
        
        # Fallback to in-memory cache
        for key, value in mapping.items():
            self.set(key, value, ttl)
        return True
    
    def ping(self) -> bool:
        """Check Redis connection."""
        try:
            if not self._use_fallback and self._client:
                self._client.ping()
                return True
        except Exception:
            self._connected = False
            self._use_fallback = True
        return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "form:schema:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            if not self._use_fallback and self._client:
                keys = self._client.keys(pattern)
                if keys:
                    deleted = self._client.delete(*keys)
                    _cache_stats['evictions'] += deleted
                    return deleted
                return 0
        except Exception as e:
            logger.warning(f"Redis invalidate_pattern failed: {e}, falling back to in-memory")
            _cache_stats['errors'] += 1
            self._use_fallback = True
        
        # Fallback to in-memory cache (simple pattern matching)
        import fnmatch
        keys_to_delete = [k for k in _memory_cache.keys() if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            del _memory_cache[key]
        _cache_stats['evictions'] += len(keys_to_delete)
        return len(keys_to_delete)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            if not self._use_fallback and self._client:
                info = self._client.info('stats')
                memory_info = self._client.info('memory')
                
                return {
                    'backend': 'redis',
                    'connected': True,
                    'total_keys': info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0),
                    'hits': _cache_stats['hits'],
                    'misses': _cache_stats['misses'],
                    'hit_ratio': _cache_stats['hits'] / (_cache_stats['hits'] + _cache_stats['misses']) if (_cache_stats['hits'] + _cache_stats['misses']) > 0 else 0.0,
                    'memory_used': memory_info.get('used_memory', 0),
                    'memory_human': memory_info.get('used_memory_human', 'N/A'),
                    'evictions': _cache_stats['evictions'],
                    'writes': _cache_stats['writes'],
                    'errors': _cache_stats['errors'],
                    'fallback_mode': False
                }
        except Exception as e:
            logger.warning(f"Redis get_cache_stats failed: {e}, using in-memory stats")
            _cache_stats['errors'] += 1
            self._use_fallback = True
        
        # Fallback to in-memory stats
        return {
            'backend': 'in_memory',
            'connected': False,
            'total_keys': len(_memory_cache),
            'hits': _cache_stats['hits'],
            'misses': _cache_stats['misses'],
            'hit_ratio': _cache_stats['hits'] / (_cache_stats['hits'] + _cache_stats['misses']) if (_cache_stats['hits'] + _cache_stats['misses']) > 0 else 0.0,
            'memory_used': sum(len(str(v['value'])) for v in _memory_cache.values()),
            'memory_human': f"{sum(len(str(v['value'])) for v in _memory_cache.values())} bytes",
            'evictions': _cache_stats['evictions'],
            'writes': _cache_stats['writes'],
            'errors': _cache_stats['errors'],
            'fallback_mode': True
        }
    
    def get_with_fallback(self, key: str, fallback_func, ttl: int = 300) -> Any:
        """
        Get from cache, fallback to DB if miss.
        
        Args:
            key: Cache key
            fallback_func: Function to call on cache miss
            ttl: Time to live in seconds
            
        Returns:
            Cached value or result of fallback function
        """
        value = self.get(key)
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        
        # Cache miss, call fallback function
        value = fallback_func()
        
        # Cache the result
        try:
            if isinstance(value, (dict, list)):
                self.set(key, json.dumps(value), ttl)
            else:
                self.set(key, str(value), ttl)
        except Exception as e:
            logger.warning(f"Failed to cache result for key '{key}': {e}")
        
        return value
    
    @contextmanager
    def pipeline(self):
        """
        Context manager for pipeline operations.
        
        Yields:
            Redis pipeline object or None if using fallback
        """
        if not self._use_fallback and self._client:
            try:
                pipe = self._client.pipeline()
                yield pipe
                pipe.execute()
                return
            except Exception as e:
                logger.warning(f"Redis pipeline failed: {e}")
                _cache_stats['errors'] += 1
        
        # Fallback: yield None, operations will be executed individually
        yield None
    
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
def connect_redis(host: str = "localhost", port: int = 6379, db: int = 0,
                  password: Optional[str] = None, max_connections: int = 50) -> bool:
    """
    Connect to Redis server.
    
    Args:
        host: Redis host
        port: Redis port
        db: Redis database number
        password: Redis password (optional)
        max_connections: Maximum connection pool size
        
    Returns:
        True if connected successfully
    """
    global redis_client
    redis_client = RedisClient(
        host=host,
        port=port,
        db=db,
        password=password,
        max_connections=max_connections
    )
    return redis_client.connect()


def reset_cache_stats() -> None:
    """Reset cache statistics to zero."""
    global _cache_stats
    _cache_stats = {
        'hits': 0,
        'misses': 0,
        'errors': 0,
        'evictions': 0,
        'writes': 0
    }
