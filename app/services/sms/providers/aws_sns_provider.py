"""
AWS SNS SMS Provider Implementation

This module provides an enhanced Amazon SNS SMS gateway implementation
using boto3's SNS client with additional features and better error handling.
"""

import re
import json
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


class AWSSNSProvider(SMSProvider):
    """
    Enhanced AWS SNS SMS provider implementation.
    
    This is a more feature-rich implementation of AWS SNS SMS,
    supporting additional options and better configuration.
    
    Configuration options:
    - aws_access_key_id: AWS Access Key ID
    - aws_secret_access_key: AWS Secret Access Key
    - aws_region: AWS Region (e.g., us-east-1)
    - sender_id: Sender ID for the message
    - sms_type: Transactional, Promotional, or Custom
    - max_price: Maximum price per SMS message (in USD)
    - service_url: Custom service endpoint URL (for local testing)
    """
    
    provider_type = SMSProviderType.AWS_SNS
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AWS SNS provider.
        
        Args:
            config: AWS SNS configuration dictionary
        """
        self.config = config
        self.aws_access_key_id = config.get('aws_access_key_id')
        self.aws_secret_access_key = config.get('aws_secret_access_key')
        self.aws_region = config.get('aws_region', 'us-east-1')
        self.sender_id = config.get('sender_id')
        self.sms_type = config.get('sms_type', 'Transactional')
        self.max_price = config.get('max_price')  # e.g., "0.50" USD
        self.service_url = config.get('service_url')  # For localstack/testing
        self._client = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the SNS client with boto3.
        
        Returns:
            True if initialization successful
        """
        try:
            import botocore.session
            from botocore.config import Config
            
            if not self.aws_access_key_id or not self.aws_secret_access_key:
                # Try to use IAM role if running on EC2/Lambda
                if not self.service_url:
                    raise SMSProviderError(
                        "AWS credentials are required",
                        provider=self.provider_type.value
                    )
            
            # Configure the SNS client
            client_kwargs = {
                'region_name': self.aws_region
            }
            
            # Add credentials
            if self.aws_access_key_id and self.aws_secret_access_key:
                client_kwargs['aws_access_key_id'] = self.aws_access_key_id
                client_kwargs['aws_secret_access_key'] = self.aws_secret_access_key
            
            # Add custom endpoint URL for local testing (LocalStack)
            if self.service_url:
                client_kwargs['endpoint_url'] = self.service_url
            
            self._client = boto3.client('sns', **client_kwargs)
            self._initialized = True
            
            # Test the connection
            self._test_connection()
            
            return True
            
        except ImportError:
            raise SMSProviderError(
                "AWS boto3 library not installed. Install with: pip install boto3",
                provider=self.provider_type.value
            )
        except SMSProviderError:
            raise
        except Exception as e:
            raise SMSProviderError(
                f"Failed to initialize AWS SNS client: {str(e)}",
                provider=self.provider_type.value
            )
    
    def _test_connection(self):
        """Test the SNS API connection."""
        try:
            # Try to get account attributes to verify credentials
            response = self._client.get_sms_attributes()
            attributes = response.get('attributes', {})
            # Default SMS attributes are set at account level
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'InvalidClientTokenId':
                raise SMSProviderError(
                    "Invalid AWS credentials",
                    provider=self.provider_type.value,
                    error_code=error_code
                )
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
            from_number: Override sender (uses sender_id config)
            **kwargs: Additional parameters:
                - message_attributes: Custom SNS message attributes
                - structured_message: Use JSON-structured message
                - hex_message: Send as hex-encoded message
                
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
                'MessageAttributes': {}
            }
            
            # Add SMS type
            msg_params['MessageAttributes']['AWS.SNS.SMS.SMSType'] = {
                'DataType': 'String',
                'StringValue': self.sms_type
            }
            
            # Add sender ID if configured
            if self.sender_id:
                msg_params['SenderID'] = self.sender_id
            
            # Add max price if configured
            if self.max_price:
                msg_params['MaxPrice'] = str(self.max_price)
            
            # Add custom message attributes from kwargs
            custom_attrs = kwargs.get('message_attributes', {})
            for key, value in custom_attrs.items():
                if len(key) <= 100:  # SNS attribute name limit
                    msg_params['MessageAttributes'][key] = {
                        'DataType': 'String',
                        'StringValue': str(value)
                    }
            
            # Send the message
            response = self._client.publish(**msg_params)
            
            message_id = response.get('MessageId')
            
            return SMSResult(
                success=True,
                message_id=message_id,
                status=SMSStatus.SENT,
                provider_response={
                    'message_id': message_id,
                    'response_metadata': response.get('ResponseMetadata'),
                    'message_attributes': msg_params.get('MessageAttributes', {})
                }
            )
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            # Common SNS error codes
            error_category = self._categorize_error(error_code)
            
            return SMSResult(
                success=False,
                error_message=f"AWS SNS Error ({error_code}): {error_message}",
                provider_response={
                    'error_code': error_code,
                    'error_message': error_message,
                    'error_category': error_category
                }
            )
        except Exception as e:
            return SMSResult(
                success=False,
                error_message=str(e),
                provider_response={'error': str(e)}
            )
    
    def _categorize_error(self, error_code: str) -> str:
        """
        Categorize AWS SNS errors for better handling.
        
        Args:
            error_code: AWS error code
            
        Returns:
            Error category string
        """
        error_categories = {
            'AuthenticationError': 'authentication',
            'InvalidClientTokenId': 'authentication',
            'SignatureDoesNotMatch': 'authentication',
            'AccessDeniedException': 'authorization',
            'ThrottledException': 'throttling',
            'LimitExceededException': 'limit_exceeded',
            'InternalError': 'server_error',
            'ServiceUnavailableException': 'server_error'
        }
        
        return error_categories.get(error_code, 'unknown')
    
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
                return PhoneNumberValidation(
                    is_valid=True,
                    formatted_number=phone_number,
                    country_code=phone_number[1:2],
                    national_number=phone_number[2:]
                )
            
            # Clean the phone number
            cleaned = re.sub(r'\D', '', phone_number)
            
            # Detect country code
            country_code_map = {
                '1': 'US',  # US/Canada
                '44': 'UK',
                '91': 'IN',  # India
                '86': 'CN',  # China
                '81': 'JP',  # Japan
                '82': 'KR',  # South Korea
                '49': 'DE',  # Germany
                '33': 'FR',  # France
                '61': 'AU',  # Australia
                '55': 'BR',  # Brazil
            }
            
            # Try to determine country code
            for code, country in sorted(country_code_map.items(), key=lambda x: -len(x[0])):
                if cleaned.startswith(code) and len(cleaned) in [len(code) + 10, len(code) + 9]:
                    e164 = '+' + cleaned
                    return PhoneNumberValidation(
                        is_valid=True,
                        formatted_number=e164,
                        country_code=country,
                        national_number=cleaned[len(code):]
                    )
            
            # Fallback: assume it's a valid number and add +
            if len(cleaned) >= 10:
                # If 10 digits, assume US
                if len(cleaned) == 10:
                    e164 = '+1' + cleaned
                    return PhoneNumberValidation(
                        is_valid=True,
                        formatted_number=e164,
                        country_code='US',
                        national_number=cleaned
                    )
                # Otherwise just add +
                e164 = '+' + cleaned
                return PhoneNumberValidation(
                    is_valid=True,
                    formatted_number=e164,
                    error_message="Number validated but country could not be determined"
                )
            
            return PhoneNumberValidation(
                is_valid=False,
                error_message=f"Invalid phone number format: {phone_number}"
            )
                
        except Exception as e:
            return PhoneNumberValidation(
                is_valid=False,
                error_message=str(e)
            )
    
    def get_status(self, message_id: str) -> SMSStatus:
        """
        Get the delivery status of an SNS message.
        
        Note: AWS SNS does not provide message delivery status after sending.
        However, SNS supports delivery status configuration for mobile apps.
        For standard SMS, this returns UNKNOWN.
        
        Args:
            message_id: SNS message ID
            
        Returns:
            SMSStatus (always UNKNOWN for standard SNS SMS)
        """
        return SMSStatus.UNKNOWN
    
    def check_delivery_status(
        self,
        message_id: str,
        endpoint_arn: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check delivery status for a message to a mobile endpoint.
        
        This requires SNS delivery status logging to be configured.
        
        Args:
            message_id: SNS message ID
            endpoint_arn: The endpoint ARN the message was sent to
            
        Returns:
            Dictionary with delivery status or None if not available
        """
        try:
            response = self._client.get_endpoint_attributes(
                EndpointArn=endpoint_arn
            )
            return response.get('Attributes', {})
        except ClientError:
            return None
    
    def set_sms_attributes(self, attributes: Dict[str, str]) -> bool:
        """
        Set SMS attributes for the account.
        
        Args:
            attributes: Dictionary of attribute names to values
            
        Returns:
            True if successful
        """
        if not self._initialized:
            self.initialize()
        
        try:
            self._client.set_sms_attributes(attributes=attributes)
            return True
        except ClientError:
            return False
    
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
            'max_price': self.max_price,
            'service_url': self.service_url,
            'aws_access_key_id_masked': f"{self.aws_access_key_id[:4]}...{self.aws_access_key_id[-4:]}" if self.aws_access_key_id else None
        })
        return info
