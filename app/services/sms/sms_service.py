"""
SMS Service

Service for sending SMS messages with provider routing and retry logic.
"""

import random
import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta

from flask import current_app
from app.models.SMSDelivery import SMSDelivery
from app.models.SMSProviderConfig import SMSProviderConfig
from app.services.sms.providers import (
    SMSProvider,
    SMSProviderType,
    SMSResult,
    SMSStatus,
    get_provider,
    SMSProviderNotFoundError,
    SMSValidationError
)


class SMSService:
    """
    Service for managing SMS sending with pluggable providers.
    
    Features:
    - Provider routing based on priority/availability
    - Exponential backoff retry logic
    - Provider health checking
    - Cost tracking
    - Delivery status tracking
    """
    
    # Exponential backoff delays in seconds: 1s, 2s, 4s, 8s, 16s
    BACKOFF_DELAYS = [1, 2, 4, 8, 16]
    
    # Statuses that should trigger a retry
    RETRY_STATUSES = {SMSStatus.PENDING}
    
    # Statuses that indicate the message was sent
    SENT_STATUSES = {SMSStatus.SENT, SMSStatus.DELIVERED}
    
    # Statuses that indicate failure
    FAILED_STATUSES = {SMSStatus.FAILED, SMSStatus.UNKNOWN}
    
    _instance = None
    _providers: Dict[str, SMSProvider] = {}
    
    def __new__(cls):
        """Singleton pattern for SMS service."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the SMS service."""
        self.logger = logging.getLogger(__name__)
        self._provider_cache = {}
    
    def _get_provider_from_config(
        self,
        config: SMSProviderConfig,
        cache: bool = True
    ) -> Optional[SMSProvider]:
        """
        Get a provider instance from a configuration.
        
        Args:
            config: SMSProviderConfig document
            cache: Whether to cache the provider instance
            
        Returns:
            SMSProvider instance or None
        """
        if not config.is_available():
            self.logger.warning(f"Provider {config.provider_id} is not available")
            return None
        
        # Check cache
        if cache and config.provider_id in self._provider_cache:
            return self._provider_cache[config.provider_id]
        
        try:
            # Get the full config (including secrets)
            provider_config = config.get_full_config()
            
            # Create provider instance
            provider = get_provider(config.provider_type, provider_config)
            
            # Initialize the provider
            if provider.initialize():
                if cache:
                    self._provider_cache[config.provider_id] = provider
                return provider
            else:
                self.logger.error(f"Provider {config.provider_id} failed to initialize")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to create provider {config.provider_id}: {str(e)}")
            return None
    
    def _get_available_providers(
        self,
        preferred_provider_id: str = None
    ) -> List[SMSProviderConfig]:
        """
        Get a list of available providers, sorted by priority.
        
        Args:
            preferred_provider_id: Prefer this provider if available
            
        Returns:
            List of available provider configurations
        """
        query = {'enabled': True}
        providers = SMSProviderConfig.objects(**query)
        
        # Sort by priority (lower = higher priority)
        available = sorted(providers, key=lambda p: p.priority)
        
        # If preferred provider is specified and available, put it first
        if preferred_provider_id:
            preferred = [p for p in available if p.provider_id == preferred_provider_id]
            other = [p for p in available if p.provider_id != preferred_provider_id]
            available = preferred + other
        
        return available
    
    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay in seconds with random jitter
        """
        if attempt >= len(self.BACKOFF_DELAYS):
            base_delay = self.BACKOFF_DELAYS[-1]
        else:
            base_delay = self.BACKOFF_DELAYS[attempt]
        
        # Add jitter: random delay between 0.5x and 1.5x of base delay
        jitter_factor = random.uniform(0.5, 1.5)
        return base_delay * jitter_factor
    
    def _select_provider(
        self,
        preferred_provider_id: str = None
    ) -> tuple[Optional[SMSProvider], Optional[SMSProviderConfig]]:
        """
        Select an available provider.
        
        Args:
            preferred_provider_id: Preferred provider ID
            
        Returns:
            Tuple of (provider instance, provider config)
        """
        available = self._get_available_providers(preferred_provider_id)
        
        for config in available:
            provider = self._get_provider_from_config(config)
            if provider and provider.test_connection():
                return provider, config
        
        return None, None
    
    def send_sms(
        self,
        to: str,
        message: str,
        form_id: str = None,
        webhook_id: str = None,
        provider_id: str = None,
        created_by: str = None,
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send an SMS with automatic provider selection and retry logic.
        
        Args:
            to: Recipient phone number
            message: SMS message content
            form_id: Form that triggered this SMS
            webhook_id: Webhook that triggered this SMS
            provider_id: Specific provider to use (optional)
            created_by: User who triggered this SMS
            max_retries: Maximum retry attempts
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with delivery status:
            {
                "status": "success" | "failed",
                "sms_id": str,
                "provider": str,
                "message_id": str,
                "attempt_count": int,
                "error": str
            }
        """
        # Validate the phone number format first
        if not self._validate_phone_number(to):
            return {
                "status": "failed",
                "error": "Invalid phone number format",
                "recipient_number": to
            }
        
        # Create delivery record
        delivery = SMSDelivery(
            recipient_number=to,
            message=message,
            form_id=form_id,
            webhook_id=webhook_id,
            provider=provider_id or 'unknown',
            max_retries=max_retries,
            created_by=created_by,
            status='pending'
        )
        delivery.save()
        
        # Retry loop
        for attempt in range(max_retries):
            attempt_num = attempt + 1
            delivery.attempt_count = attempt_num
            
            # Select provider
            provider, provider_config = self._select_provider(provider_id)
            
            if not provider:
                # No provider available
                if attempt < max_retries - 1:
                    backoff_delay = self._calculate_backoff(attempt)
                    next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff_delay)
                    delivery.schedule_retry(next_retry_at)
                    delivery.save()
                    
                    self.logger.warning(
                        f"No SMS provider available. Retrying in {backoff_delay:.2f}s "
                        f"(delivery_id: {delivery.sms_id}, attempt {attempt_num}/{max_retries})"
                    )
                    
                    time.sleep(backoff_delay)
                    continue
                else:
                    delivery.mark_failed("No SMS provider available")
                    delivery.save()
                    return {
                        "status": "failed",
                        "sms_id": str(delivery.sms_id),
                        "error": "No SMS provider available",
                        "attempt_count": attempt_num
                    }
            
            # Update provider info on delivery record
            delivery.provider = provider_config.provider_type
            delivery.provider_config_id = provider_config.provider_id
            delivery.save()
            
            try:
                # Send the SMS
                result = provider.send_sms(to, message, **kwargs)
                
                if result.success:
                    # Success!
                    delivery.mark_sent(result.message_id)
                    
                    if result.cost:
                        delivery.cost = result.cost
                    
                    delivery.metadata = {
                        'provider_response': result.provider_response,
                        'retry_schedule': self.BACKOFF_DELAYS[:max_retries]
                    }
                    
                    # Mark as delivered for providers that report it
                    if result.status == SMSStatus.DELIVERED:
                        delivery.mark_delivered()
                    else:
                        delivery.completed_at = datetime.now(timezone.utc)
                    
                    delivery.save()
                    
                    self.logger.info(
                        f"SMS sent successfully via {provider_config.provider_name} "
                        f"(delivery_id: {delivery.sms_id}, message_id: {result.message_id})"
                    )
                    
                    return {
                        "status": "success",
                        "sms_id": str(delivery.sms_id),
                        "provider": provider_config.provider_name,
                        "message_id": result.message_id,
                        "status": result.status.value,
                        "attempt_count": attempt_num,
                        "cost": result.cost
                    }
                else:
                    # Failed
                    delivery.mark_failed(
                        result.error_message or "Unknown error",
                        result.provider_response.get('error_code') if result.provider_response else None
                    )
                    
                    delivery.metadata = {
                        'provider_response': result.provider_response
                    }
                    
                    # Check if we should retry
                    if attempt < max_retries - 1:
                        backoff_delay = self._calculate_backoff(attempt)
                        next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff_delay)
                        delivery.schedule_retry(next_retry_at)
                        
                        self.logger.warning(
                            f"SMS attempt {attempt_num}/{max_retries} failed for "
                            f"{to}: {result.error_message}. Retrying in {backoff_delay:.2f}s"
                        )
                        
                        delivery.save()
                        time.sleep(backoff_delay)
                        continue
                    else:
                        # Last attempt - mark as failed
                        delivery.save()
                        
                        self.logger.error(
                            f"SMS failed after {attempt_num} attempts for {to}: {result.error_message}"
                        )
                        
                        return {
                            "status": "failed",
                            "sms_id": str(delivery.sms_id),
                            "provider": provider_config.provider_name,
                            "error": result.error_message,
                            "attempt_count": attempt_num
                        }
                        
            except Exception as e:
                self.logger.error(f"SMS sending error: {str(e)}")
                
                if attempt < max_retries - 1:
                    backoff_delay = self._calculate_backoff(attempt)
                    next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff_delay)
                    delivery.schedule_retry(next_retry_at)
                    delivery.save()
                    
                    time.sleep(backoff_delay)
                    continue
                else:
                    delivery.mark_failed(str(e))
                    delivery.save()
                    
                    return {
                        "status": "failed",
                        "sms_id": str(delivery.sms_id),
                        "error": str(e),
                        "attempt_count": attempt_num
                    }
        
        # Should not reach here, but just in case
        return {
            "status": "failed",
            "sms_id": str(delivery.sms_id),
            "error": "Unknown error"
        }
    
    def _validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate basic phone number format.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid format
        """
        import re
        
        # Remove whitespace
        cleaned = phone_number.strip()
        
        # Check for E.164 format or common formats
        e164_pattern = r'^\+[1-9]\d{1,14}$'
        digits_only = re.sub(r'\D', '', cleaned)
        
        return bool(re.match(e164_pattern, cleaned) or (10 <= len(digits_only) <= 15))
    
    def get_delivery_status(self, sms_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the delivery status of an SMS.
        
        Args:
            sms_id: The SMS delivery ID
            
        Returns:
            Dictionary with delivery status or None if not found
        """
        try:
            delivery = SMSDelivery.objects.get(sms_id=sms_id)
            return delivery.to_dict()
        except SMSDelivery.DoesNotExist:
            return None
    
    def get_delivery_history(
        self,
        form_id: str = None,
        provider: str = None,
        status: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get SMS delivery history with filtering and pagination.
        
        Args:
            form_id: Filter by form ID
            provider: Filter by provider
            status: Filter by status
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with deliveries and pagination info
        """
        query = {}
        
        if form_id:
            query['form_id'] = form_id
        
        if provider:
            query['provider'] = provider
        
        if status:
            query['status'] = status
        
        # Count total
        total = SMSDelivery.objects(**query).count()
        
        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page
        skip = (page - 1) * per_page
        
        # Get deliveries
        deliveries = SMSDelivery.objects(**query).order_by('-created_at').skip(skip).limit(per_page)
        
        return {
            "deliveries": [d.to_dict() for d in deliveries],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    
    def retry_sms(self, sms_id: str) -> Dict[str, Any]:
        """
        Retry a failed SMS delivery.
        
        Args:
            sms_id: The SMS delivery ID
            
        Returns:
            Dictionary with retry result
        """
        try:
            delivery = SMSDelivery.objects.get(sms_id=sms_id)
            
            if not delivery.is_retryable():
                return {
                    "status": "error",
                    "message": f"SMS is not retryable (status: {delivery.status}, attempts: {delivery.attempt_count}/{delivery.max_retries})"
                }
            
            # Reset for retry
            delivery.attempt_count = 0
            delivery.status = 'pending'
            delivery.error_message = None
            delivery.save()
            
            # Retry with same parameters
            return self.send_sms(
                to=delivery.recipient_number,
                message=delivery.message,
                form_id=delivery.form_id,
                webhook_id=delivery.webhook_id,
                provider_id=delivery.provider_config_id,
                created_by=delivery.created_by,
                max_retries=delivery.max_retries
            )
            
        except SMSDelivery.DoesNotExist:
            return {
                "status": "error",
                "message": "SMS delivery not found"
            }
    
    def get_provider_status(self, provider_id: str = None) -> List[Dict[str, Any]]:
        """
        Get the status of SMS providers.
        
        Args:
            provider_id: Specific provider to check (optional)
            
        Returns:
            List of provider status dictionaries
        """
        if provider_id:
            configs = [SMSProviderConfig.objects.get(provider_id=provider_id)]
        else:
            configs = SMSProviderConfig.objects()
        
        statuses = []
        for config in configs:
            provider = self._get_provider_from_config(config, cache=False)
            is_available = provider.test_connection() if provider else False
            
            status = {
                'provider_id': config.provider_id,
                'provider_name': config.provider_name,
                'provider_type': config.provider_type,
                'enabled': config.enabled,
                'available': is_available,
                'priority': config.priority,
                'is_default': config.is_default
            }
            
            if provider:
                status['info'] = provider.get_provider_info()
            
            statuses.append(status)
        
        return statuses
    
    def validate_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Validate a phone number using available providers.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            Dictionary with validation result
        """
        provider, config = self._select_provider()
        
        if provider:
            result = provider.validate_number(phone_number)
            return {
                'is_valid': result.is_valid,
                'formatted_number': result.formatted_number,
                'country_code': result.country_code,
                'carrier': result.carrier,
                'error_message': result.error_message,
                'validated_with': config.provider_name if config else None
            }
        
        # No provider available, do basic validation
        import re
        cleaned = re.sub(r'\D', '', phone_number)
        
        return {
            'is_valid': 10 <= len(cleaned) <= 15,
            'formatted_number': phone_number if phone_number.startswith('+') else None,
            'error_message': 'No SMS provider available for validation'
        }
    
    def get_providers(self) -> List[Dict[str, Any]]:
        """
        Get all configured SMS providers.
        
        Returns:
            List of provider configurations
        """
        providers = SMSProviderConfig.objects().order_by('priority')
        return [p.to_dict() for p in providers]
    
    def create_provider(
        self,
        provider_id: str,
        provider_name: str,
        provider_type: str,
        config: Dict[str, Any],
        created_by: str = None,
        **kwargs
    ) -> SMSProviderConfig:
        """
        Create a new SMS provider configuration.
        
        Args:
            provider_id: Unique provider identifier
            provider_name: Human-readable name
            provider_type: Type of provider
            config: Provider configuration
            created_by: User creating the provider
            **kwargs: Additional options
            
        Returns:
            Created SMSProviderConfig
        """
        provider = SMSProviderConfig(
            provider_id=provider_id,
            provider_name=provider_name,
            provider_type=provider_type,
            config=config,
            created_by=created_by,
            **kwargs
        )
        provider.save()
        
        return provider
    
    def update_provider(
        self,
        provider_id: str,
        config: Dict[str, Any] = None,
        enabled: bool = None,
        priority: int = None,
        updated_by: str = None
    ) -> Optional[SMSProviderConfig]:
        """
        Update an SMS provider configuration.
        
        Args:
            provider_id: Provider to update
            config: New configuration (optional)
            enabled: New enabled status (optional)
            priority: New priority (optional)
            updated_by: User making the update
            
        Returns:
            Updated SMSProviderConfig or None
        """
        try:
            provider = SMSProviderConfig.objects.get(provider_id=provider_id)
            
            if config is not None:
                provider.update_config(config, updated_by)
            
            if enabled is not None:
                if enabled:
                    provider.enable()
                else:
                    provider.disable()
            
            if priority is not None:
                provider.priority = priority
            
            provider.save()
            
            # Clear from cache
            self._provider_cache.pop(provider_id, None)
            
            return provider
            
        except SMSProviderConfig.DoesNotExist:
            return None
    
    def delete_provider(self, provider_id: str) -> bool:
        """
        Delete an SMS provider configuration.
        
        Args:
            provider_id: Provider to delete
            
        Returns:
            True if deleted
        """
        try:
            provider = SMSProviderConfig.objects.get(provider_id=provider_id)
            provider.delete()
            
            # Clear from cache
            self._provider_cache.pop(provider_id, None)
            
            return True
            
        except SMSProviderConfig.DoesNotExist:
            return False
    
    def clear_provider_cache(self):
        """Clear the provider cache."""
        self._provider_cache = {}
