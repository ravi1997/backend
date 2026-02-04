import requests
import time
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from flask import current_app
from app.models.WebhookLog import WebhookLog
from app.models.WebhookDelivery import WebhookDelivery


class WebhookService:
    """
    Service for reliable webhook delivery with retry mechanism and failure logging.
    
    Features:
    - Exponential backoff with jitter for retry delays
    - Dead letter queue detection for server errors
    - Configurable max retries
    - Comprehensive delivery tracking
    """
    
    # Dead letter queue status codes - these should trigger retries
    DEAD_LETTER_CODES = [429, 502, 503, 504] + list(range(500, 600))
    
    # Exponential backoff base delays in seconds: 1s, 2s, 4s, 8s, 16s, 32s, 64s
    BACKOFF_DELAYS = [1, 2, 4, 8, 16, 32, 64]
    
    @staticmethod
    def _calculate_backoff(attempt: int) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Args:
            attempt: The current attempt number (0-indexed)
        
        Returns:
            Delay in seconds with random jitter (0.5x to 2x of base delay)
        """
        if attempt >= len(WebhookService.BACKOFF_DELAYS):
            # Cap at the maximum backoff delay
            base_delay = WebhookService.BACKOFF_DELAYS[-1]
        else:
            base_delay = WebhookService.BACKOFF_DELAYS[attempt]
        
        # Add jitter: random delay between 0.5x and 2x of base delay
        jitter_factor = random.uniform(0.5, 2.0)
        return base_delay * jitter_factor
    
    @staticmethod
    def _is_dead_letter_error(status_code: int) -> bool:
        """
        Check if a status code indicates a dead letter queue error.
        
        Args:
            status_code: HTTP status code
        
        Returns:
            True if the status code is a dead letter error, False otherwise
        """
        return status_code in WebhookService.DEAD_LETTER_CODES
    
    @staticmethod
    def _is_success(status_code: int) -> bool:
        """
        Check if a status code indicates success.
        
        Args:
            status_code: HTTP status code
        
        Returns:
            True if the status code is a success (2xx), False otherwise
        """
        return 200 <= status_code < 300
    
    @staticmethod
    def send_webhook(
        url: str,
        payload: Dict[str, Any],
        webhook_id: str,
        form_id: str,
        created_by: str,
        max_retries: int = 5,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        schedule_for: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Send a webhook with exponential backoff retry logic.
        
        Args:
            url: The webhook URL to send to
            payload: The JSON payload to send
            webhook_id: Unique identifier for the webhook configuration
            form_id: ID of the form that triggered this webhook
            created_by: User who triggered this webhook delivery
            max_retries: Maximum number of retry attempts (default: 5)
            headers: Optional custom headers
            timeout: Request timeout in seconds (default: 10)
            schedule_for: Optional datetime to schedule delivery for later
        
        Returns:
            Dictionary with delivery status and details:
            {
                "status": "success" | "failed" | "scheduled",
                "delivery_id": str,
                "attempt_count": int,
                "message": str,
                "error": Optional[str]
            }
        """
        # Create initial delivery record
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            url=url,
            form_id=form_id,
            payload=payload,
            status='pending',
            attempt_count=0,
            max_retries=max_retries,
            created_by=created_by
        )
        
        # If scheduled for later, set next_retry_at and return
        if schedule_for:
            delivery.next_retry_at = schedule_for
            delivery.save()
            current_app.logger.info(
                f"Webhook scheduled for {schedule_for.isoformat()} to {url} "
                f"(delivery_id: {delivery.id})"
            )
            return {
                "status": "scheduled",
                "delivery_id": str(delivery.id),
                "message": f"Webhook scheduled for {schedule_for.isoformat()}",
                "next_retry_at": schedule_for.isoformat()
            }
        
        delivery.save()
        
        # Default headers
        if headers is None:
            headers = {
                "Content-Type": "application/json"
            }
        
        # Retry loop with exponential backoff and jitter
        for attempt in range(max_retries):
            attempt_num = attempt + 1
            delivery.attempt_count = attempt_num
            delivery.last_attempt_at = datetime.now(timezone.utc)
            
            # Update status to in_progress or retrying
            if attempt == 0:
                delivery.status = 'in_progress'
            else:
                delivery.status = 'retrying'
            
            delivery.save()
            
            try:
                # Send the webhook request
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                )
                
                # Check if request was successful (2xx status codes)
                if WebhookService._is_success(response.status_code):
                    # Success!
                    delivery.status = 'success'
                    delivery.response_code = response.status_code
                    delivery.response_body = response.text[:5000]  # Limit response body size
                    delivery.completed_at = datetime.now(timezone.utc)
                    delivery.metadata = {
                        'headers': dict(response.headers),
                        'retry_schedule': WebhookService.BACKOFF_DELAYS[:max_retries]
                    }
                    delivery.save()
                    
                    current_app.logger.info(
                        f"Webhook delivered successfully to {url} "
                        f"(delivery_id: {delivery.id}, attempt {attempt_num}/{max_retries})"
                    )
                    
                    return {
                        "status": "success",
                        "delivery_id": str(delivery.id),
                        "attempt_count": attempt_num,
                        "message": f"Webhook delivered successfully on attempt {attempt_num}",
                        "status_code": response.status_code
                    }
                else:
                    # Non-2xx response - treat as failure
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    delivery.error_message = error_msg
                    delivery.response_code = response.status_code
                    delivery.response_body = response.text[:5000]
                    
                    # Check if this is a dead letter error (should retry)
                    is_dead_letter = WebhookService._is_dead_letter_error(response.status_code)
                    
                    if is_dead_letter and attempt < max_retries - 1:
                        # Schedule retry with exponential backoff and jitter
                        backoff_delay = WebhookService._calculate_backoff(attempt)
                        next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff_delay)
                        delivery.next_retry_at = next_retry_at
                        delivery.metadata = {
                            'is_dead_letter': True,
                            'backoff_delay': backoff_delay,
                            'retry_schedule': WebhookService.BACKOFF_DELAYS[:max_retries]
                        }
                        delivery.save()
                        
                        current_app.logger.warning(
                            f"Webhook attempt {attempt_num}/{max_retries} failed with dead letter error "
                            f"for {url}: {error_msg}. Retrying in {backoff_delay:.2f}s "
                            f"(delivery_id: {delivery.id})"
                        )
                        
                        # Wait for backoff delay
                        time.sleep(backoff_delay)
                        continue
                    else:
                        # Not retryable or last attempt - mark as failed
                        delivery.status = 'failed'
                        delivery.completed_at = datetime.now(timezone.utc)
                        delivery.metadata = {
                            'is_dead_letter': is_dead_letter,
                            'retry_schedule': WebhookService.BACKOFF_DELAYS[:max_retries]
                        }
                        delivery.save()
                        
                        current_app.logger.warning(
                            f"Webhook failed for {url} after {attempt_num} attempts: {error_msg} "
                            f"(delivery_id: {delivery.id})"
                        )
                        
                        return {
                            "status": "failed",
                            "delivery_id": str(delivery.id),
                            "attempt_count": attempt_num,
                            "message": f"Webhook failed after {attempt_num} attempts",
                            "error": error_msg,
                            "status_code": response.status_code
                        }
                    
            except requests.exceptions.Timeout:
                error_msg = f"Request timeout after {timeout} seconds"
                delivery.error_message = error_msg
                
                if attempt < max_retries - 1:
                    # Schedule retry with exponential backoff and jitter
                    backoff_delay = WebhookService._calculate_backoff(attempt)
                    next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff_delay)
                    delivery.next_retry_at = next_retry_at
                    delivery.metadata = {
                        'error_type': 'timeout',
                        'backoff_delay': backoff_delay,
                        'retry_schedule': WebhookService.BACKOFF_DELAYS[:max_retries]
                    }
                    delivery.save()
                    
                    current_app.logger.warning(
                        f"Webhook attempt {attempt_num}/{max_retries} timed out for {url}. "
                        f"Retrying in {backoff_delay:.2f}s (delivery_id: {delivery.id})"
                    )
                    
                    # Wait for backoff delay
                    time.sleep(backoff_delay)
                    continue
                else:
                    # Last attempt - mark as failed
                    delivery.status = 'failed'
                    delivery.completed_at = datetime.now(timezone.utc)
                    delivery.save()
                    
                    current_app.logger.warning(
                        f"Webhook failed for {url} after {attempt_num} attempts (timeout) "
                        f"(delivery_id: {delivery.id})"
                    )
                    
                    return {
                        "status": "failed",
                        "delivery_id": str(delivery.id),
                        "attempt_count": attempt_num,
                        "message": f"Webhook failed after {attempt_num} attempts (timeout)",
                        "error": error_msg
                    }
                    
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error: {str(e)}"
                delivery.error_message = error_msg
                
                if attempt < max_retries - 1:
                    # Schedule retry with exponential backoff and jitter
                    backoff_delay = WebhookService._calculate_backoff(attempt)
                    next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff_delay)
                    delivery.next_retry_at = next_retry_at
                    delivery.metadata = {
                        'error_type': 'connection',
                        'backoff_delay': backoff_delay,
                        'retry_schedule': WebhookService.BACKOFF_DELAYS[:max_retries]
                    }
                    delivery.save()
                    
                    current_app.logger.warning(
                        f"Webhook attempt {attempt_num}/{max_retries} connection error for {url}: {error_msg}. "
                        f"Retrying in {backoff_delay:.2f}s (delivery_id: {delivery.id})"
                    )
                    
                    # Wait for backoff delay
                    time.sleep(backoff_delay)
                    continue
                else:
                    # Last attempt - mark as failed
                    delivery.status = 'failed'
                    delivery.completed_at = datetime.now(timezone.utc)
                    delivery.save()
                    
                    current_app.logger.warning(
                        f"Webhook failed for {url} after {attempt_num} attempts (connection error) "
                        f"(delivery_id: {delivery.id})"
                    )
                    
                    return {
                        "status": "failed",
                        "delivery_id": str(delivery.id),
                        "attempt_count": attempt_num,
                        "message": f"Webhook failed after {attempt_num} attempts (connection error)",
                        "error": error_msg
                    }
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Request error: {str(e)}"
                delivery.error_message = error_msg
                
                # Last attempt - mark as failed
                delivery.status = 'failed'
                delivery.completed_at = datetime.now(timezone.utc)
                delivery.save()
                
                current_app.logger.error(
                    f"Webhook attempt {attempt_num}/{max_retries} error for {url}: {error_msg} "
                    f"(delivery_id: {delivery.id})"
                )
                
                return {
                    "status": "failed",
                    "delivery_id": str(delivery.id),
                    "attempt_count": attempt_num,
                    "message": f"Webhook failed after {attempt_num} attempts",
                    "error": error_msg
                }
        
        # This should not be reached, but just in case
        delivery.status = 'failed'
        delivery.completed_at = datetime.now(timezone.utc)
        delivery.save()
        return {
            "status": "failed",
            "delivery_id": str(delivery.id),
            "attempt_count": max_retries,
            "message": f"Webhook failed after {max_retries} attempts",
            "error": "Unknown error"
        }
    
    @staticmethod
    def get_webhook_status(delivery_id: str) -> Optional[Dict[str, Any]]:
        """
        Get delivery status for a webhook.
        
        Args:
            delivery_id: The ID of the webhook delivery record
        
        Returns:
            Dictionary with delivery status and details, or None if not found
        """
        try:
            delivery = WebhookDelivery.objects.get(id=delivery_id)
            return delivery.to_dict()
        except WebhookDelivery.DoesNotExist:
            return None
    
    @staticmethod
    def get_webhook_history(
        form_id: Optional[str] = None,
        webhook_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Retrieve delivery history for webhooks.
        
        Args:
            form_id: Filter by form ID (optional)
            webhook_id: Filter by webhook ID (optional)
            status: Filter by status (optional)
            page: Page number (default: 1)
            per_page: Number of items per page (default: 20)
        
        Returns:
            Dictionary with delivery history:
            {
                "deliveries": [...],
                "total": int,
                "page": int,
                "per_page": int,
                "total_pages": int
            }
        """
        query = {}
        
        if form_id:
            query['form_id'] = form_id
        
        if webhook_id:
            query['webhook_id'] = webhook_id
        
        if status:
            query['status'] = status
        
        # Count total deliveries matching the query
        total = WebhookDelivery.objects(**query).count()
        
        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page
        skip = (page - 1) * per_page
        
        # Get deliveries for the current page
        deliveries = WebhookDelivery.objects(**query).order_by('-created_at').skip(skip).limit(per_page)
        
        return {
            "deliveries": [delivery.to_dict() for delivery in deliveries],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    
    @staticmethod
    def retry_webhook(delivery_id: str, reset_count: bool = False) -> Dict[str, Any]:
        """
        Retry a failed webhook delivery.
        
        Args:
            delivery_id: The ID of the webhook delivery record
            reset_count: Whether to reset the attempt count (default: False)
        
        Returns:
            Dictionary with retry status and details
        """
        try:
            delivery = WebhookDelivery.objects.get(id=delivery_id)
            
            if not delivery.is_retryable():
                return {
                    "status": "error",
                    "message": f"Webhook delivery is not retryable (status: {delivery.status}, attempts: {delivery.attempt_count}/{delivery.max_retries})"
                }
            
            # Reset attempt count if requested
            if reset_count:
                delivery.attempt_count = 0
            
            # Get the original parameters
            url = delivery.url
            payload = delivery.payload
            webhook_id = delivery.webhook_id
            form_id = delivery.form_id
            created_by = delivery.created_by
            max_retries = delivery.max_retries
            
            # Delete the old delivery record and create a new one
            # This ensures a clean retry without any previous state
            old_delivery_id = str(delivery.id)
            delivery.delete()
            
            # Send the webhook again
            result = WebhookService.send_webhook(
                url=url,
                payload=payload,
                webhook_id=webhook_id,
                form_id=form_id,
                created_by=created_by,
                max_retries=max_retries
            )
            
            result['previous_delivery_id'] = old_delivery_id
            return result
            
        except WebhookDelivery.DoesNotExist:
            return {
                "status": "error",
                "message": "Webhook delivery not found"
            }
    
    @staticmethod
    def cancel_webhook(delivery_id: str) -> Dict[str, Any]:
        """
        Cancel a pending or retrying webhook delivery.
        
        Args:
            delivery_id: The ID of the webhook delivery record
        
        Returns:
            Dictionary with cancellation status and details
        """
        try:
            delivery = WebhookDelivery.objects.get(id=delivery_id)
            
            if delivery.is_completed():
                return {
                    "status": "error",
                    "message": f"Webhook delivery is already {delivery.status} and cannot be cancelled"
                }
            
            # Update status to cancelled
            delivery.status = 'cancelled'
            delivery.completed_at = datetime.now(timezone.utc)
            delivery.save()
            
            current_app.logger.info(
                f"Webhook delivery cancelled (delivery_id: {delivery_id})"
            )
            
            return {
                "status": "success",
                "delivery_id": str(delivery.id),
                "message": "Webhook delivery cancelled successfully"
            }
            
        except WebhookDelivery.DoesNotExist:
            return {
                "status": "error",
                "message": "Webhook delivery not found"
            }
    
    @staticmethod
    def get_webhook_logs(
        url: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Retrieve webhook logs with optional filtering (legacy method).
        
        Args:
            url: Filter by webhook URL (optional)
            status: Filter by status (optional)
            limit: Maximum number of logs to return (default: 100)
        
        Returns:
            List of WebhookLog documents as dictionaries
        """
        query = {}
        
        if url:
            query['url'] = url
        
        if status:
            query['status'] = status
        
        logs = WebhookLog.objects(**query).order_by('-created_at').limit(limit)
        
        return [
            {
                'id': str(log.id),
                'url': log.url,
                'payload': log.payload,
                'status': log.status,
                'attempt_count': log.attempt_count,
                'last_attempt': log.last_attempt.isoformat() if log.last_attempt else None,
                'error_message': log.error_message,
                'status_code': log.status_code,
                'created_at': log.created_at.isoformat(),
                'metadata': log.metadata
            }
            for log in logs
        ]
    
    @staticmethod
    def get_webhook_log_by_id(log_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific webhook log by ID (legacy method).
        
        Args:
            log_id: The ID of the webhook log
        
        Returns:
            Dictionary with webhook log details or None if not found
        """
        try:
            log = WebhookLog.objects.get(id=log_id)
            return {
                'id': str(log.id),
                'url': log.url,
                'payload': log.payload,
                'status': log.status,
                'attempt_count': log.attempt_count,
                'last_attempt': log.last_attempt.isoformat() if log.last_attempt else None,
                'error_message': log.error_message,
                'status_code': log.status_code,
                'created_at': log.created_at.isoformat(),
                'metadata': log.metadata
            }
        except WebhookLog.DoesNotExist:
            return None
