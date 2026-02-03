import requests
import time
from typing import Dict, Any, Optional
from flask import current_app
from app.models.WebhookLog import WebhookLog


class WebhookService:
    """
    Service for reliable webhook delivery with retry mechanism and failure logging.
    """
    
    @staticmethod
    def send_webhook(
        url: str,
        payload: Dict[str, Any],
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Send a webhook with exponential backoff retry logic.
        
        Args:
            url: The webhook URL to send to
            payload: The JSON payload to send
            max_retries: Maximum number of retry attempts (default: 3)
            headers: Optional custom headers
            timeout: Request timeout in seconds (default: 10)
        
        Returns:
            Dictionary with delivery status and details:
            {
                "status": "success" | "failed",
                "attempt_count": int,
                "log_id": str,
                "message": str,
                "error": Optional[str]
            }
        """
        # Create initial log entry
        log = WebhookLog(
            url=url,
            payload=payload,
            status='pending',
            attempt_count=0
        )
        log.save()
        
        # Default headers
        if headers is None:
            headers = {
                "Content-Type": "application/json"
            }
        
        # Retry loop with exponential backoff
        for attempt in range(max_retries):
            attempt_num = attempt + 1
            log.attempt_count = attempt_num
            log.last_attempt = log.last_attempt or log.created_at
            
            # Update status to retrying if not first attempt
            if attempt > 0:
                log.status = 'retrying'
                log.save()
            
            try:
                # Send the webhook request
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                )
                
                # Check if request was successful (2xx status codes)
                if response.status_code >= 200 and response.status_code < 300:
                    # Success!
                    log.status = 'success'
                    log.status_code = response.status_code
                    log.metadata = {
                        'response_body': response.text[:1000],  # Limit response body size
                        'headers': dict(response.headers)
                    }
                    log.save()
                    
                    current_app.logger.info(
                        f"Webhook delivered successfully to {url} "
                        f"(attempt {attempt_num}/{max_retries})"
                    )
                    
                    return {
                        "status": "success",
                        "attempt_count": attempt_num,
                        "log_id": str(log.id),
                        "message": f"Webhook delivered successfully on attempt {attempt_num}",
                        "status_code": response.status_code
                    }
                else:
                    # Non-2xx response - treat as failure
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    log.error_message = error_msg
                    log.status_code = response.status_code
                    log.metadata = {
                        'response_body': response.text[:1000],
                        'headers': dict(response.headers)
                    }
                    log.save()
                    
                    current_app.logger.warning(
                        f"Webhook attempt {attempt_num}/{max_retries} failed for {url}: {error_msg}"
                    )
                    
                    # If this was the last attempt, mark as failed
                    if attempt == max_retries - 1:
                        log.status = 'failed'
                        log.save()
                        return {
                            "status": "failed",
                            "attempt_count": attempt_num,
                            "log_id": str(log.id),
                            "message": f"Webhook failed after {max_retries} attempts",
                            "error": error_msg,
                            "status_code": response.status_code
                        }
                    
            except requests.exceptions.Timeout:
                error_msg = f"Request timeout after {timeout} seconds"
                log.error_message = error_msg
                log.save()
                
                current_app.logger.warning(
                    f"Webhook attempt {attempt_num}/{max_retries} timed out for {url}"
                )
                
                if attempt == max_retries - 1:
                    log.status = 'failed'
                    log.save()
                    return {
                        "status": "failed",
                        "attempt_count": attempt_num,
                        "log_id": str(log.id),
                        "message": f"Webhook failed after {max_retries} attempts (timeout)",
                        "error": error_msg
                    }
                    
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error: {str(e)}"
                log.error_message = error_msg
                log.save()
                
                current_app.logger.warning(
                    f"Webhook attempt {attempt_num}/{max_retries} connection error for {url}: {error_msg}"
                )
                
                if attempt == max_retries - 1:
                    log.status = 'failed'
                    log.save()
                    return {
                        "status": "failed",
                        "attempt_count": attempt_num,
                        "log_id": str(log.id),
                        "message": f"Webhook failed after {max_retries} attempts (connection error)",
                        "error": error_msg
                    }
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Request error: {str(e)}"
                log.error_message = error_msg
                log.save()
                
                current_app.logger.error(
                    f"Webhook attempt {attempt_num}/{max_retries} error for {url}: {error_msg}"
                )
                
                if attempt == max_retries - 1:
                    log.status = 'failed'
                    log.save()
                    return {
                        "status": "failed",
                        "attempt_count": attempt_num,
                        "log_id": str(log.id),
                        "message": f"Webhook failed after {max_retries} attempts",
                        "error": error_msg
                    }
            
            # Exponential backoff: 1s, 2s, 4s, 8s, ...
            if attempt < max_retries - 1:
                backoff_time = 2 ** attempt  # 1, 2, 4, 8, ...
                current_app.logger.info(
                    f"Retrying webhook to {url} in {backoff_time}s "
                    f"(attempt {attempt_num + 1}/{max_retries})"
                )
                time.sleep(backoff_time)
        
        # This should not be reached, but just in case
        log.status = 'failed'
        log.save()
        return {
            "status": "failed",
            "attempt_count": max_retries,
            "log_id": str(log.id),
            "message": f"Webhook failed after {max_retries} attempts",
            "error": "Unknown error"
        }
    
    @staticmethod
    def get_webhook_logs(
        url: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Retrieve webhook logs with optional filtering.
        
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
        Retrieve a specific webhook log by ID.
        
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
