"""
SMS API Routes

API endpoints for sending SMS and managing SMS providers.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from typing import Any

from app.services.sms import SMSService


sms_bp = Blueprint("sms", __name__)


@sms_bp.route("/send", methods=["POST"])
@jwt_required()
def send_sms():
    """
    Send an SMS message.
    
    Request Body:
    {
        "to": "+1234567890",
        "message": "Your SMS message",
        "form_id": "form_id" (optional),
        "provider_id": "twilio" (optional),
        "max_retries": 3 (optional)
    }
    
    Response:
    {
        "status": "success" | "failed",
        "sms_id": "delivery_id",
        "provider": "Twilio",
        "message_id": "provider_message_id",
        "status": "sent",
        "attempt_count": 1,
        "error": str (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        to = data.get("to")
        message = data.get("message")
        form_id = data.get("form_id")
        provider_id = data.get("provider_id")
        max_retries = data.get("max_retries", 3)
        
        # Validate required fields
        if not to:
            return jsonify({"error": "to (recipient phone number) is required"}), 400
        
        if not message:
            return jsonify({"error": "message is required"}), 400
        
        if not isinstance(message, str):
            return jsonify({"error": "message must be a string"}), 400
        
        if len(message) > 1600:
            return jsonify({"error": "message exceeds maximum length of 1600 characters"}), 400
        
        if not isinstance(max_retries, int) or max_retries < 0:
            return jsonify({"error": "max_retries must be a non-negative integer"}), 400
        
        # Get current user
        created_by = get_jwt_identity()
        
        # Send SMS using the service
        sms_service = SMSService()
        result = sms_service.send_sms(
            to=to,
            message=message,
            form_id=form_id,
            provider_id=provider_id,
            created_by=created_by,
            max_retries=max_retries
        )
        
        status_code = 200 if result.get("status") == "success" else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        current_app.logger.error(f"SMS send error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route("/providers", methods=["GET"])
@jwt_required()
def list_providers():
    """
    List all configured SMS providers.
    
    Response:
    {
        "providers": [
            {
                "provider_id": "twilio",
                "provider_name": "Twilio",
                "provider_type": "twilio",
                "enabled": true,
                "priority": 1,
                "is_default": true,
                "available": true
            }
        ]
    }
    """
    try:
        sms_service = SMSService()
        providers = sms_service.get_providers()
        
        return jsonify({"providers": providers}), 200
        
    except Exception as e:
        current_app.logger.error(f"List providers error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route("/providers", methods=["POST"])
@jwt_required()
def create_provider():
    """
    Create a new SMS provider configuration.
    
    Request Body:
    {
        "provider_id": "twilio",
        "provider_name": "Twilio",
        "provider_type": "twilio",
        "config": {
            "account_sid": "...",
            "auth_token": "...",
            "from_number": "+1234567890"
        },
        "priority": 1,
        "description": "Primary SMS provider"
    }
    
    Response:
    {
        "status": "success",
        "provider": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        provider_id = data.get("provider_id")
        provider_name = data.get("provider_name")
        provider_type = data.get("provider_type")
        config = data.get("config", {})
        priority = data.get("priority", 100)
        description = data.get("description")
        
        # Validate required fields
        if not provider_id:
            return jsonify({"error": "provider_id is required"}), 400
        
        if not provider_name:
            return jsonify({"error": "provider_name is required"}), 400
        
        if not provider_type:
            return jsonify({"error": "provider_type is required"}), 400
        
        if provider_type not in ['twilio', 'sns', 'aws_sns', 'local_mock']:
            return jsonify({
                "error": "Invalid provider_type. Must be: twilio, sns, aws_sns, or local_mock"
            }), 400
        
        # Get current user
        created_by = get_jwt_identity()
        
        sms_service = SMSService()
        provider = sms_service.create_provider(
            provider_id=provider_id,
            provider_name=provider_name,
            provider_type=provider_type,
            config=config,
            created_by=created_by,
            priority=priority,
            description=description
        )
        
        return jsonify({
            "status": "success",
            "provider": provider.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Create provider error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route("/providers/<provider_id>", methods=["PUT"])
@jwt_required()
def update_provider(provider_id: str):
    """
    Update an SMS provider configuration.
    
    Path Parameters:
    - provider_id: The provider ID
    
    Request Body:
    {
        "config": {...},
        "enabled": true,
        "priority": 1
    }
    
    Response:
    {
        "status": "success",
        "provider": {...}
    }
    """
    try:
        data = request.get_json() or {}
        updated_by = get_jwt_identity()
        
        sms_service = SMSService()
        provider = sms_service.update_provider(
            provider_id=provider_id,
            config=data.get("config"),
            enabled=data.get("enabled"),
            priority=data.get("priority"),
            updated_by=updated_by
        )
        
        if not provider:
            return jsonify({"error": "Provider not found"}), 404
        
        return jsonify({
            "status": "success",
            "provider": provider.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update provider error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route("/providers/<provider_id>", methods=["DELETE"])
@jwt_required()
def delete_provider(provider_id: str):
    """
    Delete an SMS provider configuration.
    
    Path Parameters:
    - provider_id: The provider ID
    
    Response:
    {
        "status": "success",
        "message": "Provider deleted successfully"
    }
    """
    try:
        sms_service = SMSService()
        deleted = sms_service.delete_provider(provider_id)
        
        if not deleted:
            return jsonify({"error": "Provider not found"}), 404
        
        return jsonify({
            "status": "success",
            "message": "Provider deleted successfully"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete provider error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route("/providers/<provider_id>/status", methods=["GET"])
@jwt_required()
def get_provider_status(provider_id: str):
    """
    Get the status of a specific SMS provider.
    
    Path Parameters:
    - provider_id: The provider ID
    
    Response:
    {
        "provider_id": "twilio",
        "provider_name": "Twilio",
        "enabled": true,
        "available": true,
        "info": {...}
    }
    """
    try:
        sms_service = SMSService()
        statuses = sms_service.get_provider_status(provider_id)
        
        if not statuses:
            return jsonify({"error": "Provider not found"}), 404
        
        return jsonify(statuses[0]), 200
        
    except Exception as e:
        current_app.logger.error(f"Get provider status error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route("/deliveries", methods=["GET"])
@jwt_required()
def get_deliveries():
    """
    Get SMS delivery history.
    
    Query Parameters:
    - form_id: Filter by form ID (optional)
    - provider: Filter by provider (optional)
    - status: Filter by status (optional)
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    
    Response:
    {
        "deliveries": [...],
        "total": 100,
        "page": 1,
        "per_page": 20,
        "total_pages": 5
    }
    """
    try:
        form_id = request.args.get("form_id")
        provider = request.args.get("provider")
        status = request.args.get("status")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        
        # Validate pagination
        if page < 1:
            return jsonify({"error": "page must be a positive integer"}), 400
        
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "per_page must be between 1 and 100"}), 400
        
        # Validate status
        if status and status not in ['pending', 'sent', 'delivered', 'failed']:
            return jsonify({
                "error": "Invalid status. Must be: pending, sent, delivered, or failed"
            }), 400
        
        sms_service = SMSService()
        result = sms_service.get_delivery_history(
            form_id=form_id,
            provider=provider,
            status=status,
            page=page,
            per_page=per_page
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Get deliveries error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route("/deliveries/<sms_id>/status", methods=["GET"])
@jwt_required()
def get_delivery_status(sms_id: str):
    """
    Get the status of a specific SMS delivery.
    
    Path Parameters:
    - sms_id: The SMS delivery ID
    
    Response:
    {
        "sms_id": "...",
        "recipient_number": "+1234567890",
        "message": "...",
        "status": "sent",
        "provider": "twilio",
        ...
    }
    """
    try:
        sms_service = SMSService()
        status = sms_service.get_delivery_status(sms_id)
        
        if not status:
            return jsonify({"error": "SMS delivery not found"}), 404
        
        return jsonify(status), 200
        
    except Exception as e:
        current_app.logger.error(f"Get delivery status error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route("/deliveries/<sms_id>/retry", methods=["POST"])
@jwt_required()
def retry_delivery(sms_id: str):
    """
    Retry a failed SMS delivery.
    
    Path Parameters:
    - sms_id: The SMS delivery ID
    
    Response:
    {
        "status": "success" | "error",
        "sms_id": "...",
        ...
    }
    """
    try:
        sms_service = SMSService()
        result = sms_service.retry_sms(sms_id)
        
        if result.get("status") == "error":
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Retry delivery error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route("/validate", methods=["POST"])
@jwt_required()
def validate_number():
    """
    Validate a phone number.
    
    Request Body:
    {
        "phone_number": "+1234567890"
    }
    
    Response:
    {
        "is_valid": true,
        "formatted_number": "+1234567890",
        "country_code": "1",
        "carrier": "AT&T",
        "validated_with": "Twilio"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        phone_number = data.get("phone_number")
        
        if not phone_number:
            return jsonify({"error": "phone_number is required"}), 400
        
        sms_service = SMSService()
        result = sms_service.validate_number(phone_number)
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Validate number error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route("/test", methods=["POST"])
@jwt_required()
def test_sms():
    """
    Send a test SMS using the default or specified provider.
    
    Request Body:
    {
        "to": "+1234567890",
        "provider_id": "twilio" (optional)
    }
    
    Response:
    {
        "status": "success" | "failed",
        "sms_id": "...",
        "message": "Test SMS sent successfully"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        to = data.get("to")
        provider_id = data.get("provider_id")
        
        if not to:
            return jsonify({"error": "to (recipient phone number) is required"}), 400
        
        created_by = get_jwt_identity()
        
        sms_service = SMSService()
        result = sms_service.send_sms(
            to=to,
            message="This is a test SMS from the Form Management API.",
            form_id="test",
            webhook_id="test",
            provider_id=provider_id,
            created_by=created_by,
            max_retries=3
        )
        
        status_code = 200 if result.get("status") == "success" else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        current_app.logger.error(f"Test SMS error: {str(e)}")
        return jsonify({"error": str(e)}), 500
