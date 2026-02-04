"""
SMS Provider Configuration Model

MongoEngine model for storing SMS provider configurations.
"""

from mongoengine import Document, StringField, BooleanField, DictField, DateTimeField, IntField
from datetime import datetime, timezone


class SMSProviderConfig(Document):
    """
    Model for storing SMS provider configurations.
    
    This collection stores provider settings that can be managed
    through the API without code changes.
    """
    
    meta = {
        'collection': 'sms_providers',
        'indexes': [
            'provider_id',
            'provider_name',
            'enabled',
            'provider_type',
            ('provider_id', 'enabled'),
            'created_at'
        ]
    }
    
    # Unique provider identifier
    provider_id = StringField(required=True, unique=True)
    
    # Human-readable provider name
    provider_name = StringField(required=True)
    
    # Provider type (twilio, sns, aws_sns, local_mock)
    provider_type = StringField(
        required=True,
        choices=('twilio', 'sns', 'aws_sns', 'local_mock')
    )
    
    # Whether this provider is enabled
    enabled = BooleanField(default=True)
    
    # Provider priority (lower = higher priority)
    priority = IntField(default=100, min_value=0)
    
    # Provider-specific configuration (encrypted/secrets handled separately)
    # Common fields:
    # - account_sid / aws_access_key_id
    # - auth_token / aws_secret_access_key
    # - from_number / sender_id
    # - messaging_service_sid
    # - aws_region
    config = DictField()
    
    # Description of the provider
    description = StringField()
    
    # Who created this provider configuration
    created_by = StringField()
    
    # Who last updated this configuration
    updated_by = StringField()
    
    # Timestamp when the provider was created
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    # Timestamp when the provider was last updated
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    # Whether this is the default provider
    is_default = BooleanField(default=False)
    
    # Rate limiting settings
    rate_limit_per_minute = IntField()
    rate_limit_per_hour = IntField()
    rate_limit_per_day = IntField()
    
    # Cost settings
    max_cost_per_message = IntField()  # in cents
    
    def to_dict(self) -> dict:
        """
        Convert the SMSProviderConfig document to a dictionary.
        
        Returns:
            Dictionary representation of the provider config
        """
        return {
            'provider_id': self.provider_id,
            'provider_name': self.provider_name,
            'provider_type': self.provider_type,
            'enabled': self.enabled,
            'priority': self.priority,
            'description': self.description,
            'config': self._get_masked_config(),
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_default': self.is_default,
            'rate_limit_per_minute': self.rate_limit_per_minute,
            'rate_limit_per_hour': self.rate_limit_per_hour,
            'rate_limit_per_day': self.rate_limit_per_day,
            'max_cost_per_message': self.max_cost_per_message
        }
    
    def _get_masked_config(self) -> dict:
        """
        Get the config with sensitive fields masked.
        
        Returns:
            Dictionary with sensitive fields masked
        """
        if not self.config:
            return {}
        
        masked = {}
        sensitive_keys = [
            'auth_token', 'aws_secret_access_key', 'api_key', 'api_secret',
            'secret', 'password', 'token', 'private_key'
        ]
        
        for key, value in self.config.items():
            if any(s in key.lower() for s in sensitive_keys):
                masked[key] = '***MASKED***'
            else:
                masked[key] = value
        
        return masked
    
    def get_full_config(self) -> dict:
        """
        Get the full configuration (including secrets).
        
        WARNING: This returns sensitive data. Use with caution.
        
        Returns:
            Full configuration dictionary
        """
        return self.config or {}
    
    def is_available(self) -> bool:
        """
        Check if the provider is available for use.
        
        Returns:
            True if enabled and configured
        """
        return self.enabled and bool(self.config)
    
    def update_config(self, new_config: dict, updated_by: str = None):
        """
        Update the provider configuration.
        
        Args:
            new_config: New configuration values
            updated_by: User who made the update
        """
        # Merge with existing config, preserving masked values if not provided
        if self.config:
            for key in self.config:
                if key in new_config and '***MASKED***' in str(new_config.get(key)):
                    new_config[key] = self.config.get(key)
        
        self.config = new_config
        self.updated_by = updated_by
        self.updated_at = datetime.now(timezone.utc)
    
    def enable(self):
        """Enable this provider."""
        self.enabled = True
        self.updated_at = datetime.now(timezone.utc)
    
    def disable(self):
        """Disable this provider."""
        self.enabled = False
        self.updated_at = datetime.now(timezone.utc)
