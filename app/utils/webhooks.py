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
    All webhook attempts are logged to the webhook_logs collection.
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

    for config in form.webhooks:
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

        # Use WebhookService for reliable delivery with retry logic
        try:
            result = WebhookService.send_webhook(
                url=url,
                payload=payload,
                max_retries=3,
                headers=headers,
                timeout=10
            )
            
            if result["status"] == "success":
                current_app.logger.info(
                    f"Webhook delivered successfully to {url} for event {event}. "
                    f"Attempt: {result['attempt_count']}, Log ID: {result['log_id']}"
                )
            else:
                current_app.logger.error(
                    f"Webhook failed to deliver to {url} for event {event}. "
                    f"Error: {result.get('error', 'Unknown error')}, "
                    f"Log ID: {result['log_id']}"
                )
        except Exception as e:
            current_app.logger.error(f"Failed to send webhook to {url}: {str(e)}")
