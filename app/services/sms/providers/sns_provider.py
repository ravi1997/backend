"""
SNS SMS Provider Implementation

This module provides the Amazon SNS SMS gateway implementation.
SNS (Simple Notification Service) can send SMS messages directly.
"""

import re
from typing import Any, Dict, Optional
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from app.services.sms.providers import (
    SMSProvider,
    SMSProviderType,
    SMSResult,
    SMSStatus,
    PhoneNumberValidation,
    SMSProviderError
)


class SNSProvider(SMSProvider):
    """
    Amazon SNS SMS provider implementation.
    
    Requires the following configuration:
    - aws_access_key_id: AWS Access Key ID
    - aws_secret_access_key: AWS Secret Access Key
    - aws_region: AWS Region (e.g., us-east-1)
    - sender_id: (optional) Sender ID for the message
    - sms_type: (optional) Transactional or Promotional
    """
    
    provider_type = SMSProviderType.SNS
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SNS provider.
        
        Args:
            config: AWS SNS configuration dictionary
        """
        self.config = config
        self.aws_access_key_id = config.get('aws_access_key_id')
        self.aws_secret_access_key = config.get('aws_secret_access_key')
        self.aws_region = config.get('aws_region', 'us-east-1')
        self.sender_id = config.get('sender_id')
        self.sms_type = config.get('sms_type', 'Transactional')  # Transactional or Promotional
        self._client = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the SNS client.
        
        Returns:
            True if initialization successful
        """
        try:
            if not self.aws_access_key_id or not self.aws_secret_access_key:
                raise SMSProviderError(
                    "AWS access key and secret key are required",
                    provider=self.provider_type.value
                )
            
            self._client = boto3.client(
                'sns',
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            
            self._initialized = True
            
            # Test the connection
            self._test_connection()
            
            return True
            
        except ImportError:
            raise SMSProviderError(
                "AWS boto3 library not installed. Install with: pip install boto3",
                provider=self.provider_type.value
            )
        except Exception as e:
            raise SMSProviderError(
                f"Failed to initialize SNS client: {str(e)}",
                provider=self.provider_type.value
            )
    
    def _test_connection(self):
        """Test the SNS API connection."""
        try:
            # Try to get account attributes to verify credentials
            self._client.get_sms_attributes()
        except ClientError as e:
            raise SMSProviderError(
                f"SNS connection test failed: {str(e)}",
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
        Send an SMS via Amazon SNS.
        
        Args:
            to: Recipient phone number
            message: SMS message content
            from_number: Override sender (SNS uses sender_id instead)
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
            
            # Prepare message parameters
            msg_params = {
                'Message': message,
                'PhoneNumber': validation.formatted_number,
                'MessageAttributes': {
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': self.sms_type
                    }
                }
            }
            
            # Add sender ID if configured and supported in region
            if self.sender_id:
                msg_params['SenderID'] = self.sender_id
            
            # Send the message
            response = self._client.publish(**msg_params)
            
            message_id = response.get('MessageId')
            
            return SMSResult(
                success=True,
                message_id=message_id,
                status=SMSStatus.SENT,
                provider_response={
                    'message_id': message_id,
                    'response_metadata': response.get('ResponseMetadata')
                }
            )
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            return SMSResult(
                success=False,
                error_message=f"AWS SNS Error ({error_code}): {error_message}",
                provider_response={
                    'error_code': error_code,
                    'error_message': error_message
                }
            )
        except Exception as e:
            return SMSResult(
                success=False,
                error_message=str(e),
                provider_response={'error': str(e)}
            )
    
    def validate_number(self, phone_number: str) -> PhoneNumberValidation:
        """
        Validate and format a phone number for SNS.
        
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
            
            # Clean the phone number
            cleaned = re.sub(r'\D', '', phone_number)
            
            # SNS requires E.164 format
            # Try to determine country code
            if cleaned.startswith('1') and len(cleaned) == 11:
                # Assume US/Canada with leading 1
                e164 = '+' + cleaned
            elif cleaned.startswith('44') and len(cleaned) == 12:
                # Assume UK
                e164 = '+' + cleaned
            elif cleaned.startswith('91') and len(cleaned) == 13:
                # Assume India
                e164 = '+' + cleaned
            elif len(cleaned) >= 10:
                # Can't determine country code, but might be valid
                # Try with assumed US country code
                if len(cleaned) == 10:
                    e164 = '+1' + cleaned
                else:
                    e164 = '+' + cleaned
            else:
                return PhoneNumberValidation(
                    is_valid=False,
                    error_message=f"Invalid phone number format: {phone_number}"
                )
            
            # Verify the format
            if re.match(e164_pattern, e164):
                return PhoneNumberValidation(
                    is_valid=True,
                    formatted_number=e164,
                    country_code=e164[1:2] if len(e164) > 1 else None,
                    national_number=e164[2:] if len(e164) > 2 else e164
                )
            else:
                return PhoneNumberValidation(
                    is_valid=True,
                    formatted_number=phone_number,
                    error_message="Number may not be in E.164 format"
                )
                
        except Exception as e:
            return PhoneNumberValidation(
                is_valid=False,
                error_message=str(e)
            )
    
    def get_status(self, message_id: str) -> SMSStatus:
        """
        Get the delivery status of an SNS message.
        
        Note: SNS does not provide message status after sending.
        This method returns UNKNOWN as SNS doesn't support message status lookup.
        
        Args:
            message_id: SNS message ID
            
        Returns:
            SMSStatus (always UNKNOWN for SNS)
        """
        # SNS doesn't support getting message status
        # The message_id is returned but there's no API to check delivery status
        return SMSStatus.UNKNOWN
    
    def get_sms_attributes(self) -> Dict[str, str]:
        """
        Get the SMS attributes for the account.
        
        Returns:
            Dictionary of SMS attributes
        """
        if not self._initialized:
            self.initialize()
        
        try:
            response = self._client.get_sms_attributes()
            return response.get('attributes', {})
        except ClientError as e:
            return {'error': str(e)}
    
    def test_connection(self) -> bool:
        """
        Test the SNS API connection.
        
        Returns:
            True if connection successful
        """
        if not self._initialized:
            self.initialize()
        
        try:
            self._client.get_sms_attributes()
            return True
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
            'aws_region': self.aws_region,
            'sender_id': self.sender_id,
            'sms_type': self.sms_type,
            'aws_access_key_id_masked': f"{self.aws_access_key_id[:4]}...{self.aws_access_key_id[-4:]}" if self.aws_access_key_id else None
        })
        return info
