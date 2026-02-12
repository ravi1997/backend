"""
User Dashboard Settings Routes

Endpoints for managing user dashboard customization:
- GET /api/v1/dashboard/settings - Get user dashboard settings
- PUT /api/v1/dashboard/settings - Update user dashboard settings
- POST /api/v1/dashboard/reset - Reset to default settings
- GET /api/v1/dashboard/widgets - Get available widgets
- POST /api/v1/dashboard/widgets - Add widget to dashboard
- DELETE /api/v1/dashboard/widgets/<widget_id> - Remove widget from dashboard
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.dashboard_service import DashboardService
from app.utils.decorator import require_roles
import logging

dashboard_settings_bp = Blueprint('dashboard_settings', __name__, url_prefix='/api/v1/dashboard')
logger = logging.getLogger(__name__)


# ==================== Settings Endpoints ====================

@dashboard_settings_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_dashboard_settings():
    """
    Get user dashboard settings.
    
    Returns the complete dashboard customization settings for the authenticated user.
    If no settings exist, default settings are created and returned.
    
    Returns:
        200: Dashboard settings object
        401: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"--- Get Dashboard Settings branch started for user: {user_id} ---")
        settings = DashboardService.get_or_create_settings(user_id)
        
        logger.info(f"Successfully retrieved dashboard settings for user: {user_id}")
        return jsonify({
            'success': True,
            'settings': settings.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard settings: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve dashboard settings'
        }), 500


@dashboard_settings_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_dashboard_settings():
    """
    Update user dashboard settings.
    
    Updates the dashboard customization settings for the authenticated user.
    All fields are optional - only provided fields will be updated.
    
    Request Body:
        {
            "layout": {...},      // Layout configuration
            "widgets": [...],     // Widgets array
            "theme": "dark",      // Theme preference (light/dark/system)
            "language": "en",     // Language preference
            "timezone": "UTC"     // Timezone preference
        }
    
    Returns:
        200: Updated settings object
        400: Validation error
        401: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"--- Update Dashboard Settings branch started for user: {user_id} ---")
        data = request.get_json()
        
        if not data:
            logger.warning(f"Update failed: Missing request body for user: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Validate settings if provided
        if any(key in data for key in ['layout', 'widgets', 'theme']):
            logger.debug(f"Validating dashboard settings for user: {user_id}")
            validation_result = DashboardService.validate_settings(data)
            if not validation_result['valid']:
                logger.warning(f"Validation failed for dashboard settings update (user: {user_id}): {validation_result['errors']}")
                return jsonify({
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }), 400
            logger.debug(f"Validation successful for user: {user_id}")
        
        # Update settings
        settings = DashboardService.save_settings(
            user_id=user_id,
            layout=data.get('layout'),
            widgets=data.get('widgets'),
            theme=data.get('theme'),
            language=data.get('language'),
            timezone=data.get('timezone'),
            validate=False  # Already validated above
        )
        
        logger.info(f"Dashboard settings updated successfully for user: {user_id}")
        return jsonify({
            'success': True,
            'message': 'Dashboard settings updated',
            'settings': settings.to_dict()
        }), 200
        
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Error updating dashboard settings: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update dashboard settings'
        }), 500


@dashboard_settings_bp.route('/reset', methods=['POST'])
@jwt_required()
def reset_dashboard_settings():
    """
    Reset user dashboard settings to defaults.
    
    Resets all dashboard customization settings to their default values.
    
    Returns:
        200: Reset settings object
        401: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"--- Reset Dashboard Settings branch started for user: {user_id} ---")
        settings = DashboardService.reset_to_defaults(user_id)
        
        logger.info(f"Dashboard settings reset to defaults for user: {user_id}")
        return jsonify({
            'success': True,
            'message': 'Dashboard settings reset to defaults',
            'settings': settings.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error resetting dashboard settings: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to reset dashboard settings'
        }), 500


# ==================== Widget Endpoints ====================

@dashboard_settings_bp.route('/widgets', methods=['GET'])
@jwt_required()
def get_available_widgets():
    """
    Get list of available widget types.
    
    Returns all available widget types that can be added to the dashboard.
    
    Returns:
        200: List of widget types
        401: Unauthorized
    """
    try:
        logger.info("--- Get Available Widgets branch started ---")
        widgets = DashboardService.get_available_widgets()
        
        logger.info(f"Successfully retrieved {len(widgets)} available widgets")
        return jsonify({
            'success': True,
            'widgets': widgets
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting available widgets: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve available widgets'
        }), 500


