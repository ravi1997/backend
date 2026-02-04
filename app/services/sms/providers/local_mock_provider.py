"""
Local Mock SMS Provider

This module provides a mock SMS provider for testing purposes.
It simulates SMS sending without actually sending messages.
"""

import re
import uuid
import random
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.services.sms.providers import (
    SMSProvider,
    SMSProviderType,
    SMSResult,
    SMSStatus,
    PhoneNumberValidation,
    SMSProviderError
)


class LocalMockProvider(SMSProvider):
    """
    Local Mock SMS provider for testing.
    
    This provider simulates SMS sending and status checking
    without making actual API calls. It's useful for:
    - Unit testing
    - Development without real SMS credentials
    - CI/CD pipelines
    
    Configuration options:
    - delay: Simulated delay in seconds (default: 0.1)
    - failure_rate: Percentage of messages that fail (default: 0)
    - success_status: Always return this status (optional)
    """
    
    provider_type = SMSProviderType.LOCAL_MOCK
    
    # Class-level storage for sent messages (for testing verification)
    _sent_messages: List[Dict[str, Any]] = []
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the mock provider.
        
        Args:
            config: Mock configuration (optional)
        """
        self.config = config or {}
        self.delay = self.config.get('delay', 0.1)  # seconds
        self.failure_rate = self.config.get('failure_rate', 0)  # 0% failure rate
        self.success_status = self.config.get('success_status')  # Force a specific status
        self._initialized = True
        self._provider_id = str(uuid.uuid4())
        
        # Clear sent messages on new instance if configured
        if self.config.get('clear_on_init', False):
            LocalMockProvider._sent_messages = []
    
    def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
        **kwargs
    ) -> SMSResult:
        """
        Simulate sending an SMS.
        
        Args:
            to: Recipient phone number
            message: SMS message content
            from_number: Sender phone number
            **kwargs: Additional parameters
            
        Returns:
            SMSResult with delivery status
        """
        try:
            # Validate the phone number
            validation = self.validate_number(to)
            if not validation.is_valid:
                return SMSResult(
                    success=False,
                    error_message=f"Invalid phone number: {validation.error_message}"
                )
            
            # Simulate network delay
            time.sleep(self.delay)
            
            # Simulate random failures based on failure_rate
            if random.random() < self.failure_rate:
                return SMSResult(
                    success=False,
                    error_message="Simulated failure",
                    provider_response={
                        'error_code': 'MockFailure',
                        'error_message': 'This is a simulated failure for testing'
                    }
                )
            
            # Generate a mock message ID
            message_id = f"mock_{uuid.uuid4().hex[:16]}"
            
            # Determine status
            if self.success_status:
                status = SMSStatus(self.success_status)
            else:
                # Randomly decide if delivered immediately
                status = SMSStatus.DELIVERED if random.random() > 0.3 else SMSStatus.SENT
            
            # Store the message for testing verification
            msg_record = {
                'message_id': message_id,
                'to': to,
                'from': from_number,
                'message': message,
                'status': status.value,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'provider_id': self._provider_id
            }
            LocalMockProvider._sent_messages.append(msg_record)
            
            return SMSResult(
                success=True,
                message_id=message_id,
                status=status,
                provider_response={
                    'mock_provider_id': self._provider_id,
                    'message_id': message_id,
                    'recipient': validation.formatted_number,
                    'sender': from_number,
                    'message_length': len(message),
                    'timestamp': msg_record['timestamp']
                },
                cost=0.0  # Mock SMS is free
            )
            
        except Exception as e:
            return SMSResult(
                success=False,
                error_message=str(e),
                provider_response={'error': str(e)}
            )
    
    def validate_number(self, phone_number: str) -> PhoneNumberValidation:
        """
        Validate a phone number.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            PhoneNumberValidation with validation results
        """
        try:
            # Basic E.164 validation
            e164_pattern = r'^\+[1-9]\d{1,14}$'
            
            if re.match(e164_pattern, phone_number):
                return PhoneNumberValidation(
                    is_valid=True,
                    formatted_number=phone_number,
                    country_code=phone_number[1:2],
                    national_number=phone_number[2:]
                )
            
            # Clean and check
            cleaned = re.sub(r'\D', '', phone_number)
            
            # Accept common formats
            if len(cleaned) >= 10:
                # Format as E.164
                if len(cleaned) == 10:
                    formatted = '+1' + cleaned
                else:
                    formatted = '+' + cleaned
                
                return PhoneNumberValidation(
                    is_valid=True,
                    formatted_number=formatted,
                    error_message="Number accepted (mock validation)"
                )
            
            return PhoneNumberValidation(
                is_valid=False,
                error_message=f"Invalid phone number: {phone_number}"
            )
                
        except Exception as e:
            return PhoneNumberValidation(
                is_valid=False,
                error_message=str(e)
            )
    
    def get_status(self, message_id: str) -> SMSStatus:
        """
        Get the delivery status of a mock SMS.
        
        Args:
            message_id: The message ID
            
        Returns:
            SMSStatus (always DELIVERED for mock provider)
        """
        # Find the message in sent messages
        for msg in LocalMockProvider._sent_messages:
            if msg['message_id'] == message_id:
                return SMSStatus(msg['status'])
        
        # If not found, return delivered (mock behavior)
        return SMSStatus.DELIVERED
    
    def get_sent_messages(self) -> List[Dict[str, Any]]:
        """
        Get all messages sent through this mock provider.
        
        Returns:
            List of sent message records
        """
        return [msg for msg in LocalMockProvider._sent_messages 
                if msg.get('provider_id') == self._provider_id]
    
    def clear_sent_messages(self):
        """Clear all sent messages for this provider."""
        LocalMockProvider._sent_messages = [
            msg for msg in LocalMockProvider._sent_messages
            if msg.get('provider_id') != self._provider_id
        ]
    
    @classmethod
    def clear_all_messages(cls):
        """Clear all sent messages across all instances."""
        cls._sent_messages = []
    
    def initialize(self) -> bool:
        """
        Initialize the mock provider.
        
        Returns:
            True (mock always initializes successfully)
        """
        self._initialized = True
        return True
    
    def test_connection(self) -> bool:
        """
        Test the mock connection.
        
        Returns:
            True (mock always "connects")
        """
        return True
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the provider.
        
        Returns:
            Dictionary with provider details
        """
        info = super().get_provider_info()
        info.update({
            'provider_id': self._provider_id,
            'delay': self.delay,
            'failure_rate': self.failure_rate,
            'success_status': self.success_status,
            'sent_messages_count': len(self.get_sent_messages()),
            'mock': True
        })
        return info
