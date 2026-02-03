from mongoengine import Document, StringField, IntField, DateTimeField, DictField
from datetime import datetime, timezone


class WebhookLog(Document):
    """
    Model for tracking webhook delivery attempts and failures.
    Stores logs of all webhook calls with retry information.
    """
    meta = {
        'collection': 'webhook_logs',
        'indexes': [
            'url',
            'status',
            'created_at',
            'last_attempt',
            ('url', 'status'),
            ('status', 'created_at')
        ]
    }
    
    # Target webhook URL
    url = StringField(required=True)
    
    # Payload sent to the webhook
    payload = DictField(required=True)
    
    # Delivery status: pending, success, failed, retrying
    status = StringField(
        required=True,
        choices=('pending', 'success', 'failed', 'retrying'),
        default='pending'
    )
    
    # Number of delivery attempts made
    attempt_count = IntField(default=0, min_value=0)
    
    # Timestamp of the last attempt
    last_attempt = DateTimeField()
    
    # Error message from the last failed attempt (if any)
    error_message = StringField()
    
    # HTTP status code from the last attempt (if any)
    status_code = IntField()
    
    # Timestamp when the webhook log was created
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    # Additional metadata (headers, response body, etc.)
    metadata = DictField()
