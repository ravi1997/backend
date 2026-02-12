"""
Unit tests for Cache Service

Tests for the cache service layer including:
- Form schema caching
- User session caching
- Query result caching
- Dashboard widget caching
- API response caching
- Cache statistics

Task: M4-01 - Redis Integration & Performance
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.cache_service import CacheService
from app.utils.redis_client import RedisClient


class TestCacheService:
    """Test suite for CacheService"""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client"""
        mock_client = Mock(spec=RedisClient)
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.delete.return_value = True
        mock_client.invalidate_pattern.return_value = 0
        return mock_client
    
    @pytest.fixture
    def cache_service(self, mock_redis_client):
        """Create a cache service instance with mocked Redis"""
        return CacheService(redis_client=mock_redis_client)
    
    # ============ Form Schema Caching Tests ============
    
    def test_cache_form_schema_success(self, cache_service, mock_redis_client):
        """Test successful form schema caching"""
        form_id = "test_form_123"
        schema = {
            "fields": [
                {"name": "name", "type": "text"},
                {"name": "email", "type": "email"}
            ]
        }
        
        result = cache_service.cache_form_schema(form_id, schema)
        
        assert result is True
        mock_redis_client.set.assert_called_once()
        call_args = mock_redis_client.set.call_args
        assert "form:schema:test_form_123" in call_args[0][0]
        
        # Verify cached data structure
        cached_data = json.loads(call_args[0][1])
        assert cached_data['schema'] == schema
        assert 'cached_at' in cached_data
        assert cached_data['cache_type'] == 'form_schema'
    
    def test_get_form_schema_hit(self, cache_service, mock_redis_client):
        """Test getting cached form schema (cache hit)"""
        form_id = "test_form_123"
        schema = {"fields": [{"name": "name", "type": "text"}]}
        cached_data = json.dumps({
            'schema': schema,
            'cached_at': datetime.utcnow().isoformat(),
            'cache_type': 'form_schema'
        })
        
        mock_redis_client.get.return_value = cached_data
        
        result = cache_service.get_form_schema(form_id)
        
        assert result == schema
        mock_redis_client.get.assert_called_once_with("form:schema:test_form_123")
    
    def test_get_form_schema_miss(self, cache_service, mock_redis_client):
        """Test getting cached form schema (cache miss)"""
        form_id = "test_form_123"
        mock_redis_client.get.return_value = None
        
        result = cache_service.get_form_schema(form_id)
        
        assert result is None
        mock_redis_client.get.assert_called_once_with("form:schema:test_form_123")
    
    def test_invalidate_form_schema(self, cache_service, mock_redis_client):
        """Test invalidating form schema cache"""
        form_id = "test_form_123"
        mock_redis_client.delete.return_value = 1
        
        result = cache_service.invalidate_form_schema(form_id)
        
        assert result is True
        mock_redis_client.delete.assert_called_once_with("form:schema:test_form_123")
    
    # ============ User Session Caching Tests ============
    
    def test_cache_user_session_success(self, cache_service, mock_redis_client):
        """Test successful user session caching"""
        user_id = "user_456"
        session_data = {
            "id": user_id,
            "email": "test@example.com",
            "role": "admin",
            "permissions": ["read", "write"]
        }
        
        result = cache_service.cache_user_session(user_id, session_data)
        
        assert result is True
        mock_redis_client.set.assert_called_once()
        call_args = mock_redis_client.set.call_args
        assert "user:session:user_456" in call_args[0][0]
        
        # Verify cached data structure
        cached_data = json.loads(call_args[0][1])
        assert cached_data['session'] == session_data
        assert 'cached_at' in cached_data
        assert cached_data['cache_type'] == 'user_session'
    
    def test_get_user_session_hit(self, cache_service, mock_redis_client):
        """Test getting cached user session (cache hit)"""
        user_id = "user_456"
        session_data = {
            "id": user_id,
            "email": "test@example.com",
            "role": "admin"
        }
        cached_data = json.dumps({
            'session': session_data,
            'cached_at': datetime.utcnow().isoformat(),
            'cache_type': 'user_session'
        })
        
        mock_redis_client.get.return_value = cached_data
        
        result = cache_service.get_user_session(user_id)
        
        assert result == session_data
        mock_redis_client.get.assert_called_once_with("user:session:user_456")
    
    def test_invalidate_user_session(self, cache_service, mock_redis_client):
        """Test invalidating user session cache"""
        user_id = "user_456"
        mock_redis_client.delete.return_value = 1
        
        result = cache_service.invalidate_user_session(user_id)
        
        assert result is True
        mock_redis_client.delete.assert_called_once_with("user:session:user_456")
    
    # ============ Query Result Caching Tests ============
    
    def test_cache_query_result_success(self, cache_service, mock_redis_client):
        """Test successful query result caching"""
        query_hash = "abc123def456"
        results = [
            {"id": "1", "name": "Form 1"},
            {"id": "2", "name": "Form 2"}
        ]
        
        result = cache_service.cache_query_result(query_hash, results)
        
        assert result is True
        mock_redis_client.set.assert_called_once()
        call_args = mock_redis_client.set.call_args
        assert "query:result:abc123def456" in call_args[0][0]
        
        # Verify cached data structure
        cached_data = json.loads(call_args[0][1])
        assert cached_data['results'] == results
        assert 'cached_at' in cached_data
        assert cached_data['cache_type'] == 'query_result'
    
    def test_get_query_result_hit(self, cache_service, mock_redis_client):
        """Test getting cached query result (cache hit)"""
        query_hash = "abc123def456"
        results = [{"id": "1", "name": "Form 1"}]
        cached_data = json.dumps({
            'results': results,
            'cached_at': datetime.utcnow().isoformat(),
            'cache_type': 'query_result'
        })
        
        mock_redis_client.get.return_value = cached_data
        
        result = cache_service.get_query_result(query_hash)
        
        assert result == results
        mock_redis_client.get.assert_called_once_with("query:result:abc123def456")
    
    def test_invalidate_query_results(self, cache_service, mock_redis_client):
        """Test invalidating query results"""
        form_id = "form_123"
        mock_redis_client.invalidate_pattern.return_value = 5
        
        result = cache_service.invalidate_query_results(form_id=form_id)
        
        assert result is True
        mock_redis_client.invalidate_pattern.assert_called_once()
    
    # ============ Dashboard Widget Caching Tests ============
    
    def test_cache_dashboard_widget_success(self, cache_service, mock_redis_client):
        """Test successful dashboard widget caching"""
        user_id = "user_456"
        widget_id = "widget_789"
        widget_data = {
            "type": "chart",
            "data": [10, 20, 30, 40]
        }
        
        result = cache_service.cache_dashboard_widget(user_id, widget_id, widget_data)
        
        assert result is True
        mock_redis_client.set.assert_called_once()
        call_args = mock_redis_client.set.call_args
        assert "dashboard:widget:user_456:widget_789" in call_args[0][0]
        
        # Verify cached data structure
        cached_data = json.loads(call_args[0][1])
        assert cached_data['data'] == widget_data
        assert 'cached_at' in cached_data
        assert cached_data['cache_type'] == 'dashboard_widget'
    
    def test_get_dashboard_widget_hit(self, cache_service, mock_redis_client):
        """Test getting cached dashboard widget (cache hit)"""
        user_id = "user_456"
        widget_id = "widget_789"
        widget_data = {"type": "chart", "data": [10, 20, 30]}
        cached_data = json.dumps({
            'data': widget_data,
            'cached_at': datetime.utcnow().isoformat(),
            'cache_type': 'dashboard_widget'
        })
        
        mock_redis_client.get.return_value = cached_data
        
        result = cache_service.get_dashboard_widget(user_id, widget_id)
        
        assert result == widget_data
        mock_redis_client.get.assert_called_once_with("dashboard:widget:user_456:widget_789")
    
    def test_invalidate_dashboard_widgets(self, cache_service, mock_redis_client):
        """Test invalidating dashboard widgets"""
        user_id = "user_456"
        form_id = "form_123"
        mock_redis_client.invalidate_pattern.return_value = 3
        
        result = cache_service.invalidate_dashboard_widgets(user_id=user_id, form_id=form_id)
        
        assert result is True
        mock_redis_client.invalidate_pattern.assert_called_once()
    
    # ============ API Response Caching Tests ============
    
    def test_cache_api_response_success(self, cache_service, mock_redis_client):
        """Test successful API response caching"""
        endpoint = "/api/v1/forms"
        params_hash = "xyz789"
        response_data = {"forms": [{"id": "1", "name": "Form 1"}]}
        
        result = cache_service.cache_api_response(endpoint, params_hash, response_data)
        
        assert result is True
        mock_redis_client.set.assert_called_once()
        call_args = mock_redis_client.set.call_args
        assert "api:response:/api/v1/forms:xyz789" in call_args[0][0]
        
        # Verify cached data structure
        cached_data = json.loads(call_args[0][1])
        assert cached_data['response'] == response_data
        assert 'cached_at' in cached_data
        assert cached_data['cache_type'] == 'api_response'
    
    def test_get_api_response_hit(self, cache_service, mock_redis_client):
        """Test getting cached API response (cache hit)"""
        endpoint = "/api/v1/forms"
        params_hash = "xyz789"
        response_data = {"forms": [{"id": "1", "name": "Form 1"}]}
        cached_data = json.dumps({
            'response': response_data,
            'cached_at': datetime.utcnow().isoformat(),
            'cache_type': 'api_response'
        })
        
        mock_redis_client.get.return_value = cached_data
        
        result = cache_service.get_api_response(endpoint, params_hash)
        
        assert result == response_data
        mock_redis_client.get.assert_called_once_with("api:response:/api/v1/forms:xyz789")
    
    # ============ Cache Statistics Tests ============
    
    def test_get_stats(self, cache_service, mock_redis_client):
        """Test getting cache statistics"""
        mock_stats = {
            'backend': 'redis',
            'connected': True,
            'total_keys': 100,
            'hits': 80,
            'misses': 20,
            'hit_ratio': 0.8,
            'memory_used': 1024000,
            'memory_human': '1.00M',
            'evictions': 5,
            'writes': 100,
            'errors': 0,
            'fallback_mode': False
        }
        mock_redis_client.get_cache_stats.return_value = mock_stats
        
        stats = cache_service.get_stats()
        
        assert stats['backend'] == 'redis'
        assert stats['connected'] is True
        assert stats['hit_ratio'] == 0.8
        assert 'cache_types' in stats
        mock_redis_client.get_cache_stats.assert_called_once()
    
    # ============ Cache Warming Tests ============
    
    def test_warmup_cache_forms(self, cache_service, mock_redis_client):
        """Test cache warmup with forms"""
        forms = [
            {"id": "form_1", "schema": {"fields": [{"name": "name"}]}},
            {"id": "form_2", "schema": {"fields": [{"name": "email"}]}}
        ]
        
        results = cache_service.warmup_cache(forms=forms)
        
        assert results['forms_cached'] == 2
        assert results['users_cached'] == 0
        assert results['errors'] == 0
        assert mock_redis_client.set.call_count == 2
    
    def test_warmup_cache_users(self, cache_service, mock_redis_client):
        """Test cache warmup with users"""
        users = [
            {"id": "user_1", "email": "user1@example.com", "role": "admin"},
            {"id": "user_2", "email": "user2@example.com", "role": "user"}
        ]
        
        results = cache_service.warmup_cache(users=users)
        
        assert results['forms_cached'] == 0
        assert results['users_cached'] == 2
        assert results['errors'] == 0
        assert mock_redis_client.set.call_count == 2
    
    # ============ Utility Method Tests ============
    
    def test_generate_query_hash(self, cache_service):
        """Test query hash generation"""
        query = "test query"
        filters = {"status": "active", "date": "2024-01-01"}
        
        hash1 = cache_service.generate_query_hash(query, filters)
        hash2 = cache_service.generate_query_hash(query, filters)
        
        # Same input should produce same hash
        assert hash1 == hash2
        
        # Different input should produce different hash
        hash3 = cache_service.generate_query_hash(query, {"status": "inactive"})
        assert hash1 != hash3
        
        # Hash should be 32 characters
        assert len(hash1) == 32
    
    def test_clear_all_cache(self, cache_service, mock_redis_client):
        """Test clearing all cache"""
        mock_redis_client.clear.return_value = True
        
        result = cache_service.clear_all_cache()
        
        assert result is True
        mock_redis_client.clear.assert_called_once()
    
    def test_is_enabled(self, cache_service):
        """Test cache enabled status"""
        with patch('app.services.cache_service.config') as mock_config:
            mock_config.CACHE_ENABLED = True
            assert cache_service.is_enabled() is True
            
            mock_config.CACHE_ENABLED = False
            assert cache_service.is_enabled() is False
