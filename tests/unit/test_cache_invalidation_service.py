"""
Unit tests for Cache Invalidation Service

Tests for cache invalidation service including:
- Form-related invalidation
- Response-related invalidation
- User-related invalidation
- Webhook-related invalidation
- Dashboard-related invalidation

Task: M4-01 - Redis Integration & Performance
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.cache_invalidation_service import CacheInvalidationService
from app.services.cache_service import CacheService


class TestCacheInvalidationService:
    """Test suite for CacheInvalidationService"""
    
    @pytest.fixture
    def mock_cache_service(self):
        """Create a mock cache service"""
        mock_service = Mock(spec=CacheService)
        mock_service.invalidate_form_schema.return_value = True
        mock_service.invalidate_query_results.return_value = 5
        mock_service.invalidate_dashboard_widgets.return_value = 3
        mock_service.invalidate_user_session.return_value = True
        mock_service.cache_form_schema.return_value = True
        mock_service.cache_user_session.return_value = True
        return mock_service
    
    @pytest.fixture
    def invalidation_service(self, mock_cache_service):
        """Create a cache invalidation service instance with mocked cache service"""
        return CacheInvalidationService(cache_service=mock_cache_service)
    
    # ============ Form-Related Invalidation Tests ============
    
    def test_on_form_created(self, invalidation_service, mock_cache_service):
        """Test handling form creation event"""
        form_id = "form_123"
        form_data = {
            "id": form_id,
            "schema": {
                "fields": [{"name": "name", "type": "text"}]
            }
        }
        
        results = invalidation_service.on_form_created(form_id, form_data)
        
        assert results['form_schemas_invalidated'] == 0
        assert results['query_results_invalidated'] == 0
        assert results['dashboard_widgets_invalidated'] == 0
        mock_cache_service.cache_form_schema.assert_called_once_with(form_id, form_data['schema'])
    
    def test_on_form_updated(self, invalidation_service, mock_cache_service):
        """Test handling form update event"""
        form_id = "form_123"
        form_data = {
            "id": form_id,
            "schema": {
                "fields": [{"name": "email", "type": "email"}]
            }
        }
        
        results = invalidation_service.on_form_updated(form_id, form_data)
        
        assert results['form_schemas_invalidated'] == 1
        assert results['query_results_invalidated'] == 5
        assert results['dashboard_widgets_invalidated'] == 3
        
        # Verify all invalidation methods were called
        mock_cache_service.invalidate_form_schema.assert_called_once_with(form_id)
        mock_cache_service.invalidate_query_results.assert_called_once_with(form_id=form_id)
        mock_cache_service.invalidate_dashboard_widgets.assert_called_once_with(form_id=form_id)
        mock_cache_service.cache_form_schema.assert_called_once_with(form_id, form_data['schema'])
    
    def test_on_form_deleted(self, invalidation_service, mock_cache_service):
        """Test handling form deletion event"""
        form_id = "form_123"
        
        results = invalidation_service.on_form_deleted(form_id)
        
        assert results['form_schemas_invalidated'] == 1
        assert results['query_results_invalidated'] == 5
        assert results['dashboard_widgets_invalidated'] == 3
        
        # Verify all invalidation methods were called
        mock_cache_service.invalidate_form_schema.assert_called_once_with(form_id)
        mock_cache_service.invalidate_query_results.assert_called_once_with(form_id=form_id)
        mock_cache_service.invalidate_dashboard_widgets.assert_called_once_with(form_id=form_id)
    
    # ============ Response-Related Invalidation Tests ============
    
    def test_on_response_submitted(self, invalidation_service, mock_cache_service):
        """Test handling form submission event"""
        form_id = "form_123"
        response_id = "response_456"
        
        results = invalidation_service.on_response_submitted(form_id, response_id)
        
        assert results['query_results_invalidated'] == 5
        assert results['dashboard_widgets_invalidated'] == 3
        
        # Verify invalidation methods were called
        mock_cache_service.invalidate_query_results.assert_called_once_with(form_id=form_id)
        mock_cache_service.invalidate_dashboard_widgets.assert_called_once_with(form_id=form_id)
    
    def test_on_response_updated(self, invalidation_service, mock_cache_service):
        """Test handling response update event"""
        form_id = "form_123"
        response_id = "response_456"
        
        results = invalidation_service.on_response_updated(form_id, response_id)
        
        assert results['query_results_invalidated'] == 5
        assert results['dashboard_widgets_invalidated'] == 3
        
        # Verify invalidation methods were called
        mock_cache_service.invalidate_query_results.assert_called_once_with(form_id=form_id)
        mock_cache_service.invalidate_dashboard_widgets.assert_called_once_with(form_id=form_id)
    
    # ============ User-Related Invalidation Tests ============
    
    def test_on_user_permission_changed(self, invalidation_service, mock_cache_service):
        """Test handling user permission change event"""
        user_id = "user_456"
        
        results = invalidation_service.on_user_permission_changed(user_id)
        
        assert results['user_sessions_invalidated'] == 1
        assert results['dashboard_widgets_invalidated'] == 3
        
        # Verify invalidation methods were called
        mock_cache_service.invalidate_user_session.assert_called_once_with(user_id)
        mock_cache_service.invalidate_dashboard_widgets.assert_called_once_with(user_id=user_id)
    
    def test_on_user_updated(self, invalidation_service, mock_cache_service):
        """Test handling user update event"""
        user_id = "user_456"
        user_data = {
            "id": user_id,
            "email": "updated@example.com",
            "role": "admin",
            "permissions": ["read", "write", "delete"]
        }
        
        results = invalidation_service.on_user_updated(user_id, user_data)
        
        assert results['user_sessions_invalidated'] == 1
        assert results['dashboard_widgets_invalidated'] == 3
        
        # Verify invalidation methods were called
        mock_cache_service.invalidate_user_session.assert_called_once_with(user_id)
        mock_cache_service.invalidate_dashboard_widgets.assert_called_once_with(user_id=user_id)
        mock_cache_service.cache_user_session.assert_called_once()
    
    # ============ Webhook-Related Invalidation Tests ============
    
    def test_on_webhook_config_changed(self, invalidation_service, mock_cache_service):
        """Test handling webhook configuration change event"""
        webhook_id = "webhook_789"
        form_id = "form_123"
        
        results = invalidation_service.on_webhook_config_changed(webhook_id, form_id)
        
        assert results['api_responses_invalidated'] == 0  # Mock returns 0
        
        # Verify invalidation method was called
        mock_cache_service.redis.invalidate_pattern.assert_called_once()
    
    # ============ Dashboard-Related Invalidation Tests ============
    
    def test_on_dashboard_updated(self, invalidation_service, mock_cache_service):
        """Test handling dashboard update event"""
        user_id = "user_456"
        
        results = invalidation_service.on_dashboard_updated(user_id)
        
        assert results['dashboard_widgets_invalidated'] == 3
        
        # Verify invalidation method was called
        mock_cache_service.invalidate_dashboard_widgets.assert_called_once_with(user_id=user_id)
    
    # ============ Utility Method Tests ============
    
    def test_get_invalidation_log(self, invalidation_service):
        """Test getting invalidation log"""
        # Trigger some invalidation events
        invalidation_service.on_form_updated("form_1", {"schema": {}})
        invalidation_service.on_user_permission_changed("user_1")
        
        log = invalidation_service.get_invalidation_log(limit=10)
        
        assert len(log) >= 2
        assert log[-1]['event_type'] == 'user_permission_changed'
        assert log[-2]['event_type'] == 'form_updated'
    
    def test_get_invalidation_log_limit(self, invalidation_service):
        """Test getting invalidation log with limit"""
        # Trigger multiple events
        for i in range(5):
            invalidation_service.on_form_updated(f"form_{i}", {"schema": {}})
        
        log = invalidation_service.get_invalidation_log(limit=3)
        
        assert len(log) == 3
    
    def test_clear_invalidation_log(self, invalidation_service):
        """Test clearing invalidation log"""
        # Trigger some events
        invalidation_service.on_form_updated("form_1", {"schema": {}})
        
        # Clear log
        invalidation_service.clear_invalidation_log()
        
        log = invalidation_service.get_invalidation_log()
        assert len(log) == 0
    
    def test_log_size_management(self, invalidation_service):
        """Test that log size is managed (max 1000 entries)"""
        # Trigger more than 1000 events
        for i in range(1100):
            invalidation_service.on_form_updated(f"form_{i}", {"schema": {}})
        
        log = invalidation_service.get_invalidation_log()
        
        # Log should be limited to 1000 entries
        assert len(log) == 1000
