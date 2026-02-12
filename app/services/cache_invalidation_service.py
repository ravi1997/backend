"""
Cache Invalidation Service - Event-driven cache invalidation

Handles automatic cache invalidation based on data changes:
- Form updates invalidate form schema cache
- Form submissions invalidate dashboard and query caches
- User permission changes invalidate session cache
- Webhook configuration changes invalidate webhook cache

Task: M4-01 - Redis Integration & Performance
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class CacheInvalidationService:
    """
    Event-driven cache invalidation service.
    
    Automatically invalidates related cache entries when data changes,
    ensuring data consistency while maintaining cache performance.
    """
    
    def __init__(self, cache_service=None):
        """
        Initialize cache invalidation service.
        
        Args:
            cache_service: Cache service instance (uses global if not provided)
        """
        self.cache_service = cache_service or cache_service
        self._invalidation_log = []
        
        logger.info("CacheInvalidationService initialized")
    
    # ============ Form-Related Invalidation ============
    
    def on_form_created(self, form_id: str, form_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Handle form creation event.
        
        Args:
            form_id: Form identifier
            form_data: Form data
            
        Returns:
            Dictionary with invalidation counts
        """
        results = {
            'form_schemas_invalidated': 0,
            'query_results_invalidated': 0,
            'dashboard_widgets_invalidated': 0
        }
        
        try:
            # Cache the new form schema
            schema = form_data.get('schema')
            if schema:
                self.cache_service.cache_form_schema(form_id, schema)
                logger.info(f"Cached new form schema: {form_id}")
            
            self._log_invalidation('form_created', form_id, results)
            return results
            
        except Exception as e:
            logger.error(f"Failed to handle form creation for {form_id}: {e}")
            return results
    
    def on_form_updated(self, form_id: str, form_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Handle form update event.
        
        Args:
            form_id: Form identifier
            form_data: Updated form data
            
        Returns:
            Dictionary with invalidation counts
        """
        results = {
            'form_schemas_invalidated': 0,
            'query_results_invalidated': 0,
            'dashboard_widgets_invalidated': 0
        }
        
        try:
            # Invalidate form schema cache
            if self.cache_service.invalidate_form_schema(form_id):
                results['form_schemas_invalidated'] += 1
                logger.info(f"Invalidated form schema cache: {form_id}")
            
            # Invalidate query results related to this form
            deleted_queries = self.cache_service.invalidate_query_results(form_id=form_id)
            results['query_results_invalidated'] = deleted_queries
            logger.info(f"Invalidated {deleted_queries} query result caches for form: {form_id}")
            
            # Invalidate dashboard widgets related to this form
            deleted_widgets = self.cache_service.invalidate_dashboard_widgets(form_id=form_id)
            results['dashboard_widgets_invalidated'] = deleted_widgets
            logger.info(f"Invalidated {deleted_widgets} dashboard widget caches for form: {form_id}")
            
            # Cache the updated form schema
            schema = form_data.get('schema')
            if schema:
                self.cache_service.cache_form_schema(form_id, schema)
                logger.info(f"Cached updated form schema: {form_id}")
            
            self._log_invalidation('form_updated', form_id, results)
            return results
            
        except Exception as e:
            logger.error(f"Failed to handle form update for {form_id}: {e}")
            return results
    
    def on_form_deleted(self, form_id: str) -> Dict[str, int]:
        """
        Handle form deletion event.
        
        Args:
            form_id: Form identifier
            
        Returns:
            Dictionary with invalidation counts
        """
        results = {
            'form_schemas_invalidated': 0,
            'query_results_invalidated': 0,
            'dashboard_widgets_invalidated': 0
        }
        
        try:
            # Invalidate form schema cache
            if self.cache_service.invalidate_form_schema(form_id):
                results['form_schemas_invalidated'] += 1
                logger.info(f"Invalidated form schema cache: {form_id}")
            
            # Invalidate query results related to this form
            deleted_queries = self.cache_service.invalidate_query_results(form_id=form_id)
            results['query_results_invalidated'] = deleted_queries
            logger.info(f"Invalidated {deleted_queries} query result caches for form: {form_id}")
            
            # Invalidate dashboard widgets related to this form
            deleted_widgets = self.cache_service.invalidate_dashboard_widgets(form_id=form_id)
            results['dashboard_widgets_invalidated'] = deleted_widgets
            logger.info(f"Invalidated {deleted_widgets} dashboard widget caches for form: {form_id}")
            
            self._log_invalidation('form_deleted', form_id, results)
            return results
            
        except Exception as e:
            logger.error(f"Failed to handle form deletion for {form_id}: {e}")
            return results
    
    # ============ Response-Related Invalidation ============
    
    def on_response_submitted(self, form_id: str, response_id: str) -> Dict[str, int]:
        """
        Handle form submission event.
        
        Args:
            form_id: Form identifier
            response_id: Response identifier
            
        Returns:
            Dictionary with invalidation counts
        """
        results = {
            'query_results_invalidated': 0,
            'dashboard_widgets_invalidated': 0
        }
        
        try:
            # Invalidate query results related to this form
            deleted_queries = self.cache_service.invalidate_query_results(form_id=form_id)
            results['query_results_invalidated'] = deleted_queries
            logger.info(f"Invalidated {deleted_queries} query result caches for form: {form_id}")
            
            # Invalidate dashboard widgets related to this form
            deleted_widgets = self.cache_service.invalidate_dashboard_widgets(form_id=form_id)
            results['dashboard_widgets_invalidated'] = deleted_widgets
            logger.info(f"Invalidated {deleted_widgets} dashboard widget caches for form: {form_id}")
            
            self._log_invalidation('response_submitted', f"{form_id}:{response_id}", results)
            return results
            
        except Exception as e:
            logger.error(f"Failed to handle response submission for {form_id}:{response_id}: {e}")
            return results
    
    def on_response_updated(self, form_id: str, response_id: str) -> Dict[str, int]:
        """
        Handle response update event.
        
        Args:
            form_id: Form identifier
            response_id: Response identifier
            
        Returns:
            Dictionary with invalidation counts
        """
        results = {
            'query_results_invalidated': 0,
            'dashboard_widgets_invalidated': 0
        }
        
        try:
            # Invalidate query results related to this form
            deleted_queries = self.cache_service.invalidate_query_results(form_id=form_id)
            results['query_results_invalidated'] = deleted_queries
            logger.info(f"Invalidated {deleted_queries} query result caches for form: {form_id}")
            
            # Invalidate dashboard widgets related to this form
            deleted_widgets = self.cache_service.invalidate_dashboard_widgets(form_id=form_id)
            results['dashboard_widgets_invalidated'] = deleted_widgets
            logger.info(f"Invalidated {deleted_widgets} dashboard widget caches for form: {form_id}")
            
            self._log_invalidation('response_updated', f"{form_id}:{response_id}", results)
            return results
            
        except Exception as e:
            logger.error(f"Failed to handle response update for {form_id}:{response_id}: {e}")
            return results
    
    # ============ User-Related Invalidation ============
    
    def on_user_permission_changed(self, user_id: str) -> Dict[str, int]:
        """
        Handle user permission change event.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with invalidation counts
        """
        results = {
            'user_sessions_invalidated': 0,
            'dashboard_widgets_invalidated': 0
        }
        
        try:
            # Invalidate user session cache
            if self.cache_service.invalidate_user_session(user_id):
                results['user_sessions_invalidated'] += 1
                logger.info(f"Invalidated user session cache: {user_id}")
            
            # Invalidate dashboard widgets for this user
            deleted_widgets = self.cache_service.invalidate_dashboard_widgets(user_id=user_id)
            results['dashboard_widgets_invalidated'] = deleted_widgets
            logger.info(f"Invalidated {deleted_widgets} dashboard widget caches for user: {user_id}")
            
            self._log_invalidation('user_permission_changed', user_id, results)
            return results
            
        except Exception as e:
            logger.error(f"Failed to handle user permission change for {user_id}: {e}")
            return results
    
    def on_user_updated(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Handle user update event.
        
        Args:
            user_id: User identifier
            user_data: Updated user data
            
        Returns:
            Dictionary with invalidation counts
        """
        results = {
            'user_sessions_invalidated': 0,
            'dashboard_widgets_invalidated': 0
        }
        
        try:
            # Invalidate user session cache
            if self.cache_service.invalidate_user_session(user_id):
                results['user_sessions_invalidated'] += 1
                logger.info(f"Invalidated user session cache: {user_id}")
            
            # Invalidate dashboard widgets for this user
            deleted_widgets = self.cache_service.invalidate_dashboard_widgets(user_id=user_id)
            results['dashboard_widgets_invalidated'] = deleted_widgets
            logger.info(f"Invalidated {deleted_widgets} dashboard widget caches for user: {user_id}")
            
            # Cache updated user session data
            session_data = {
                'id': user_id,
                'email': user_data.get('email'),
                'role': user_data.get('role'),
                'permissions': user_data.get('permissions', [])
            }
            self.cache_service.cache_user_session(user_id, session_data)
            logger.info(f"Cached updated user session: {user_id}")
            
            self._log_invalidation('user_updated', user_id, results)
            return results
            
        except Exception as e:
            logger.error(f"Failed to handle user update for {user_id}: {e}")
            return results
    
    # ============ Webhook-Related Invalidation ============
    
    def on_webhook_config_changed(self, webhook_id: str, form_id: Optional[str] = None) -> Dict[str, int]:
        """
        Handle webhook configuration change event.
        
        Args:
            webhook_id: Webhook identifier
            form_id: Optional form identifier
            
        Returns:
            Dictionary with invalidation counts
        """
        results = {
            'api_responses_invalidated': 0
        }
        
        try:
            # Invalidate API responses for webhook endpoints
            pattern = f"api:response:*webhook*"
            deleted = self.cache_service.redis.invalidate_pattern(pattern)
            results['api_responses_invalidated'] = deleted
            logger.info(f"Invalidated {deleted} API response caches for webhook: {webhook_id}")
            
            self._log_invalidation('webhook_config_changed', webhook_id, results)
            return results
            
        except Exception as e:
            logger.error(f"Failed to handle webhook config change for {webhook_id}: {e}")
            return results
    
    # ============ Dashboard-Related Invalidation ============
    
    def on_dashboard_updated(self, user_id: str) -> Dict[str, int]:
        """
        Handle dashboard update event.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with invalidation counts
        """
        results = {
            'dashboard_widgets_invalidated': 0
        }
        
        try:
            # Invalidate all dashboard widgets for this user
            deleted_widgets = self.cache_service.invalidate_dashboard_widgets(user_id=user_id)
            results['dashboard_widgets_invalidated'] = deleted_widgets
            logger.info(f"Invalidated {deleted_widgets} dashboard widget caches for user: {user_id}")
            
            self._log_invalidation('dashboard_updated', user_id, results)
            return results
            
        except Exception as e:
            logger.error(f"Failed to handle dashboard update for {user_id}: {e}")
            return results
    
    # ============ Utility Methods ============
    
    def _log_invalidation(self, event_type: str, resource_id: str, 
                          results: Dict[str, int]) -> None:
        """
        Log cache invalidation event.
        
        Args:
            event_type: Type of event
            resource_id: Resource identifier
            results: Invalidation results
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'resource_id': resource_id,
            'results': results
        }
        
        self._invalidation_log.append(log_entry)
        
        # Keep log size manageable (last 1000 entries)
        if len(self._invalidation_log) > 1000:
            self._invalidation_log = self._invalidation_log[-1000:]
    
    def get_invalidation_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent cache invalidation log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of invalidation log entries
        """
        return self._invalidation_log[-limit:]
    
    def clear_invalidation_log(self) -> None:
        """Clear the invalidation log."""
        self._invalidation_log.clear()
        logger.info("Cache invalidation log cleared")


# Global cache invalidation service instance
cache_invalidation_service = CacheInvalidationService()
