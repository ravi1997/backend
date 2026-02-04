from mongoengine import Document, StringField, IntField, DateTimeField, DictField, UUIDField
from datetime import datetime, timezone
import uuid


class WebhookDelivery(Document):
    """
    Model for tracking webhook delivery attempts with retry logic and failure logging.
    
    This collection stores comprehensive delivery tracking information including:
    - Delivery status (pending, in_progress, success, failed, retrying, cancelled)
    - Retry attempt tracking with exponential backoff
    - Response details (status code, body, error messages)
    - Next retry scheduling
    """
    meta = {
        'collection': 'webhook_deliveries',
        'indexes': [
            'webhook_id',
            'url',
            'form_id',
            'status',
            'created_at',
            'last_attempt_at',
            'next_retry_at',
            'created_by',
            ('webhook_id', 'status'),
            ('form_id', 'status'),
            ('status', 'next_retry_at'),
            ('webhook_id', 'created_at'),
            ('form_id', 'created_at')
        ]
    }
    
    # Unique identifier for this delivery record
    id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    
    # Reference to the webhook configuration (stored as string for flexibility)
    webhook_id = StringField(required=True)
    
    # Target webhook URL
    url = StringField(required=True)
    
    # Reference to the form that triggered this webhook
    form_id = StringField(required=True)
    
    # Payload sent to the webhook
    payload = DictField(required=True)
    
    # Delivery status: pending, in_progress, success, failed, retrying, cancelled
    status = StringField(
        required=True,
        choices=('pending', 'in_progress', 'success', 'failed', 'retrying', 'cancelled'),
        default='pending'
    )
    
    # Number of delivery attempts made
    attempt_count = IntField(default=0, min_value=0)
    
    # Maximum number of retry attempts allowed
    max_retries = IntField(default=5, min_value=0)
    
    # Timestamp of the last attempt
    last_attempt_at = DateTimeField()
    
    # When to schedule the next retry attempt
    next_retry_at = DateTimeField()
    
    # User who created/triggered this webhook delivery
    created_by = StringField(required=True)
    
    # HTTP status code from the last attempt (if any)
    response_code = IntField()
    
    # Response body from the last attempt (limited size)
    response_body = StringField()
    
    # Error message from the last failed attempt (if any)
    error_message = StringField()
    
    # Additional metadata (headers, retry schedule, etc.)
    metadata = DictField()
    
    # Timestamp when the webhook delivery record was created
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    # Timestamp when the webhook delivery was completed/failed/cancelled
    completed_at = DateTimeField()
    
    def to_dict(self) -> dict:
        """
        Convert the WebhookDelivery document to a dictionary.
        
        Returns:
            Dictionary representation of the webhook delivery
        """
        return {
            'id': str(self.id),
            'webhook_id': self.webhook_id,
            'url': self.url,
            'form_id': self.form_id,
            'payload': self.payload,
            'status': self.status,
            'attempt_count': self.attempt_count,
            'max_retries': self.max_retries,
            'last_attempt_at': self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            'next_retry_at': self.next_retry_at.isoformat() if self.next_retry_at else None,
            'created_by': self.created_by,
            'response_code': self.response_code,
            'response_body': self.response_body,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def is_retryable(self) -> bool:
        """
        Check if this webhook delivery is eligible for retry.
        
        Returns:
            True if the delivery can be retried, False otherwise
        """
        return (
            self.status in ['failed', 'retrying'] and
            self.attempt_count < self.max_retries
        )
    
    def is_completed(self) -> bool:
        """
        Check if this webhook delivery has completed (success, failed, or cancelled).
        
        Returns:
            True if the delivery is complete, False otherwise
        """
        return self.status in ['success', 'failed', 'cancelled']
