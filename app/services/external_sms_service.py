"""
External SMS Service for AIIMS RPC Application

This service provides a simple wrapper for sending SMS via the external
AIIMS SMS API endpoint.

API Endpoint: https://rpcapplication.aiims.edu/services/api/v1/sms/single

Example usage:
    curl --location 'https://rpcapplication.aiims.edu/services/api/v1/sms/single' \
        --header 'Content-Type: application/json' \
        --header 'Authorization: Bearer <TOKEN>' \
        --data '{
          "mobile": "9899378106",
          "message": "Hello from AIIMS"
        }'
"""

import requests
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SMSResult:
    """Result of an SMS send operation."""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message_id": self.message_id,
            "error_message": self.error_message,
            "status_code": self.status_code
        }


class ExternalSMSService:
    """
    Service for sending SMS via external AIIMS RPC API.
    
    This service acts as a thin wrapper around the external SMS API,
    forwarding requests from the application to the remote endpoint.
    """
    
    def __init__(self, api_url: str = None, api_token: str = None):
        """
        Initialize the external SMS service.
        
        Args:
            api_url: The external SMS API endpoint URL
            api_token: The authorization bearer token
        """
        from app.config import Config
        
        self.api_url = api_url or Config.SMS_API_URL
        self.api_token = api_token or Config.SMS_API_TOKEN
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        })
    
    def send_sms(self, mobile: str, message: str) -> SMSResult:
        """
        Send an SMS message via the external API.
        
        Args:
            mobile: The recipient's mobile number
            message: The message content to send
            
        Returns:
            SMSResult indicating success or failure
        """
        payload = {
            "mobile": mobile,
            "message": message
        }
        
        try:
            logger.info(f"Sending SMS to {mobile}: {message[:50]}...")
            
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            
            self._log_response(response)
            
            if response.status_code in (200, 201):
                return SMSResult(
                    success=True,
                    message_id=response.text or None,
                    status_code=response.status_code
                )
            else:
                return SMSResult(
                    success=False,
                    error_message=response.text or f"HTTP {response.status_code}",
                    status_code=response.status_code
                )
                
        except requests.exceptions.Timeout:
            error_msg = "SMS API request timed out"
            logger.error(error_msg)
            return SMSResult(success=False, error_message=error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"SMS API request failed: {str(e)}"
            logger.error(error_msg)
            return SMSResult(success=False, error_message=error_msg)
    
    def send_otp(self, mobile: str, otp: str) -> SMSResult:
        """
        Send an OTP message via the external API.
        
        Args:
            mobile: The recipient's mobile number
            otp: The OTP code to send
            
        Returns:
            SMSResult indicating success or failure
        """
        message = f"Your OTP is: {otp}. Valid for 10 minutes. Do not share."
        return self.send_sms(mobile, message)
    
    def send_notification(self, mobile: str, title: str, body: str) -> SMSResult:
        """
        Send a notification message via the external API.
        
        Args:
            mobile: The recipient's mobile number
            title: The notification title
            body: The notification body
            
        Returns:
            SMSResult indicating success or failure
        """
        message = f"{title}: {body}"
        return self.send_sms(mobile, message)
    
    def _log_response(self, response: requests.Response) -> None:
        """Log the API response for debugging."""
        logger.debug(f"SMS API Response: {response.status_code} - {response.text[:200]}")


# Singleton instance for application-wide use
_sms_service: Optional[ExternalSMSService] = None


def get_sms_service() -> ExternalSMSService:
    """Get the singleton SMS service instance."""
    global _sms_service
    if _sms_service is None:
        _sms_service = ExternalSMSService()
    return _sms_service
