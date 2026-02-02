import pytest
import uuid
from unittest.mock import patch, MagicMock

def get_tokens(client):
    # Register admin and submitter
    email_adm = f"wf_admin_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/form/api/v1/auth/register", json={
        "username": "wf_admin", "email": email_adm, "password": "Pass", 
        "employee_id": f"WA_{uuid.uuid4().hex[:4]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": f"55{uuid.uuid4().int % 100000000:08d}"
    })
    admin_token = client.post("/form/api/v1/auth/login", json={"email": email_adm, "password": "Pass"}).get_json()["access_token"]
    
    email_sub = f"wf_sub_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/form/api/v1/auth/register", json={
        "username": "wf_sub", "email": email_sub, "password": "Pass", 
        "employee_id": f"WS_{uuid.uuid4().hex[:4]}", "user_type": "employee", 
        "roles": ["user"], "mobile": f"44{uuid.uuid4().int % 100000000:08d}"
    })
    user_token = client.post("/form/api/v1/auth/login", json={"email": email_sub, "password": "Pass"}).get_json()["access_token"]
    
    return admin_token, user_token, email_sub

# Mock the send_email_notification function effectively
@patch('app.routes.v1.form.responses.send_email_notification')
def test_embedded_workflow_execution(mock_send_email, client):
    admin_token, user_token, user_email = get_tokens(client)
    headers_adm = {"Authorization": f"Bearer {admin_token}"}
    headers_user = {"Authorization": f"Bearer {user_token}"}
    
    # 1. Create Form with embedded workflow
    s1_id = str(uuid.uuid4())
    form_payload = {
        "title": "Workflow Form", 
        "slug": f"wf-form-{uuid.uuid4().hex[:6]}", 
        "status": "published",
        "is_public": True,
        "versions": [{"version": "1.0", "sections": [{"id": s1_id, "title": "S1", "questions": []}]}],
        # M-17 Embedded Workflow Config
        "workflows": {
            "on_submit": [
                {
                    "action": "email_notification",
                    "target": "manager@example.com"
                }
            ]
        }
    }
    
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers_adm)
    assert res.status_code == 201
    form_id = res.get_json()["form_id"]
    
    # 2. Submit Response
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {}}, headers=headers_user)
    
    # 3. Verify Email Mock Called
    assert mock_send_email.called
    args, _ = mock_send_email.call_args
    assert "manager@example.com" in args[0] # Target list
    assert "Workflow Notification" in args[1] # Subject
