"""
Dashboard Service for user dashboard customization persistence.

This service handles:
- Saving user dashboard settings
- Retrieving user dashboard settings
- Providing default settings for new users
- Validating settings structure
- Managing widgets (add, remove, update)
"""
import logging
from datetime import datetime, timezone
import uuid
from typing import Dict, List, Any, Optional

from app.models.UserDashboardSettings import (
    UserDashboardSettings,
    WIDGET_TYPES,
    get_available_widgets,
    get_widget_by_id,
    create_default_widgets
)

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Service class for managing user dashboard settings and customization.
    """
    
    @staticmethod
    def get_settings(user_id: str) -> Optional[UserDashboardSettings]:
        """
        Get dashboard settings for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            UserDashboardSettings object or None if not found
        """
        try:
            settings = UserDashboardSettings.objects(user_id=user_id).first()
            return settings
        except Exception as e:
            logger.error(f"Error retrieving dashboard settings for user {user_id}: {e}")
            raise
    
    @staticmethod
    def get_or_create_settings(user_id: str) -> UserDashboardSettings:
        """
        Get existing settings or create default settings for a new user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            UserDashboardSettings object
        """
        try:
            settings = UserDashboardSettings.objects(user_id=user_id).first()
            if not settings:
                settings = DashboardService.create_default_settings(user_id)
            return settings
        except Exception as e:
            logger.error(f"Error getting/creating dashboard settings for user {user_id}: {e}")
            raise
    
    @staticmethod
    def create_default_settings(user_id: str) -> UserDashboardSettings:
        """
        Create default dashboard settings for a new user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Newly created UserDashboardSettings object
        """
        try:
            settings = UserDashboardSettings(
                user_id=user_id,
                layout={
                    "columns": 3,
                    "rowHeight": 100,
                    "margin": [10, 10],
                    "compactType": "vertical",
                    "positions": {}
                },
                widgets=create_default_widgets(),
                theme='system',
                language='en',
                timezone='UTC'
            )
            settings.save()
            logger.info(f"Created default dashboard settings for user {user_id}")
            return settings
        except Exception as e:
            logger.error(f"Error creating default dashboard settings for user {user_id}: {e}")
            raise
    
    @staticmethod
    def save_settings(
        user_id: str,
        layout: Optional[Dict] = None,
        widgets: Optional[List[Dict]] = None,
        theme: Optional[str] = None,
        language: Optional[str] = None,
        timezone: Optional[str] = None,
        validate: bool = True
    ) -> UserDashboardSettings:
        """
        Save dashboard settings for a user.
        
        Args:
            user_id: The user's ID
            layout: Dashboard layout configuration
            widgets: List of widget configurations
            theme: Theme preference (light/dark/system)
            language: Language preference
            timezone: Timezone preference
            validate: Whether to validate the settings structure
            
        Returns:
            Updated UserDashboardSettings object
        """
        try:
            settings = DashboardService.get_or_create_settings(user_id)
            
            if layout is not None:
                if validate:
                    DashboardService._validate_layout(layout)
                settings.layout = layout
            
            if widgets is not None:
                if validate:
                    DashboardService._validate_widgets(widgets)
                settings.widgets = widgets
            
            if theme is not None:
                DashboardService._validate_theme(theme)
                settings.theme = theme
            
            if language is not None:
                settings.language = language
            
            if timezone is not None:
                settings.timezone = timezone
            
            settings.save()
            logger.info(f"Saved dashboard settings for user {user_id}")
            return settings
        except Exception as e:
            logger.error(f"Error saving dashboard settings for user {user_id}: {e}")
            raise
    
    @staticmethod
    def reset_to_defaults(user_id: str) -> UserDashboardSettings:
        """
        Reset user's dashboard settings to defaults.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Reset UserDashboardSettings object
        """
        try:
            settings = DashboardService.get_or_create_settings(user_id)
            settings.reset_to_defaults()
            logger.info(f"Reset dashboard settings to defaults for user {user_id}")
            return settings
        except Exception as e:
            logger.error(f"Error resetting dashboard settings for user {user_id}: {e}")
            raise
    
    @staticmethod
    def add_widget(user_id: str, widget_type: str, position: Optional[Dict] = None, 
                   size: Optional[Dict] = None, config: Optional[Dict] = None) -> Dict:
        """
        Add a widget to the user's dashboard.
        
        Args:
            user_id: The user's ID
            widget_type: Type of widget to add
            position: Widget position {x, y}
            size: Widget size {w, h}
            config: Widget-specific configuration
            
        Returns:
            Added widget object
        """
        try:
            # Validate widget type
            widget_info = get_widget_by_id(widget_type)
            if not widget_info:
                raise ValueError(f"Invalid widget type: {widget_type}")
            
            settings = DashboardService.get_or_create_settings(user_id)
            
            # Get next position
            widgets = settings.widgets or []
            if position is None:
                position = DashboardService._get_next_position(widgets)
            
            # Use default size if not provided
            if size is None:
                size = widget_info['default_size']
            
            # Get default config
            if config is None:
                config = {}
                for key, schema in widget_info['config_schema'].items():
                    if 'default' in schema:
                        config[key] = schema['default']
            
            new_widget = {
                'id': str(uuid.uuid4()),
                'type': widget_type,
                'name': widget_info['name'],
                'position': position,
                'size': size,
                'config': config,
                'is_visible': True
            }
            
            widgets.append(new_widget)
            settings.widgets = widgets
            settings.save()
            
            logger.info(f"Added widget {widget_type} to dashboard for user {user_id}")
            return new_widget
        except Exception as e:
            logger.error(f"Error adding widget {widget_type} for user {user_id}: {e}")
            raise
    
    @staticmethod
    def remove_widget(user_id: str, widget_id: str) -> bool:
        """
        Remove a widget from the user's dashboard.
        
        Args:
            user_id: The user's ID
            widget_id: ID of the widget to remove
            
        Returns:
            True if widget was removed, False if not found
        """
        try:
            settings = DashboardService.get_or_create_settings(user_id)
            widgets = settings.widgets or []
            
            original_count = len(widgets)
            widgets = [w for w in widgets if w.get('id') != widget_id]
            
            if len(widgets) == original_count:
                logger.warning(f"Widget {widget_id} not found for user {user_id}")
                return False
            
            settings.widgets = widgets
            settings.save()
            
            logger.info(f"Removed widget {widget_id} from dashboard for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing widget {widget_id} for user {user_id}: {e}")
            raise
    
    @staticmethod
    def update_widget(user_id: str, widget_id: str, 
                     position: Optional[Dict] = None,
                     size: Optional[Dict] = None,
                     config: Optional[Dict] = None,
                     is_visible: Optional[bool] = None) -> Optional[Dict]:
        """
        Update a widget's configuration.
        
        Args:
            user_id: The user's ID
            widget_id: ID of the widget to update
            position: New position {x, y}
            size: New size {w, h}
            config: New configuration
            is_visible: Visibility status
            
        Returns:
            Updated widget object or None if not found
        """
        try:
            settings = DashboardService.get_or_create_settings(user_id)
            widgets = settings.widgets or []
            
            for widget in widgets:
                if widget.get('id') == widget_id:
                    if position is not None:
                        widget['position'] = position
                    if size is not None:
                        widget['size'] = size
                    if config is not None:
                        widget['config'].update(config)
                    if is_visible is not None:
                        widget['is_visible'] = is_visible
                    
                    settings.widgets = widgets
                    settings.save()
                    
                    logger.info(f"Updated widget {widget_id} for user {user_id}")
                    return widget
            
            logger.warning(f"Widget {widget_id} not found for user {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating widget {widget_id} for user {user_id}: {e}")
            raise
    
    @staticmethod
    def update_widget_positions(user_id: str, positions: Dict[str, Dict]) -> List[Dict]:
        """
        Update positions for multiple widgets.
        
        Args:
            user_id: The user's ID
            positions: Dict mapping widget_id to position {x, y}
            
        Returns:
            List of updated widgets
        """
        try:
            settings = DashboardService.get_or_create_settings(user_id)
            widgets = settings.widgets or []
            updated = []
            
            for widget in widgets:
                widget_id = widget.get('id')
                if widget_id in positions:
                    widget['position'] = positions[widget_id]
                    updated.append(widget)
            
            settings.save()
            
            logger.info(f"Updated positions for {len(updated)} widgets for user {user_id}")
            return updated
        except Exception as e:
            logger.error(f"Error updating widget positions for user {user_id}: {e}")
            raise
    
    @staticmethod
    def get_available_widgets() -> List[Dict]:
        """
        Get list of available widget types.
        
        Returns:
            List of widget type definitions
        """
        return get_available_widgets()
    
    @staticmethod
    def get_widget_types() -> Dict:
        """
        Get all widget type definitions.
        
        Returns:
            Dict of widget type definitions
        """
        return WIDGET_TYPES
    
    # ==================== Validation Methods ====================
    
    @staticmethod
    def _validate_layout(layout: Dict) -> None:
        """Validate layout configuration."""
        if not isinstance(layout, dict):
            raise ValueError("Layout must be a dictionary")
        
        valid_keys = {'columns', 'rowHeight', 'margin', 'compactType', 'positions'}
        for key in layout.keys():
            if key not in valid_keys:
                raise ValueError(f"Invalid layout key: {key}")
        
        if 'columns' in layout:
            if not isinstance(layout['columns'], int) or layout['columns'] < 1:
                raise ValueError("Layout columns must be a positive integer")
    
    @staticmethod
    def _validate_widgets(widgets: List[Dict]) -> None:
        """Validate widget configurations."""
        if not isinstance(widgets, list):
            raise ValueError("Widgets must be a list")
        
        for i, widget in enumerate(widgets):
            if not isinstance(widget, dict):
                raise ValueError(f"Widget at index {i} must be a dictionary")
            
            if 'id' not in widget:
                raise ValueError(f"Widget at index {i} must have an 'id' field")
            
            if 'type' not in widget:
                raise ValueError(f"Widget at index {i} must have a 'type' field")
            
            widget_type = widget['type']
            if widget_type not in WIDGET_TYPES:
                raise ValueError(f"Invalid widget type: {widget_type}")
    
    @staticmethod
    def _validate_theme(theme: str) -> None:
        """Validate theme preference."""
        valid_themes = {'light', 'dark', 'system'}
        if theme not in valid_themes:
            raise ValueError(f"Invalid theme: {theme}. Must be one of {valid_themes}")
    
    @staticmethod
    def _get_next_position(widgets: List[Dict]) -> Dict:
        """Calculate next widget position based on existing widgets."""
        if not widgets:
            return {'x': 0, 'y': 0}
        
        max_y = 0
        for widget in widgets:
            pos = widget.get('position', {})
            y = pos.get('y', 0) + widget.get('size', {}).get('h', 2)
            if y > max_y:
                max_y = y
        
        return {'x': 0, 'y': max_y}
    
    @staticmethod
    def validate_settings(settings: Dict) -> Dict:
        """
        Validate a complete settings object.
        
        Args:
            settings: Settings dictionary to validate
            
        Returns:
            Validation result with 'valid' flag and any errors
        """
        errors = []
        
        if 'layout' in settings:
            try:
                DashboardService._validate_layout(settings['layout'])
            except ValueError as e:
                errors.append(f"Layout validation error: {str(e)}")
        
        if 'widgets' in settings:
            try:
                DashboardService._validate_widgets(settings['widgets'])
            except ValueError as e:
                errors.append(f"Widgets validation error: {str(e)}")
        
        if 'theme' in settings:
            try:
                DashboardService._validate_theme(settings['theme'])
            except ValueError as e:
                errors.append(f"Theme validation error: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
