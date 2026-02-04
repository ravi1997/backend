"""
Twilio SMS Provider Implementation

This module provides the Twilio SMS gateway implementation.
"""

import re
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from app.services.sms.providers import (
    SMSProvider,
    SMSProviderType,
    SMSResult,
    SMSStatus,
    PhoneNumberValidation,
    SMSProviderError
)


class TwilioProvider(SMSProvider):
    """
    Twilio SMS provider implementation.
    
    Requires the following configuration:
    - account_sid: Twilio Account SID
    - auth_token: Twilio Auth Token
    - from_number: Twilio phone number (E.164 format)
    - messaging_service_sid: (optional) Messaging Service SID
    """
    
    provider_type = SMSProviderType.TWILIO
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Twilio provider.
        
        Args:
            config: Twilio configuration dictionary
        """
        self.config = config
        self.account_sid = config.get('account_sid')
        self.auth_token = config.get('auth_token')
        self.from_number = config.get('from_number')
        self.messaging_service_sid = config.get('messaging_service_sid')
        self._client = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the Twilio client.
        
        Returns:
            True if initialization successful
        """
        try:
            # Import Twilio client here to make it optional
            from twilio.rest import Client
            from twilio.base.exceptions import TwilioRestException
            
            if not self.account_sid or not self.auth_token:
                raise SMSProviderError(
                    "Twilio account_sid and auth_token are required",
                    provider=self.provider_type.value
                )
            
            self._client = Client(self.account_sid, self.auth_token)
            self._initialized = True
            
            # Test the connection
            self._test_connection()
            
            return True
            
        except ImportError:
            raise SMSProviderError(
                "Twilio library not installed. Install with: pip install twilio",
                provider=self.provider_type.value
            )
        except Exception as e:
            raise SMSProviderError(
                f"Failed to initialize Twilio client: {str(e)}",
                provider=self.provider_type.value
            )
    
    def _test_connection(self):
        """Test the Twilio API connection."""
        try:
            # Try to fetch account info to verify credentials
            account = self._client.api.account.fetch()
            # If we get here, credentials are valid
        except Exception as e:
            raise SMSProviderError(
                f"Twilio connection test failed: {str(e)}",
                provider=self.provider_type.value
            )
    
    def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
        **kwargs
    ) -> SMSResult:
        """
        Send an SMS via Twilio.
        
        Args:
            to: Recipient phone number
            message: SMS message content
            from_number: Override sender number
            **kwargs: Additional parameters
            
        Returns:
            SMSResult with delivery status
        """
        if not self._initialized:
            self.initialize()
        
        try:
            # Validate and format the phone number
            validation = self.validate_number(to)
            if not validation.is_valid:
                return SMSResult(
                    success=False,
                    error_message=f"Invalid phone number: {validation.error_message}"
                )
            
            # Use provided from_number or fall back to configured
            sender = from_number or self.from_number
            
            if not sender and not self.messaging_service_sid:
                return SMSResult(
                    success=False,
                    error_message="No sender number or messaging service SID configured"
                )
            
            # Prepare message parameters
            msg_params = {
                'to': validation.formatted_number,
                'body': message
            }
            
            if self.messaging_service_sid:
                msg_params['messagingServiceSid'] = self.messaging_service_sid
            else:
                msg_params['from'] = sender
            
            # Send the message
            if self.messaging_service_sid:
                msg = self._client.messages.create(**msg_params)
            else:
                msg = self._client.messages.create(**msg_params)
            
            # Map Twilio status to our status
            status = self._map_status(msg.status)
            
            return SMSResult(
                success=status in [SMSStatus.SENT, SMSStatus.DELIVERED],
                message_id=msg.sid,
                status=status,
                provider_response={
                    'status': msg.status,
                    'date_created': str(msg.date_created) if msg.date_created else None,
                    'date_sent': str(msg.date_sent) if msg.date_sent else None,
                    'error_code': msg.error_code,
                    'error_message': msg.error_message
                },
                cost=float(msg.price) if msg.price else None
            )
            
        except Exception as e:
            return SMSResult(
                success=False,
                error_message=str(e),
                provider_response={'error': str(e)}
            )
    
    def validate_number(self, phone_number: str) -> PhoneNumberValidation:
        """
        Validate and format a phone number using Twilio lookup.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            PhoneNumberValidation with validation results
        """
        try:
            # Basic E.164 validation regex
            e164_pattern = r'^\+[1-9]\d{1,14}$'
            
            if re.match(e164_pattern, phone_number):
                # Already in E.164 format
                return PhoneNumberValidation(
                    is_valid=True,
                    formatted_number=phone_number,
                    country_code=phone_number[1:2],
                    national_number=phone_number[2:]
                )
            
            # Try to look up the number using Twilio Lookup API
            if self._client:
                lookup = self._client.lookups.phone_numbers(phone_number).fetch()
                
                if lookup.valid:
                    return PhoneNumberValidation(
                        is_valid=True,
                        formatted_number=lookup.phone_number,
                        country_code=lookup.country_code,
                        national_number=lookup.national_format,
                        carrier=lookup.carrier.get('name') if lookup.carrier else None
                    )
                else:
                    return PhoneNumberValidation(
                        is_valid=False,
                        error_message="Phone number is not valid"
                    )
            
            # Fallback: Basic validation without API
            # Remove non-digit characters
            cleaned = re.sub(r'\D', '', phone_number)
            
            # Basic US/International validation
            if len(cleaned) >= 10 and len(cleaned) <= 15:
                # Assume it's valid but can't format without country code
                return PhoneNumberValidation(
                    is_valid=True,
                    formatted_number=phone_number,
                    error_message="Number validated without carrier info (no Lookup API)"
                )
            else:
                return PhoneNumberValidation(
                    is_valid=False,
                    error_message=f"Invalid phone number length: {len(cleaned)} digits"
                )
                
        except Exception as e:
            return PhoneNumberValidation(
                is_valid=False,
                error_message=str(e)
            )
    
    def get_status(self, message_id: str) -> SMSStatus:
        """
        Get the delivery status of a Twilio message.
        
        Args:
            message_id: Twilio message SID
            
        Returns:
            SMSStatus indicating delivery status
        """
        if not self._initialized:
            self.initialize()
        
        try:
            msg = self._client.messages(message_id).fetch()
            return self._map_status(msg.status)
        except Exception as e:
            return SMSStatus.UNKNOWN
    
    def _map_status(self, twilio_status: str) -> SMSStatus:
        """
        Map Twilio message status to our SMSStatus.
        
        Args:
            twilio_status: Twilio status string
            
        Returns:
            Corresponding SMSStatus
        """
        status_mapping = {
            'queued': SMSStatus.PENDING,
            'sending': SMSStatus.PENDING,
            'sent': SMSStatus.SENT,
            'delivered': SMSStatus.DELIVERED,
            'undelivered': SMSStatus.FAILED,
            'failed': SMSStatus.FAILED,
            'canceled': SMSStatus.FAILED,
        }
        
        return status_mapping.get(twilio_status.lower(), SMSStatus.UNKNOWN)
    
    def test_connection(self) -> bool:
        """
        Test the Twilio API connection.
        
        Returns:
            True if connection successful
        """
        if not self._initialized:
            self.initialize()
        
        try:
            account = self._client.api.account.fetch()
            return account is not None
        except Exception:
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the provider.
        
        Returns:
            Dictionary with provider details
        """
        info = super().get_provider_info()
        info.update({
            'account_sid_masked': f"{self.account_sid[:4]}...{self.account_sid[-4:]}" if self.account_sid else None,
            'from_number': self.from_number,
            'messaging_service_sid': self.messaging_service_sid
        })
        return info
