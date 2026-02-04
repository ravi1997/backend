"""
SMS Providers Package

This package contains pluggable SMS provider implementations.
"""

from app.services.sms.providers import (
    SMSProvider,
    SMSProviderType,
    SMSResult,
    SMSStatus,
    PhoneNumberValidation,
    SMSProviderError,
    SMSProviderNotFoundError,
    SMSValidationError
)

from app.services.sms.providers.twilio_provider import TwilioProvider
from app.services.sms.providers.sns_provider import SNSProvider
from app.services.sms.providers.aws_sns_provider import AWSSNSProvider
from app.services.sms.providers.local_mock_provider import LocalMockProvider


# Provider factory
PROVIDER_CLASSES = {
    SMSProviderType.TWILIO: TwilioProvider,
    SMSProviderType.SNS: SNSProvider,
    SMSProviderType.AWS_SNS: AWSSNSProvider,
    SMSProviderType.LOCAL_MOCK: LocalMockProvider,
    'twilio': TwilioProvider,
    'sns': SNSProvider,
    'aws_sns': AWSSNSProvider,
    'local_mock': LocalMockProvider,
}


def get_provider(provider_type: str, config: dict = None) -> SMSProvider:
    """
    Get an SMS provider instance by type.
    
    Args:
        provider_type: Type of provider ('twilio', 'sns', 'aws_sns', 'local_mock')
        config: Provider configuration
        
    Returns:
        SMSProvider instance
        
    Raises:
        SMSProviderNotFoundError: If provider type is not found
    """
    provider_type_upper = provider_type.lower()
    
    # Handle enum values
    if hasattr(SMSProviderType, provider_type_upper.upper()):
        provider_type_key = getattr(SMSProviderType, provider_type_upper.upper())
    else:
        provider_type_key = provider_type_upper
    
    provider_class = PROVIDER_CLASSES.get(provider_type_key)
    
    if not provider_class:
        raise SMSProviderNotFoundError(
            f"Unknown SMS provider type: {provider_type}",
            provider=provider_type
        )
    
    return provider_class(config or {})


__all__ = [
    'SMSProvider',
    'SMSProviderType',
    'SMSResult',
    'SMSStatus',
    'PhoneNumberValidation',
    'SMSProviderError',
    'SMSProviderNotFoundError',
    'SMSValidationError',
    'TwilioProvider',
    'SNSProvider',
    'AWSSNSProvider',
    'LocalMockProvider',
    'get_provider',
    'PROVIDER_CLASSES',
]
