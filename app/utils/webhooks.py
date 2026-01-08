import hmac
import hashlib
from flask import json
import requests
from flask import current_app

def trigger_webhooks(form, event, data):
    """
    Triggers all active webhooks for a given form and event.
    data should be a JSON-serializable dictionary.
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

        try:
            # We use a timeout to prevent blocking the main request for too long
            # In a production app, this should be offloaded to a task queue (Celery/RQ)
            response = requests.post(url, data=encoded_payload, headers=headers, timeout=5)
            current_app.logger.info(f"Webhook sent to {url} for event {event}. Status: {response.status_code}")
        except Exception as e:
            current_app.logger.error(f"Failed to send webhook to {url}: {str(e)}")
