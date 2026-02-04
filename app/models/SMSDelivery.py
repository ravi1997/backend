"""
SMS Delivery Model

MongoEngine model for tracking SMS delivery status and history.
"""

from mongoengine import Document, StringField, IntField, DateTimeField, DictField, FloatField, UUIDField, BooleanField
from datetime import datetime, timezone
import uuid


class SMSDelivery(Document):
    """
    Model for tracking SMS delivery attempts with retry logic and failure logging.
    
    This collection stores comprehensive delivery tracking information including:
    - Delivery status (pending, sent, delivered, failed)
    - Retry attempt tracking with exponential backoff
    - Provider response details
    - Cost tracking
    """
    
    meta = {
        'collection': 'sms_deliveries',
        'indexes': [
            'sms_id',
            'form_id',
            'recipient_number',
            'provider',
            'status',
            'created_at',
            'sent_at',
            'delivered_at',
            ('provider', 'status'),
            ('form_id', 'status'),
            ('recipient_number', 'status'),
            ('sms_id', 'provider'),
            'created_at'
        ]
    }
    
    # Unique identifier for this SMS delivery
    sms_id = UUIDField(primary_key=True, binary=False, default=uuid.uuid4)
    
    # Reference to the form that triggered this SMS (optional)
    form_id = StringField()
    
    # Reference to the webhook/action that triggered this SMS (optional)
    webhook_id = StringField()
    
    # Recipient phone number (E.164 format)
    recipient_number = StringField(required=True)
    
    # SMS message content
    message = StringField(required=True)
    
    # Delivery status: pending, sent, delivered, failed
    status = StringField(
        required=True,
        choices=('pending', 'sent', 'delivered', 'failed'),
        default='pending'
    )
    
    # SMS provider used
    provider = StringField(
        required=True,
        choices=('twilio', 'sns', 'aws_sns', 'local_mock')
    )
    
    # Provider configuration ID used
    provider_config_id = StringField()
    
    # Provider's message ID (for status tracking)
    provider_message_id = StringField()
    
    # Number of delivery attempts made
    attempt_count = IntField(default=0, min_value=0)
    
    # Maximum number of retry attempts allowed
    max_retries = IntField(default=3, min_value=0)
    
    # When to schedule the next retry attempt
    next_retry_at = DateTimeField()
    
    # Timestamp when the SMS was sent
    sent_at = DateTimeField()
    
    # Timestamp when the SMS was delivered (if known)
    delivered_at = DateTimeField()
    
    # User who triggered this SMS
    created_by = StringField()
    
    # Error message from the last failed attempt (if any)
    error_message = StringField()
    
    # Error code from the provider
    error_code = StringField()
    
    # Cost of the SMS (in provider's currency)
    cost = FloatField()
    
    # Currency code
    currency = StringField(default='USD')
    
    # Additional metadata (provider response, etc.)
    metadata = DictField()
    
    # Timestamp when the SMS delivery record was created
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    # Timestamp when the SMS delivery was completed/failed
    completed_at = DateTimeField()
    
    # Whether this SMS can be retried
    retryable = BooleanField(default=True)
    
    def to_dict(self) -> dict:
        """
        Convert the SMSDelivery document to a dictionary.
        
        Returns:
            Dictionary representation of the SMS delivery
        """
        return {
            'sms_id': str(self.sms_id),
            'form_id': self.form_id,
            'webhook_id': self.webhook_id,
            'recipient_number': self.recipient_number,
            'message': self.message,
            'status': self.status,
            'provider': self.provider,
            'provider_config_id': self.provider_config_id,
            'provider_message_id': self.provider_message_id,
            'attempt_count': self.attempt_count,
            'max_retries': self.max_retries,
            'next_retry_at': self.next_retry_at.isoformat() if self.next_retry_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'created_by': self.created_by,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'cost': self.cost,
            'currency': self.currency,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'retryable': self.retryable
        }
    
    def is_retryable(self) -> bool:
        """
        Check if this SMS delivery is eligible for retry.
        
        Returns:
            True if the delivery can be retried, False otherwise
        """
        return (
            self.status == 'failed' and
            self.attempt_count < self.max_retries and
            self.retryable
        )
    
    def is_completed(self) -> bool:
        """
        Check if this SMS delivery has completed (delivered or failed).
        
        Returns:
            True if the delivery is complete, False otherwise
        """
        return self.status in ['delivered', 'failed']
    
    def mark_sent(self, provider_message_id: str = None, sent_at: datetime = None):
        """
        Mark the SMS as sent.
        
        Args:
            provider_message_id: Provider's message ID
            sent_at: When the SMS was sent
        """
        self.status = 'sent'
        self.attempt_count += 1
        self.sent_at = sent_at or datetime.now(timezone.utc)
        if provider_message_id:
            self.provider_message_id = provider_message_id
    
    def mark_delivered(self):
        """Mark the SMS as delivered."""
        self.status = 'delivered'
        self.delivered_at = datetime.now(timezone.utc)
        self.completed_at = datetime.now(timezone.utc)
    
    def mark_failed(self, error_message: str, error_code: str = None):
        """
        Mark the SMS as failed.
        
        Args:
            error_message: Error message
            error_code: Error code
        """
        self.status = 'failed'
        self.error_message = error_message
        self.error_code = error_code
        self.completed_at = datetime.now(timezone.utc)
        
        # Not retryable if max retries reached
        if self.attempt_count >= self.max_retries:
            self.retryable = False
    
    def schedule_retry(self, next_retry_at: datetime):
        """
        Schedule a retry for this SMS.
        
        Args:
            next_retry_at: When to retry
        """
        self.next_retry_at = next_retry_at
        self.status = 'pending'
