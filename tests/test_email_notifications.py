
import pytest
from unittest.mock import patch
import uuid
from app.models.Form import Form

def get_admin_token(client):
    email = f"admin_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/form/api/v1/auth/register", json={
        "username": "admin_user", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": "9988776655"
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_email_notification_on_submit(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Form with notification_emails
    form_payload = {
        "title": "Email Form", 
        "slug": f"email-form-{uuid.uuid4().hex[:6]}", 
        "status": "published",
        "notification_emails": ["admin@example.com", "manager@example.com"],
        "versions": [{"version": "1.0", "sections": [{"id": str(uuid.uuid4()), "title": "S1", "questions": []}]}]
    }
    form_res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    assert form_res.status_code == 201
    form_id = form_res.get_json()["form_id"]
    
    # Mock the email helper's internal smtplib usage, OR mock the helper itself.
    # Since we want to test that the route calls the helper, checking the helper is called is sufficient.
    
    with patch("app.routes.v1.form.responses.send_email_notification") as mock_send_email:
        mock_send_email.return_value = True
        
        # 2. Submit Response
        client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {}}, headers=headers)
        
        # 3. Verify Email Sent
        assert mock_send_email.called
        args, _ = mock_send_email.call_args
        assert args[0] == ["admin@example.com", "manager@example.com"]
        assert "New Submission" in args[1]

def test_public_email_notification_on_submit(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Public Form
    form_payload = {
        "title": "Public Email Form", 
        "slug": f"pub-email-{uuid.uuid4().hex[:6]}", 
        "status": "published",
        "is_public": True,
        "notification_emails": ["public@example.com"],
        "versions": [{"version": "1.0", "sections": [{"id": str(uuid.uuid4()), "title": "S1", "questions": []}]}]
    }
    form_res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    form_id = form_res.get_json()["form_id"]
    
    with patch("app.routes.v1.form.misc.send_email_notification") as mock_send_email:
        mock_send_email.return_value = True
        
        # 2. Public Submit
        client.post(f"/form/api/v1/form/{form_id}/public-submit", json={"data": {}})
        
        # 3. Verify Email
        assert mock_send_email.called
        args, _ = mock_send_email.call_args
        assert args[0] == ["public@example.com"]
        assert "New Public Submission" in args[1]
