from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from app.services.webhook_service import WebhookService
import logging

webhooks_bp = Blueprint("webhooks", __name__)
logger = logging.getLogger(__name__)


@webhooks_bp.route("/deliver", methods=["POST"])
@jwt_required()
def deliver_webhook():
    """
    Trigger webhook delivery with retry mechanism.
    
    Request Body:
    {
        "url": "https://example.com/webhook",
        "webhook_id": "webhook_config_id",
        "form_id": "form_id",
        "payload": {
            "event": "submitted",
            "data": {"key": "value"}
        },
        "max_retries": 5,
        "headers": {
            "Authorization": "Bearer token"
        },
        "timeout": 10,
        "schedule_for": "2026-02-04T10:00:00Z"
    }
    
    Response:
    {
        "status": "success" | "failed" | "scheduled",
        "delivery_id": "delivery_id",
        "attempt_count": int,
        "message": str,
        "error": str (optional),
        "next_retry_at": "ISO-8601 timestamp" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        url = data.get("url")
        webhook_id = data.get("webhook_id")
        form_id = data.get("form_id")
        payload = data.get("payload")
        max_retries = data.get("max_retries", 5)
        headers = data.get("headers")
        timeout = data.get("timeout", 10)
        schedule_for_str = data.get("schedule_for")
        
        # Validate required fields
        if not url:
            logger.warning("Deliver Webhook failed: URL missing")
            return jsonify({"error": "url is required"}), 400
        
        if not webhook_id:
            logger.warning("Deliver Webhook failed: webhook_id missing")
            return jsonify({"error": "webhook_id is required"}), 400
        
        if not form_id:
            logger.warning("Deliver Webhook failed: form_id missing")
            return jsonify({"error": "form_id is required"}), 400
        
        if not payload:
            logger.warning("Deliver Webhook failed: payload missing")
            return jsonify({"error": "payload is required"}), 400
        
        if not isinstance(payload, dict):
            logger.warning("Deliver Webhook failed: payload is not a dictionary")
            return jsonify({"error": "payload must be a dictionary"}), 400
        
        if not isinstance(max_retries, int) or max_retries < 0:
            logger.warning(f"Deliver Webhook failed: Invalid max_retries {max_retries}")
            return jsonify({"error": "max_retries must be a non-negative integer"}), 400
        
        if not isinstance(timeout, int) or timeout < 1:
            logger.warning(f"Deliver Webhook failed: Invalid timeout {timeout}")
            return jsonify({"error": "timeout must be a positive integer"}), 400
        
        # Parse schedule_for if provided
        schedule_for = None
        if schedule_for_str:
            logger.debug(f"Parsing schedule_for: {schedule_for_str}")
            try:
                schedule_for = datetime.fromisoformat(schedule_for_str.replace('Z', '+00:00'))
                if schedule_for.tzinfo is None:
                    schedule_for = schedule_for.replace(tzinfo=timezone.utc)
                logger.info(f"Webhook scheduled for: {schedule_for}")
            except ValueError:
                logger.warning(f"Deliver Webhook failed: Invalid schedule_for format {schedule_for_str}")
                return jsonify({"error": "schedule_for must be a valid ISO-8601 datetime"}), 400
        
        # Get current user
        created_by = get_jwt_identity()
        
        # Send webhook using the service
        logger.info(f"Handing off webhook delivery to URL {url} (created_by: {created_by})")
        result = WebhookService.send_webhook(
            url=url,
            payload=payload,
            webhook_id=webhook_id,
            form_id=form_id,
            created_by=created_by,
            max_retries=max_retries,
            headers=headers,
            timeout=timeout,
            schedule_for=schedule_for
        )
        
        logger.info(f"Webhook handoff result: {result.get('status')}")
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Webhook delivery error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@webhooks_bp.route("/<delivery_id>/status", methods=["GET"])
@jwt_required()
def get_webhook_status(delivery_id: str):
    """
    Get webhook delivery status.
    
    Path Parameters:
    - delivery_id: The ID of the webhook delivery
    
    Response:
    {
        "id": "delivery_id",
        "webhook_id": "webhook_config_id",
        "url": "https://example.com/webhook",
        "form_id": "form_id",
        "payload": {...},
        "status": "success",
        "attempt_count": 1,
        "max_retries": 5,
        "last_attempt_at": "2026-02-04T08:00:00Z",
        "next_retry_at": "2026-02-04T08:02:00Z",
        "created_by": "user_id",
        "response_code": 200,
        "response_body": "...",
        "error_message": null,
        "metadata": {...},
        "created_at": "2026-02-04T08:00:00Z",
        "completed_at": "2026-02-04T08:00:00Z"
    }
    """
    try:
        logger.info(f"--- Get Webhook Status branch started for id: {delivery_id} ---")
        status = WebhookService.get_webhook_status(delivery_id)
        
        if not status:
            logger.warning(f"Get Webhook Status failed: ID {delivery_id} not found")
            return jsonify({"error": "Webhook delivery not found"}), 404
        
        logger.info(f"Returning status for webhook: {delivery_id}")
        return jsonify(status), 200
        
    except Exception as e:
        current_app.logger.error(f"Get webhook status error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@webhooks_bp.route("/<delivery_id>/history", methods=["GET"])
@jwt_required()
def get_webhook_history(delivery_id: str):
    """
    Get webhook delivery history for a specific delivery.
    
    Path Parameters:
    - delivery_id: The ID of the webhook delivery
    
    Query Parameters:
    - form_id: Filter by form ID (optional)
    - webhook_id: Filter by webhook ID (optional)
    - status: Filter by status (optional): pending, in_progress, success, failed, retrying, cancelled
    - page: Page number (default: 1)
    - per_page: Number of items per page (default: 20)
    
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
        logger.info(f"--- Get Webhook History branch started for delivery_id: {delivery_id} ---")
        # Parse query parameters
        form_id = request.args.get("form_id")
        webhook_id = request.args.get("webhook_id")
        status = request.args.get("status")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        
        # Validate status if provided
        if status and status not in ['pending', 'in_progress', 'success', 'failed', 'retrying', 'cancelled']:
            logger.warning(f"Get Webhook History failed: Invalid status '{status}'")
            return jsonify({
                "error": "Invalid status. Must be one of: pending, in_progress, success, failed, retrying, cancelled"
            }), 400
        
        # Validate pagination parameters
        if page < 1:
            logger.warning(f"Get Webhook History failed: Invalid page '{page}'")
            return jsonify({"error": "page must be a positive integer"}), 400
        
        if per_page < 1 or per_page > 100:
            logger.warning(f"Get Webhook History failed: Invalid per_page '{per_page}'")
            return jsonify({"error": "per_page must be between 1 and 100"}), 400
        
        # If delivery_id is provided, use it to filter
        # Otherwise, use the query parameters
        if delivery_id:
            logger.info(f"Filtering history by specified delivery_id: {delivery_id}")
            # Get the specific delivery first to get form_id and webhook_id
            status_data = WebhookService.get_webhook_status(delivery_id)
            if not status_data:
                logger.warning(f"Get Webhook History failed: delivery_id {delivery_id} not found")
                return jsonify({"error": "Webhook delivery not found"}), 404
            
            form_id = form_id or status_data.get('form_id')
            webhook_id = webhook_id or status_data.get('webhook_id')
            logger.debug(f"Resolved from delivery_id: form_id={form_id}, webhook_id={webhook_id}")
        
        # Get history
        history = WebhookService.get_webhook_history(
            form_id=form_id,
            webhook_id=webhook_id,
            status=status,
            page=page,
            per_page=per_page
        )
        
        return jsonify(history), 200
        
    except Exception as e:
        current_app.logger.error(f"Get webhook history error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@webhooks_bp.route("/<delivery_id>/retry", methods=["POST"])
@jwt_required()
def retry_webhook(delivery_id: str):
    """
    Retry a failed webhook delivery.
    
    Path Parameters:
    - delivery_id: The ID of the webhook delivery
    
    Request Body:
    {
        "reset_count": false
    }
    
    Response:
    {
        "status": "success" | "failed",
        "delivery_id": "new_delivery_id",
        "attempt_count": int,
        "message": str,
        "error": str (optional),
        "previous_delivery_id": "old_delivery_id"
    }
    """
    try:
        logger.info(f"--- Retry Webhook branch started for id: {delivery_id} ---")
        data = request.get_json() or {}
        reset_count = data.get("reset_count", False)
        
        # Validate reset_count
        if not isinstance(reset_count, bool):
            logger.warning(f"Retry Webhook failed: Invalid reset_count type {type(reset_count)}")
            return jsonify({"error": "reset_count must be a boolean"}), 400
        
        # Retry webhook
        logger.info(f"Retrying webhook delivery for {delivery_id} (reset_count={reset_count})")
        result = WebhookService.retry_webhook(delivery_id, reset_count=reset_count)
        
        if result.get("status") == "error":
            logger.warning(f"Retry Webhook service error: {result.get('message')}")
            return jsonify(result), 400
        
        logger.info(f"Retry Webhook successful for {delivery_id}")
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Retry webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@webhooks_bp.route("/<delivery_id>/cancel", methods=["DELETE"])
@jwt_required()
def cancel_webhook(delivery_id: str):
    """
    Cancel a pending or retrying webhook delivery.
    
    Path Parameters:
    - delivery_id: The ID of the webhook delivery
    
    Response:
    {
        "status": "success",
        "delivery_id": "delivery_id",
        "message": "Webhook delivery cancelled successfully"
    }
    """
    try:
        logger.info(f"--- Cancel Webhook branch started for id: {delivery_id} ---")
        result = WebhookService.cancel_webhook(delivery_id)
        
        if result.get("status") == "error":
            logger.warning(f"Cancel Webhook service error: {result.get('message')}")
            return jsonify(result), 400
        
        logger.info(f"Cancel Webhook successful for {delivery_id}")
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Cancel webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 500


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
            logger.warning("Test Webhook failed: URL missing")
            return jsonify({"error": "url is required"}), 400
        
        if not payload:
            logger.warning("Test Webhook failed: Payload missing")
            return jsonify({"error": "payload is required"}), 400
        
        if not isinstance(payload, dict):
            logger.warning("Test Webhook failed: Payload is not a dictionary")
            return jsonify({"error": "payload must be a dictionary"}), 400
        
        if not isinstance(max_retries, int) or max_retries < 1:
            logger.warning(f"Test Webhook failed: Invalid max_retries {max_retries}")
            return jsonify({"error": "max_retries must be a positive integer"}), 400
        
        # Get current user
        created_by = get_jwt_identity()
        
        # Send webhook using the service with test webhook_id and form_id
        logger.info(f"Testing webhook delivery to {url}")
        result = WebhookService.send_webhook(
            url=url,
            payload=payload,
            webhook_id="test_webhook",
            form_id="test_form",
            created_by=created_by,
            max_retries=max_retries,
            headers=headers
        )
        
        logger.info(f"Test webhook result: {result.get('status')}")
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Webhook test error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@webhooks_bp.route("/logs", methods=["GET"])
@jwt_required()
def get_webhook_logs():
    """
    Retrieve webhook logs with optional filtering (legacy endpoint).
    
    Query Parameters:
    - url: Filter by webhook URL (optional)
    - status: Filter by status (optional): pending, success, failed, retrying
    - limit: Maximum number of logs to return (default: 100)
    
    Response:
    {
        "count": 10,
        "logs": [
            {
                "id": "log_id",
                "url": "https://example.com/webhook",
                "payload": {...},
                "status": "success",
                "attempt_count": 1,
                "last_attempt": "2026-02-04T09:00:00Z",
                "error_message": null,
                "status_code": 200,
                "created_at": "2026-02-04T09:00:00Z",
                "metadata": {...}
            }
        ]
    }
    """
    try:
        logger.info("--- Get Webhook Logs branch started ---")
        url = request.args.get("url")
        status = request.args.get("status")
        limit = request.args.get("limit", 100, type=int)
        
        # Validate status if provided
        if status and status not in ['pending', 'success', 'failed', 'retrying']:
            logger.warning(f"Get Webhook Logs failed: Invalid status '{status}'")
            return jsonify({
                "error": "Invalid status. Must be one of: pending, success, failed, retrying"
            }), 400
        
        # Validate limit
        if limit < 1 or limit > 1000:
            logger.warning(f"Get Webhook Logs failed: Invalid limit {limit}")
            return jsonify({"error": "limit must be between 1 and 1000"}), 400
        
        logger.info(f"Fetching logs (url={url}, status={status}, limit={limit})")
        
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
    Retrieve a specific webhook log by ID (legacy endpoint).
    
    Path Parameters:
    - log_id: The ID of the webhook log
    
    Response:
    {
        "id": "log_id",
        "url": "https://example.com/webhook",
        "payload": {...},
        "status": "success",
        "attempt_count": 1,
        "last_attempt": "2026-02-04T09:00:00Z",
        "error_message": null,
        "status_code": 200,
        "created_at": "2026-02-04T09:00:00Z",
        "metadata": {...}
    }
    """
    try:
        logger.info(f"--- Get Webhook Log branch started for id: {log_id} ---")
        log = WebhookService.get_webhook_log_by_id(log_id)
        
        if not log:
            logger.warning(f"Get Webhook Log failed: ID {log_id} not found")
            return jsonify({"error": "Webhook log not found"}), 404
        
        logger.info(f"Returning log for: {log_id}")
        return jsonify(log), 200
        
    except Exception as e:
        current_app.logger.error(f"Get webhook log error: {str(e)}")
        return jsonify({"error": str(e)}), 500
