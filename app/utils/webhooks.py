import hmac
import hashlib
from typing import Any
from flask import json
from flask import current_app
from app.models.Form import Form
from app.services.webhook_service import WebhookService


def trigger_webhooks(form: Form, event: str, data: dict[str, Any]) -> None:
    """
    Triggers all active webhooks for a given form and event with retry mechanism.
    data should be a JSON-serializable dictionary.
    
    Uses WebhookService for reliable delivery with exponential backoff retry logic.
    All webhook attempts are logged to the webhook_deliveries collection.
    """
    if not form.webhooks:
        return

    payload = {
        "event": event,
        "form_id": str(form.id),
        "form_title": form.title,
        "payload": data
    }
    
    encoded_payload = json.dumps(payload).encode('utf-8')

    for idx, config in enumerate(form.webhooks):
        # Expected config format: {"url": "...", "events": ["submitted", "updated"], "secret": "..."}
        url = config.get("url")
        events = config.get("events", [])
        secret = config.get("secret")

        if not url:
            continue
        
        if event not in events:
            continue

        headers = {
            "Content-Type": "application/json",
            "X-Form-Event": event
        }

        if secret:
            signature = hmac.new(
                secret.encode('utf-8'),
                encoded_payload,
                hashlib.sha256
            ).hexdigest()
            headers["X-Form-Signature"] = f"sha256={signature}"

        # Use WebhookService for reliable delivery with enhanced retry logic
        try:
            # Generate a unique webhook_id for this webhook configuration
            webhook_id = f"{str(form.id)}_{idx}_{url}"
            
            result = WebhookService.send_webhook(
                url=url,
                payload=payload,
                webhook_id=webhook_id,
                form_id=str(form.id),
                created_by="system",  # System-triggered webhook
                max_retries=5,  # Use enhanced retry logic with 5 retries
                headers=headers,
                timeout=10
            )
            
            if result["status"] == "success":
                current_app.logger.info(
                    f"Webhook delivered successfully to {url} for event {event}. "
                    f"Attempt: {result['attempt_count']}, Delivery ID: {result['delivery_id']}"
                )
            elif result["status"] == "scheduled":
                current_app.logger.info(
                    f"Webhook scheduled for {result.get('next_retry_at')} to {url} for event {event}. "
                    f"Delivery ID: {result['delivery_id']}"
                )
            else:
                current_app.logger.error(
                    f"Webhook failed to deliver to {url} for event {event}. "
                    f"Error: {result.get('error', 'Unknown error')}, "
                    f"Delivery ID: {result['delivery_id']}"
                )
        except Exception as e:
            current_app.logger.error(f"Failed to send webhook to {url}: {str(e)}")
