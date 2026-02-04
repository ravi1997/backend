from datetime import datetime, timezone
import uuid
from mongoengine import Document, StringField, DateTimeField, DictField
from mongoengine import UUIDField
import json

class UserDashboardSettings(Document):
    """
    User-specific dashboard customization settings.
    Stores user preferences for dashboard layout, widgets, theme, etc.
    """
    meta = {
        'collection': 'user_dashboard_settings',
        'indexes': [
            {'fields': ['user_id'], 'unique': True}
        ]
    }
    
    user_id = StringField(required=True)
    
    # Layout configuration (JSON)
    # Example: {"columns": 3, "rowHeight": 100, "margin": [10, 10], "compactType": "vertical"}
    layout = DictField(default=lambda: {
        "columns": 3,
        "rowHeight": 100,
        "margin": [10, 10],
        "compactType": "vertical",
        "positions": {}
    })
    
    # Widgets configuration (JSON)
    # Array of widget objects with id, type, position, size, config
    widgets = DictField(default=list)
    
    # Theme preferences
    theme = StringField(choices=('light', 'dark', 'system'), default='system')
    
    # Language preference
    language = StringField(default='en')
    
    # Timezone preference
    timezone = StringField(default='UTC')
    
    # Timestamps
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def save(self, *args, **kwargs):
        """Override save to update timestamp."""
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def to_dict(self):
        """Convert settings to dictionary for API responses."""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'layout': self.layout,
            'widgets': self.widgets,
            'theme': self.theme,
            'language': self.language,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def reset_to_defaults(self):
        """Reset settings to default values."""
        self.layout = {
            "columns": 3,
            "rowHeight": 100,
            "margin": [10, 10],
            "compactType": "vertical",
            "positions": {}
        }
        self.widgets = []
        self.theme = 'system'
        self.language = 'en'
        self.timezone = 'UTC'
        self.updated_at = datetime.now(timezone.utc)
        return self.save()


# ==================== Widget Types and Available Widgets ====================

# Available widget types for the dashboard
WIDGET_TYPES = {
    'form_statistics': {
        'id': 'form_statistics',
        'name': 'Form Statistics',
        'description': 'Display statistics about your forms',
        'icon': '📊',
        'default_size': {'w': 2, 'h': 2},
        'config_schema': {
            'forms_to_show': {'type': 'number', 'default': 5},
            'show_submission_count': {'type': 'boolean', 'default': True},
            'show_completion_rate': {'type': 'boolean', 'default': True}
        }
    },
    'recent_responses': {
        'id': 'recent_responses',
        'name': 'Recent Responses',
        'description': 'Show recent form responses',
        'icon': '📋',
        'default_size': {'w': 2, 'h': 3},
        'config_schema': {
            'form_id': {'type': 'string', 'default': None},
            'limit': {'type': 'number', 'default': 10},
            'show_data_preview': {'type': 'boolean', 'default': True}
        }
    },
    'quick_actions': {
        'id': 'quick_actions',
        'name': 'Quick Actions',
        'description': 'Quick access to common actions',
        'icon': '⚡',
        'default_size': {'w': 1, 'h': 2},
        'config_schema': {
            'actions': {
                'type': 'array',
                'default': [
                    {'id': 'create_form', 'label': 'Create Form', 'icon': '➕'},
                    {'id': 'view_responses', 'label': 'View Responses', 'icon': '👁️'},
                    {'id': 'export_data', 'label': 'Export Data', 'icon': '📤'}
                ]
            }
        }
    },
    'notifications': {
        'id': 'notifications',
        'name': 'Notifications',
        'description': 'Show recent notifications',
        'icon': '🔔',
        'default_size': {'w': 1, 'h': 2},
        'config_schema': {
            'limit': {'type': 'number', 'default': 5},
            'show_read': {'type': 'boolean', 'default': True}
        }
    },
    'charts': {
        'id': 'charts',
        'name': 'Charts',
        'description': 'Display charts and analytics',
        'icon': '📈',
        'default_size': {'w': 2, 'h': 2},
        'config_schema': {
            'chart_type': {'type': 'string', 'default': 'bar', 'options': ['bar', 'pie', 'line', 'doughnut']},
            'form_id': {'type': 'string', 'default': None},
            'x_field': {'type': 'string', 'default': None},
            'y_field': {'type': 'string', 'default': None},
            'aggregation': {'type': 'string', 'default': 'count', 'options': ['count', 'sum', 'avg', 'min', 'max']}
        }
    },
    'analytics_overview': {
        'id': 'analytics_overview',
        'name': 'Analytics Overview',
        'description': 'Overview of key analytics metrics',
        'icon': '📉',
        'default_size': {'w': 2, 'h': 1},
        'config_schema': {
            'metrics': {
                'type': 'array',
                'default': ['total_responses', 'completion_rate', 'avg_time']
            }
        }
    },
    'workflow_status': {
        'id': 'workflow_status',
        'name': 'Workflow Status',
        'description': 'Show status of active workflows',
        'icon': '🔄',
        'default_size': {'w': 1, 'h': 2},
        'config_schema': {
            'show_pending': {'type': 'boolean', 'default': True},
            'show_completed': {'type': 'boolean', 'default': True}
        }
    },
    'calendar': {
        'id': 'calendar',
        'name': 'Calendar',
        'description': 'Calendar view for scheduled forms',
        'icon': '📅',
        'default_size': {'w': 2, 'h': 3},
        'config_schema': {
            'form_id': {'type': 'string', 'default': None},
            'date_field': {'type': 'string', 'default': 'created_at'}
        }
    }
}


def get_available_widgets():
    """Return list of available widget types."""
    return [
        {
            'id': widget_id,
            'name': info['name'],
            'description': info['description'],
            'icon': info['icon'],
            'default_size': info['default_size'],
            'config_schema': info['config_schema']
        }
        for widget_id, info in WIDGET_TYPES.items()
    ]


def get_widget_by_id(widget_id):
    """Get a specific widget type by ID."""
    return WIDGET_TYPES.get(widget_id)


def create_default_widgets():
    """Create default widgets for new users."""
    return [
        {
            'id': str(uuid.uuid4()),
            'type': 'form_statistics',
            'name': 'Form Statistics',
            'position': {'x': 0, 'y': 0},
            'size': WIDGET_TYPES['form_statistics']['default_size'],
            'config': WIDGET_TYPES['form_statistics']['config_schema'],
            'is_visible': True
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'recent_responses',
            'name': 'Recent Responses',
            'position': {'x': 2, 'y': 0},
            'size': WIDGET_TYPES['recent_responses']['default_size'],
            'config': WIDGET_TYPES['recent_responses']['config_schema'],
            'is_visible': True
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'quick_actions',
            'name': 'Quick Actions',
            'position': {'x': 0, 'y': 2},
            'size': WIDGET_TYPES['quick_actions']['default_size'],
            'config': WIDGET_TYPES['quick_actions']['config_schema'],
            'is_visible': True
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'notifications',
            'name': 'Notifications',
            'position': {'x': 1, 'y': 2},
            'size': WIDGET_TYPES['notifications']['default_size'],
            'config': WIDGET_TYPES['notifications']['config_schema'],
            'is_visible': True
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'charts',
            'name': 'Response Charts',
            'position': {'x': 0, 'y': 4},
            'size': WIDGET_TYPES['charts']['default_size'],
            'config': WIDGET_TYPES['charts']['config_schema'],
            'is_visible': True
        }
    ]
