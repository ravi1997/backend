"""
Cache Statistics API Endpoint

Provides admin endpoints for:
- Viewing cache statistics
- Clearing cache
- Cache warmup
- Cache pattern invalidation

Task: M4-01 - Redis Integration & Performance
"""

import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from functools import wraps

from app.services.cache_service import cache_service
from app import config

logger = logging.getLogger(__name__)

cache_stats_bp = Blueprint('cache_stats', __name__, url_prefix='/api/v1/admin/cache')


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(current_user, 'role') or current_user.role != config.ADMIN_ROLE:
            logger.warning(f"Admin access denied for user: {getattr(current_user, 'id', 'unknown')}")
            return jsonify({'error': 'Admin access required'}), 403
        logger.info(f"Admin access granted for user: {getattr(current_user, 'id', 'unknown')}")
        return f(*args, **kwargs)
    return decorated_function


@cache_stats_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_cache_stats():
    """
    Get comprehensive cache statistics.
    
    Returns:
        JSON with cache statistics including:
        - Backend type (redis/in_memory)
        - Connection status
        - Hit/miss ratios
        - Memory usage
        - Eviction count
    """
    try:
        logger.info("Fetching cache statistics")
        stats = cache_service.get_stats()
        logger.debug(f"Cache stats fetched successfully: {stats}")
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@cache_stats_bp.route('/all', methods=['DELETE'])
@jwt_required()
@admin_required
def clear_all_cache():
    """
    Clear all cached data.
    
    Returns:
        JSON with success status
    """
    try:
        logger.info("Attempting to clear all cache")
        success = cache_service.clear_all_cache()
        if success:
            logger.info("All cache cleared successfully")
            return jsonify({
                'message': 'All cache cleared successfully',
                'timestamp': cache_service.redis.get_cache_stats().get('timestamp')
            }), 200
        else:
            logger.error("Failed to clear all cache: service returned failure")
            return jsonify({'error': 'Failed to clear cache'}), 500
    except Exception as e:
        logger.error(f"Critical error during cache clear: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@cache_stats_bp.route('/pattern/<pattern>', methods=['DELETE'])
@jwt_required()
@admin_required
def clear_cache_pattern(pattern):
    """
    Clear cache entries matching a pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "form:schema:*")
        
    Returns:
        JSON with number of keys deleted
    """
    try:
        logger.info(f"Clearing cache entries matching pattern: {pattern}")
        deleted = cache_service.redis.invalidate_pattern(pattern)
        logger.info(f"Successfully deleted {deleted} keys for pattern: {pattern}")
        return jsonify({
            'message': f'Cleared {deleted} cache entries matching pattern: {pattern}',
            'deleted_count': deleted
        }), 200
    except Exception as e:
        logger.error(f"Failed to clear cache pattern {pattern}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@cache_stats_bp.route('/warmup', methods=['POST'])
@jwt_required()
@admin_required
def warmup_cache():
    """
    Trigger cache warmup with frequently accessed data.
    
    Request Body:
        {
            "forms": [{"id": "form1", "schema": {...}}],
            "users": [{"id": "user1", "email": "..."}]
        }
        
    Returns:
        JSON with warmup results
    """
    try:
        data = request.get_json() or {}
        forms = data.get('forms', [])
        users = data.get('users', [])
        
        logger.info(f"Starting cache warmup for {len(forms)} forms and {len(users)} users")
        results = cache_service.warmup_cache(forms=forms, users=users)
        logger.info("Cache warmup completed")
        
        return jsonify({
            'message': 'Cache warmup completed',
            'results': results
        }), 200
    except Exception as e:
        logger.error(f"Cache warmup failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@cache_stats_bp.route('/form/<form_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def clear_form_cache(form_id):
    """
    Clear all cache entries for a specific form.
    
    Args:
        form_id: Form identifier
        
    Returns:
        JSON with success status
    """
    try:
        logger.info(f"Clearing cache for form_id: {form_id}")
        # Clear form schema cache
        cache_service.invalidate_form_schema(form_id)
        
        # Clear query results related to this form
        cache_service.invalidate_query_results(form_id=form_id)
        
        # Clear dashboard widgets related to this form
        cache_service.invalidate_dashboard_widgets(form_id=form_id)
        
        logger.info(f"Successfully cleared all cache for form_id: {form_id}")
        return jsonify({
            'message': f'Cleared all cache entries for form: {form_id}',
            'form_id': form_id
        }), 200
    except Exception as e:
        logger.error(f"Failed to clear form cache {form_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@cache_stats_bp.route('/user/<user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def clear_user_cache(user_id):
    """
    Clear all cache entries for a specific user.
    
    Args:
        user_id: User identifier
        
    Returns:
        JSON with success status
    """
    try:
        logger.info(f"Clearing cache for user_id: {user_id}")
        # Clear user session cache
        cache_service.invalidate_user_session(user_id)
        
        # Clear dashboard widgets for this user
        cache_service.invalidate_dashboard_widgets(user_id=user_id)
        
        logger.info(f"Successfully cleared all cache for user_id: {user_id}")
        return jsonify({
            'message': f'Cleared all cache entries for user: {user_id}',
            'user_id': user_id
        }), 200
    except Exception as e:
        logger.error(f"Failed to clear user cache {user_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@cache_stats_bp.route('/health', methods=['GET'])
@jwt_required()
@admin_required
def cache_health():
    """
    Get cache health status.
    
    Returns:
        JSON with health status and metrics
    """
    try:
        logger.info("Checking cache health")
        stats = cache_service.get_stats()
        
        # Determine health status
        hit_ratio = stats.get('hit_ratio', 0.0)
        memory_used = stats.get('memory_used', 0)
        errors = stats.get('errors', 0)
        connected = stats.get('connected', False)
        
        if hit_ratio > 0.8 and errors == 0:
            status = 'healthy'
            logger.info("Cache status: healthy")
        elif hit_ratio > 0.5 and errors < 10:
            status = 'degraded'
            logger.warning(f"Cache status: degraded (hit_ratio={hit_ratio}, errors={errors})")
        else:
            status = 'unhealthy'
            logger.error(f"Cache status: unhealthy (hit_ratio={hit_ratio}, errors={errors}, connected={connected})")
        
        return jsonify({
            'status': status,
            'backend': stats.get('backend', 'unknown'),
            'connected': connected,
            'hit_ratio': hit_ratio,
            'memory_used': memory_used,
            'memory_human': stats.get('memory_human', 'N/A'),
            'errors': errors,
            'cache_enabled': stats.get('cache_enabled', False)
        }), 200
    except Exception as e:
        logger.error(f"Failed to get cache health: {e}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@cache_stats_bp.route('/config', methods=['GET'])
@jwt_required()
@admin_required
def get_cache_config():
    """
    Get current cache configuration.
    
    Returns:
        JSON with cache configuration
    """
    try:
        logger.info("Fetching cache configuration")
        config_data = {
            'cache_enabled': config.CACHE_ENABLED,
            'default_ttl': config.CACHE_DEFAULT_TTL,
            'redis_host': config.REDIS_HOST,
            'redis_port': config.REDIS_PORT,
            'redis_db': config.REDIS_DB,
            'cache_types': {
                'form_schema': {
                    'ttl': config.CACHE_TTL_FORM_SCHEMA,
                    'max_entries': config.CACHE_MAX_ENTRIES_FORM_SCHEMA
                },
                'user_session': {
                    'ttl': config.CACHE_TTL_USER_SESSION,
                    'max_entries': config.CACHE_MAX_ENTRIES_USER_SESSION
                },
                'query_result': {
                    'ttl': config.CACHE_TTL_QUERY_RESULT,
                    'max_entries': config.CACHE_MAX_ENTRIES_QUERY_RESULT
                },
                'dashboard_widget': {
                    'ttl': config.CACHE_TTL_DASHBOARD_WIDGET,
                    'max_entries': config.CACHE_MAX_ENTRIES_DASHBOARD_WIDGET
                },
                'api_response': {
                    'ttl': config.CACHE_TTL_API_RESPONSE,
                    'max_entries': 10000
                }
            }
        }
        logger.debug(f"Cache config fetched: {config_data}")
        return jsonify(config_data), 200
    except Exception as e:
        logger.error(f"Failed to get cache config: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
