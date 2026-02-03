from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.services.webhook_service import WebhookService


webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.route("/test", methods=["POST"])
@jwt_required()
def test_webhook():
    """
    Test webhook delivery with retry mechanism.
    
    Request Body:
    {
        "url": "https://example.com/webhook",
        "payload": {
            "event": "test",
            "data": {"key": "value"}
        },
        "max_retries": 3,
        "headers": {
            "Authorization": "Bearer token"
        }
    }
    
    Response:
    {
        "status": "success" | "failed",
        "attempt_count": int,
        "log_id": str,
        "message": str,
        "error": str (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        url = data.get("url")
        payload = data.get("payload")
        max_retries = data.get("max_retries", 3)
        headers = data.get("headers")
        
        # Validate required fields
        if not url:
            return jsonify({"error": "url is required"}), 400
        
        if not payload:
            return jsonify({"error": "payload is required"}), 400
        
        if not isinstance(payload, dict):
            return jsonify({"error": "payload must be a dictionary"}), 400
        
        if not isinstance(max_retries, int) or max_retries < 1:
            return jsonify({"error": "max_retries must be a positive integer"}), 400
        
        # Send webhook using the service
        result = WebhookService.send_webhook(
            url=url,
            payload=payload,
            max_retries=max_retries,
            headers=headers
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Webhook test error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@webhooks_bp.route("/logs", methods=["GET"])
@jwt_required()
def get_webhook_logs():
    """
    Retrieve webhook logs with optional filtering.
    
    Query Parameters:
    - url: Filter by webhook URL (optional)
    - status: Filter by status (optional): pending, success, failed, retrying
    - limit: Maximum number of logs to return (default: 100)
    
    Response:
    [
        {
            "id": "log_id",
            "url": "https://example.com/webhook",
            "payload": {...},
            "status": "success",
            "attempt_count": 1,
            "last_attempt": "2026-02-03T09:00:00Z",
            "error_message": null,
            "status_code": 200,
            "created_at": "2026-02-03T09:00:00Z",
            "metadata": {...}
        }
    ]
    """
    try:
        url = request.args.get("url")
        status = request.args.get("status")
        limit = request.args.get("limit", 100, type=int)
        
        # Validate status if provided
        if status and status not in ['pending', 'success', 'failed', 'retrying']:
            return jsonify({
                "error": "Invalid status. Must be one of: pending, success, failed, retrying"
            }), 400
        
        # Validate limit
        if limit < 1 or limit > 1000:
            return jsonify({"error": "limit must be between 1 and 1000"}), 400
        
        # Get logs
        logs = WebhookService.get_webhook_logs(
            url=url,
            status=status,
            limit=limit
        )
        
        return jsonify({
            "count": len(logs),
            "logs": logs
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get webhook logs error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@webhooks_bp.route("/logs/<log_id>", methods=["GET"])
@jwt_required()
def get_webhook_log(log_id: str):
    """
    Retrieve a specific webhook log by ID.
    
    Path Parameters:
    - log_id: The ID of the webhook log
    
    Response:
    {
        "id": "log_id",
        "url": "https://example.com/webhook",
        "payload": {...},
        "status": "success",
        "attempt_count": 1,
        "last_attempt": "2026-02-03T09:00:00Z",
        "error_message": null,
        "status_code": 200,
        "created_at": "2026-02-03T09:00:00Z",
        "metadata": {...}
    }
    """
    try:
        log = WebhookService.get_webhook_log_by_id(log_id)
        
        if not log:
            return jsonify({"error": "Webhook log not found"}), 404
        
        return jsonify(log), 200
        
    except Exception as e:
        current_app.logger.error(f"Get webhook log error: {str(e)}")
        return jsonify({"error": str(e)}), 500