@dashboard_settings_bp.route('/widgets', methods=['POST'])
@jwt_required()
def add_widget():
    """
    Add a widget to the user's dashboard.
    
    Request Body:
        {
            "type": "form_statistics",  // Widget type ID
            "position": {"x": 0, "y": 4}, // Optional position
            "size": {"w": 2, "h": 2},     // Optional size
            "config": {...}               // Optional widget config
        }
    
    Returns:
        201: Added widget object
        400: Validation error
        401: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"--- Add Widget branch started for user: {user_id} ---")
        data = request.get_json()
        
        if not data:
            logger.warning(f"Add widget failed: Missing request body for user: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        if 'type' not in data:
            logger.warning(f"Add widget failed: Missing widget type for user: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Widget type is required'
            }), 400
        
        widget = DashboardService.add_widget(
            user_id=user_id,
            widget_type=data['type'],
            position=data.get('position'),
            size=data.get('size'),
            config=data.get('config')
        )
        
        logger.info(f"Widget (type: {data['type']}) added successfully for user: {user_id}")
        return jsonify({
            'success': True,
            'message': 'Widget added successfully',
            'widget': widget
        }), 201
        
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Error adding widget: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to add widget'
        }), 500


@dashboard_settings_bp.route('/widgets/<widget_id>', methods=['DELETE'])
@jwt_required()
def remove_widget(widget_id):
    """
    Remove a widget from the user's dashboard.
    
    Args:
        widget_id: ID of the widget to remove
    
    Returns:
        200: Success message
        404: Widget not found
        401: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"--- Remove Widget branch started for widget_id: {widget_id} (user: {user_id}) ---")
        removed = DashboardService.remove_widget(user_id, widget_id)
        
        if not removed:
            logger.warning(f"Remove widget failed: Widget {widget_id} not found for user: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Widget not found'
            }), 404
        
        logger.info(f"Widget {widget_id} removed successfully for user: {user_id}")
        return jsonify({
            'success': True,
            'message': 'Widget removed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error removing widget: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to remove widget'
        }), 500


@dashboard_settings_bp.route('/widgets/<widget_id>', methods=['PUT'])
@jwt_required()
def update_widget(widget_id):
    """
    Update a widget's configuration.
    
    Args:
        widget_id: ID of the widget to update
    
    Request Body:
        {
            "position": {"x": 0, "y": 4},  // Optional new position
            "size": {"w": 2, "h": 2},      // Optional new size
            "config": {...},               // Optional config updates
            "is_visible": true             // Optional visibility
        }
    
    Returns:
        200: Updated widget object
        404: Widget not found
        401: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"--- Update Widget branch started for widget_id: {widget_id} (user: {user_id}) ---")
        data = request.get_json()
        
        if not data:
            logger.warning(f"Update widget failed: Missing request body for user: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        widget = DashboardService.update_widget(
            user_id=user_id,
            widget_id=widget_id,
            position=data.get('position'),
            size=data.get('size'),
            config=data.get('config'),
            is_visible=data.get('is_visible')
        )
        
        if not widget:
            logger.warning(f"Update widget failed: Widget {widget_id} not found for user: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Widget not found'
            }), 404
        
        logger.info(f"Widget {widget_id} updated successfully for user: {user_id}")
        return jsonify({
            'success': True,
            'message': 'Widget updated successfully',
            'widget': widget
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating widget: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update widget'
        }), 500


@dashboard_settings_bp.route('/widgets/positions', methods=['PUT'])
@jwt_required()
def update_widget_positions():
    """
    Update positions for multiple widgets.
    
    Used for drag-and-drop reordering of widgets.
    
    Request Body:
        {
            "positions": {
                "widget_id_1": {"x": 0, "y": 0},
                "widget_id_2": {"x": 2, "y": 0}
            }
        }
    
    Returns:
        200: List of updated widgets
        400: Validation error
        401: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"--- Update Widget Positions branch started for user: {user_id} ---")
        data = request.get_json()
        
        if not data or 'positions' not in data:
            logger.warning(f"Update positions failed: Missing data or 'positions' key for user: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Positions data is required'
            }), 400
        
        positions = data['positions']
        
        if not isinstance(positions, dict):
            logger.warning(f"Update positions failed: 'positions' is not a dictionary for user: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Positions must be a dictionary'
            }), 400
        
        updated = DashboardService.update_widget_positions(user_id, positions)
        
        logger.info(f"Successfully updated positions for {len(updated)} widgets (user: {user_id})")
        return jsonify({
            'success': True,
            'message': f'Updated positions for {len(updated)} widgets',
            'updated_widgets': updated
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating widget positions: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update widget positions'
        }), 500


@dashboard_settings_bp.route('/layout', methods=['PUT'])
@jwt_required()
def update_layout():
    """
    Update only the layout configuration.
    
    Request Body:
        {
            "columns": 4,
            "rowHeight": 120,
            "margin": [15, 15],
            "compactType": "vertical",
            "positions": {
                "widget_id_1": {"x": 0, "y": 0}
            }
        }
    
    Returns:
        200: Updated settings object
        400: Validation error
        401: Unauthorized
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"--- Update Layout branch started for user: {user_id} ---")
        data = request.get_json()
        
        if not data:
            logger.warning(f"Update layout failed: Missing request body for user: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Validate layout
        logger.debug(f"Validating layout for user: {user_id}")
        validation_result = DashboardService.validate_settings({'layout': data})
        if not validation_result['valid']:
            logger.warning(f"Layout validation failed for user: {user_id}: {validation_result['errors']}")
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': validation_result['errors']
            }), 400
        logger.debug(f"Layout validation successful for user: {user_id}")
        
        settings = DashboardService.save_settings(
            user_id=user_id,
            layout=data,
            validate=False
        )
        
        logger.info(f"Layout updated successfully for user: {user_id}")
        return jsonify({
            'success': True,
            'message': 'Layout updated',
            'settings': settings.to_dict()
        }), 200
        
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Error updating layout: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update layout'
        }), 500
