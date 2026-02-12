"""
SMS Route - External API Wrapper

This module provides a simple SMS endpoint that forwards requests
to the external AIIMS SMS API.

Endpoints:
    POST /api/v1/sms/single - Send a single SMS message
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
import logging

from app.services.external_sms_service import get_sms_service, SMSResult

logger = logging.getLogger(__name__)

sms_bp = Blueprint("sms", __name__, url_prefix="/api/v1/sms")


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated (simplified - adapt to your auth system)
        if not hasattr(g, 'current_user') and not g.get('is_authenticated'):
            logger.warning("SMS auth check failed: Authentication required")
            return jsonify({"error": "Authentication required"}), 401
        logger.info("SMS auth check successful")
        return f(*args, **kwargs)
    return decorated_function


@sms_bp.route("/single", methods=["POST"])
@require_auth
def send_single_sms():
    """
    Send a single SMS message via external API.
    
    Request Body:
        {
            "mobile": "9899378106",
            "message": "Hello from AIIMS"
        }
    
    Response:
        {
            "success": true,
            "message_id": "...",
            "status_code": 200
        }
    """
    try:
        logger.info("--- Send Single SMS branch started ---")
        data = request.get_json()
        
        if not data:
            logger.warning("Send SMS failed: Request body missing")
            return jsonify({"error": "Request body is required"}), 400
        
        mobile = data.get("mobile")
        message = data.get("message")
        
        # Validate required fields
        if not mobile:
            logger.warning("Send SMS failed: Mobile number missing")
            return jsonify({"error": "mobile field is required"}), 400
        if not message:
            logger.warning("Send SMS failed: Message content missing")
            return jsonify({"error": "message field is required"}), 400
        
        # Validate mobile format (basic validation)
        if not isinstance(mobile, str):
            logger.debug(f"Converting mobile to string: {mobile}")
            mobile = str(mobile)
        
        mobile = mobile.strip()
        if len(mobile) < 10 or len(mobile) > 15:
            logger.warning(f"Send SMS failed: Invalid mobile format '{mobile}'")
            return jsonify({"error": "Invalid mobile number format"}), 400
        
        # Send SMS via external service
        logger.debug(f"Calling external SMS service for {mobile}")
        sms_service = get_sms_service()
        result = sms_service.send_sms(mobile, message)
        
        if result.success:
            logger.info(f"SMS sent successfully to {mobile} (MessageID: {result.message_id})")
            return jsonify({
                "success": True,
                "message_id": result.message_id,
                "status_code": result.status_code
            }), 200
        else:
            logger.error(f"Failed to send SMS to {mobile}: {result.error_message}")
            return jsonify({
                "success": False,
                "error": result.error_message,
                "status_code": result.status_code or 500
            }), result.status_code or 500
            
    except Exception as e:
        logger.exception(f"Error sending SMS: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@sms_bp.route("/otp", methods=["POST"])
@require_auth
def send_otp():
    """
    Send an OTP via SMS.
    
    Request Body:
        {
            "mobile": "9899378106",
            "otp": "123456"
        }
    
    Response:
        {
            "success": true,
            "message_id": "...",
            "status_code": 200
        }
    """
    try:
        logger.info("--- Send OTP SMS branch started ---")
        data = request.get_json()
        
        if not data:
            logger.warning("Send OTP failed: Request body missing")
            return jsonify({"error": "Request body is required"}), 400
        
        mobile = data.get("mobile")
        otp = data.get("otp")
        
        # Validate required fields
        if not mobile:
            logger.warning("Send OTP failed: Mobile number missing")
            return jsonify({"error": "mobile field is required"}), 400
        if not otp:
            logger.warning("Send OTP failed: OTP missing")
            return jsonify({"error": "otp field is required"}), 400
        
        # Send OTP via external service
        logger.debug(f"Calling external SMS service (OTP) for {mobile}")
        sms_service = get_sms_service()
        result = sms_service.send_otp(mobile, otp)
        
        if result.success:
            logger.info(f"OTP sent successfully to {mobile} (MessageID: {result.message_id})")
            return jsonify({
                "success": True,
                "message_id": result.message_id,
                "status_code": result.status_code
            }), 200
        else:
            logger.error(f"Failed to send OTP to {mobile}: {result.error_message}")
            return jsonify({
                "success": False,
                "error": result.error_message,
                "status_code": result.status_code or 500
            }), result.status_code or 500
            
    except Exception as e:
        logger.exception(f"Error sending OTP: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@sms_bp.route("/notify", methods=["POST"])
@require_auth
def send_notification():
    """
    Send a notification via SMS.
    
    Request Body:
        {
            "mobile": "9899378106",
            "title": "Appointment Reminder",
            "body": "Your appointment is tomorrow at 10 AM"
        }
    
    Response:
        {
            "success": true,
            "message_id": "...",
            "status_code": 200
        }
    """
    try:
        logger.info("--- Send Notification branch started ---")
        data = request.get_json()
        
        if not data:
            logger.warning("Send notification failed: Request body missing")
            return jsonify({"error": "Request body is required"}), 400
        
        mobile = data.get("mobile")
        title = data.get("title", "")
        body = data.get("body", "")
        
        # Validate required fields
        if not mobile:
            logger.warning("Send notification failed: Mobile number missing")
            return jsonify({"error": "mobile field is required"}), 400
        if not body:
            logger.warning("Send notification failed: Body content missing")
            return jsonify({"error": "body field is required"}), 400
        
        # Send notification via external service
        logger.debug(f"Calling external SMS service (Notification) for {mobile}")
        sms_service = get_sms_service()
        result = sms_service.send_notification(mobile, title, body)
        
        if result.success:
            logger.info(f"Notification sent successfully to {mobile} (MessageID: {result.message_id})")
            return jsonify({
                "success": True,
                "message_id": result.message_id,
                "status_code": result.status_code
            }), 200
        else:
            logger.error(f"Failed to send notification to {mobile}: {result.error_message}")
            return jsonify({
                "success": False,
                "error": result.error_message,
                "status_code": result.status_code or 500
            }), result.status_code or 500
            
    except Exception as e:
        logger.exception(f"Error sending notification: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# Health check endpoint
@sms_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for the SMS service.
    
    This endpoint checks if the external SMS API is reachable.
    """
    try:
        logger.info("--- SMS Health Check branch started ---")
        sms_service = get_sms_service()
        # Just check if we can make a request (without sending actual SMS)
        # For now, just return success if the service is configured
        if sms_service.api_url and sms_service.api_token:
            logger.info("SMS service is healthy and configured")
            return jsonify({
                "status": "healthy",
                "service": "external_sms",
                "api_url": sms_service.api_url
            }), 200
        else:
            logger.error("SMS service is unhealthy: API not configured")
            return jsonify({
                "status": "unhealthy",
                "service": "external_sms",
                "error": "SMS API not configured"
            }), 503
            
    except Exception as e:
        logger.exception(f"SMS health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "service": "external_sms",
            "error": str(e)
        }), 503
