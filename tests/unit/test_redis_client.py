"""
Unit tests for Redis Client

Tests for Redis client wrapper including:
- Basic get/set/delete operations
- Connection handling
- Distributed locking
- Cache statistics
- Fallback to in-memory cache

Task: M4-01 - Redis Integration & Performance
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock

from app.utils.redis_client import RedisClient, generate_cache_key, reset_cache_stats


class TestRedisClient:
    """Test suite for RedisClient"""
    
    @pytest.fixture
    def mock_redis_connection(self):
        """Create a mock Redis connection"""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis.delete.return_value = 1
        mock_redis.keys.return_value = []
        mock_redis.mget.return_value = []
        mock_redis.pipeline.return_value = MagicMock()
        mock_redis.info.return_value = {
            'keyspace_hits': 100,
            'keyspace_misses': 20,
            'used_memory': 1024000,
            'used_memory_human': '1.00M',
            'evicted_keys': 5
        }
        return mock_redis
    
    @pytest.fixture
    def redis_client(self, mock_redis_connection):
        """Create a Redis client instance with mocked connection"""
        with patch('app.utils.redis_client.ConnectionPool') as mock_pool:
            mock_pool.return_value = MagicMock()
            client = RedisClient(host="localhost", port=6379, db=0)
            client._client = mock_redis_connection
            client._connected = True
            client._use_fallback = False
            return client
    
    # ============ Basic Operations Tests ============
    
    def test_set_and_get(self, redis_client, mock_redis_connection):
        """Test basic set and get operations"""
        key = "test_key"
        value = "test_value"
        
        redis_client.set(key, value, ttl=300)
        mock_redis_connection.setex.assert_called_once_with(key, 300, value)
        
        mock_redis_connection.get.return_value = value
        result = redis_client.get(key)
        
        assert result == value
        mock_redis_connection.get.assert_called_once_with(key)
    
    def test_get_cache_miss(self, redis_client, mock_redis_connection):
        """Test get operation with cache miss"""
        key = "non_existent_key"
        mock_redis_connection.get.return_value = None
        
        result = redis_client.get(key)
        
        assert result is None
        mock_redis_connection.get.assert_called_once_with(key)
    
    def test_delete(self, redis_client, mock_redis_connection):
        """Test delete operation"""
        key = "test_key"
        mock_redis_connection.delete.return_value = 1
        
        result = redis_client.delete(key)
        
        assert result is True
        mock_redis_connection.delete.assert_called_once_with(key)
    
    def test_clear(self, redis_client, mock_redis_connection):
        """Test clear operation"""
        redis_client.clear()
        mock_redis_connection.flushdb.assert_called_once()
    
    # ============ Connection Tests ============
    
    def test_connect_success(self):
        """Test successful Redis connection"""
        with patch('app.utils.redis_client.ConnectionPool') as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_redis = Mock()
            mock_redis.ping.return_value = True
            
            with patch('app.utils.redis_client.redis.Redis', return_value=mock_redis):
                client = RedisClient(host="localhost", port=6379, db=0)
                
                assert client._connected is True
                assert client._use_fallback is False
    
    def test_connect_failure_fallback(self):
        """Test Redis connection failure with fallback"""
        with patch('app.utils.redis_client.ConnectionPool') as mock_pool:
            mock_pool.side_effect = Exception("Connection failed")
            
            client = RedisClient(host="localhost", port=6379, db=0)
            
            assert client._connected is False
            assert client._use_fallback is True
    
    def test_ping(self, redis_client, mock_redis_connection):
        """Test ping operation"""
        result = redis_client.ping()
        
        assert result is True
        mock_redis_connection.ping.assert_called_once()
    
    # ============ Distributed Locking Tests ============
    
    def test_acquire_lock_success(self, redis_client):
        """Test successful lock acquisition"""
        key = "test_key"
        
        result = redis_client.acquire_lock(key, timeout=10)
        
        assert result is True
        assert key in redis_client._locks
    
    def test_acquire_lock_failure(self, redis_client):
        """Test lock acquisition when already held"""
        key = "test_key"
        
        # Acquire lock first time
        redis_client.acquire_lock(key, timeout=10)
        
        # Try to acquire again (should fail)
        result = redis_client.acquire_lock(key, timeout=10)
        
        assert result is False
    
    def test_release_lock(self, redis_client):
        """Test lock release"""
        key = "test_key"
        
        # Acquire lock
        redis_client.acquire_lock(key, timeout=10)
        
        # Release lock
        result = redis_client.release_lock(key)
        
        assert result is True
        assert key not in redis_client._locks
    
    def test_acquire_lock_with_retry(self, redis_client):
        """Test lock acquisition with retry logic"""
        key = "test_key"
        
        # Acquire lock first time
        redis_client.acquire_lock(key, timeout=10)
        
        # Try to acquire with retry (should fail after retries)
        result = redis_client.acquire_lock_with_retry(key, timeout=10, max_attempts=2)
        
        assert result is False
    
    def test_set_with_lock(self, redis_client, mock_redis_connection):
        """Test set operation with distributed locking"""
        key = "test_key"
        value = "test_value"
        
        result = redis_client.set_with_lock(key, value, ttl=300)
        
        assert result is True
        mock_redis_connection.setex.assert_called_once()
        assert key not in redis_client._locks  # Lock should be released
    
    # ============ Pattern Invalidation Tests ============
    
    def test_invalidate_pattern(self, redis_client, mock_redis_connection):
        """Test pattern-based invalidation"""
        pattern = "form:schema:*"
        mock_redis_connection.keys.return_value = ["form:schema:1", "form:schema:2"]
        mock_redis_connection.delete.return_value = 2
        
        result = redis_client.invalidate_pattern(pattern)
        
        assert result == 2
        mock_redis_connection.keys.assert_called_once_with(pattern)
        mock_redis_connection.delete.assert_called_once()
    
    # ============ Cache Statistics Tests ============
    
    def test_get_cache_stats_redis(self, redis_client, mock_redis_connection):
        """Test getting cache statistics from Redis"""
        reset_cache_stats()
        
        # Simulate some cache operations
        mock_redis_connection.get.return_value = "value"
        redis_client.get("test_key")
        redis_client.get("test_key")
        redis_client.get("test_key")
        mock_redis_connection.get.return_value = None
        redis_client.get("test_key")
        
        stats = redis_client.get_cache_stats()
        
        assert stats['backend'] == 'redis'
        assert stats['connected'] is True
        assert stats['hits'] == 3
        assert stats['misses'] == 1
        assert 'hit_ratio' in stats
        assert 'memory_used' in stats
    
    def test_get_cache_stats_fallback(self):
        """Test getting cache statistics from in-memory fallback"""
        client = RedisClient(host="localhost", port=6379, db=0)
        client._use_fallback = True
        
        # Set some values in memory
        client.set("key1", "value1", ttl=300)
        client.set("key2", "value2", ttl=300)
        
        stats = client.get_cache_stats()
        
        assert stats['backend'] == 'in_memory'
        assert stats['connected'] is False
        assert stats['total_keys'] == 2
        assert stats['fallback_mode'] is True
    
    # ============ Fallback to In-Memory Tests ============
    
    def test_fallback_get(self):
        """Test get operation with in-memory fallback"""
        client = RedisClient(host="localhost", port=6379, db=0)
        client._use_fallback = True
        
        key = "test_key"
        value = "test_value"
        
        # Set value
        client.set(key, value, ttl=300)
        
        # Get value
        result = client.get(key)
        
        assert result == value
    
    def test_fallback_expiration(self):
        """Test TTL expiration in in-memory fallback"""
        client = RedisClient(host="localhost", port=6379, db=0)
        client._use_fallback = True
        
        key = "test_key"
        value = "test_value"
        
        # Set value with short TTL
        client.set(key, value, ttl=1)
        
        # Get immediately (should work)
        result1 = client.get(key)
        assert result1 == value
        
        # Wait for expiration
        time.sleep(2)
        
        # Get after expiration (should return None)
        result2 = client.get(key)
        assert result2 is None
    
    # ============ Utility Function Tests ============
    
    def test_generate_cache_key_simple(self):
        """Test simple cache key generation"""
        key = generate_cache_key("test", param1="value1", param2="value2")
        
        assert "test" in key
        assert "param1=value1" in key
        assert "param2=value2" in key
    
    def test_generate_cache_key_long_key_hashing(self):
        """Test cache key hashing for long keys"""
        # Create a very long key
        long_params = {f"param{i}": f"value{i}" * 100 for i in range(10)}
        key = generate_cache_key("test", **long_params)
        
        # Should be hashed if too long
        assert "hash:" in key
        assert len(key) < 250  # Hashed keys should be shorter
    
    def test_reset_cache_stats(self):
        """Test resetting cache statistics"""
        # Create a client and perform some operations
        client = RedisClient(host="localhost", port=6379, db=0)
        client._use_fallback = True
        
        client.set("key1", "value1", ttl=300)
        client.get("key1")
        client.get("key2")
        
        # Reset stats
        reset_cache_stats()
        
        # Create new client to get fresh stats
        new_client = RedisClient(host="localhost", port=6379, db=0)
        new_client._use_fallback = True
        
        stats = new_client.get_cache_stats()
        
        # Stats should be reset
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['errors'] == 0
    
    # ============ Pipeline Operations Tests ============
    
    def test_pipeline_context(self, redis_client, mock_redis_connection):
        """Test pipeline context manager"""
        with redis_client.pipeline() as pipe:
            if pipe is not None:
                pipe.get("key1")
                pipe.get("key2")
        
        # Verify pipeline was created and executed
        mock_redis_connection.pipeline.assert_called_once()
