import pytest
import uuid
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

def get_tokens(client):
    # Register admin and creator
    uid = uuid.uuid4().hex[:6]
    email = f"admin_{uid}@ex.com"
    # Ensure unique mobile by using random digits
    unique_mobile = "".join(filter(str.isdigit, str(uuid.uuid4().int)))[:10]
    
    reg_resp = client.post("/form/api/v1/auth/register", json={
        "username": f"admin_{uid}", "email": email, "password": "Pass", 
        "employee_id": f"A_{uid}", "user_type": "employee", "roles": ["admin"], "mobile": unique_mobile
    })
    assert reg_resp.status_code == 201, f"Admin Reg Failed: {reg_resp.get_json()}"
    
    login_resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "Pass"})
    assert login_resp.status_code == 200, f"Admin Login Failed: {login_resp.get_json()}"
    admin_token = login_resp.get_json()["access_token"]
    
    uid_sub = uuid.uuid4().hex[:6]
    email_sub = f"sub_{uid_sub}@ex.com"
    unique_mobile_sub = "".join(filter(str.isdigit, str(uuid.uuid4().int)))[:10]
    
    reg_resp_sub = client.post("/form/api/v1/auth/register", json={
        "username": f"sub_{uid_sub}", "email": email_sub, "password": "Pass", 
        "employee_id": f"S_{uid_sub}", "user_type": "employee", "roles": ["user"], "mobile": unique_mobile_sub
    })
    assert reg_resp_sub.status_code == 201, f"User Reg Failed: {reg_resp_sub.get_json()}"
    
    login_resp_sub = client.post("/form/api/v1/auth/login", json={"email": email_sub, "password": "Pass"})
    assert login_resp_sub.status_code == 200, f"User Login Failed: {login_resp_sub.get_json()}"
    user_token = login_resp_sub.get_json()["access_token"]
    
    return admin_token, user_token

def test_conditional_required(client):
    admin_token, user_token = get_tokens(client)
    
    q1_id = str(uuid.uuid4())
    q2_id = str(uuid.uuid4())
    s_id = str(uuid.uuid4())
    
    # Q2 is required if Q1 == 'yes'
    form_payload = {
        "title": "Cond Form", "slug": f"cond-{uuid.uuid4().hex[:6]}", "status": "published", "is_public": True,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s_id, "title": "S1",
                "questions": [
                    {"id": q1_id, "label": "Q1", "field_type": "input"},
                    {"id": q2_id, "label": "Q2", "field_type": "input", 
                     "required_condition": f"{q1_id} == 'yes'"}
                ]
            }]
        }]
    }
    
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_resp.status_code == 201
    form_id = create_resp.get_json()["form_id"]
    
    # Case 1: Q1='no', Q2 missing -> OK
    resp = client.post(f'/form/api/v1/form/{form_id}/responses', 
                       json={"data": {s_id: {q1_id: "no"}}},
                       headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 201, f"Case 1 Q1=no Failed: {resp.get_json()}"
    
    # Case 2: Q1='yes', Q2 missing -> FAIL
    resp = client.post(f'/form/api/v1/form/{form_id}/responses', 
                       json={"data": {s_id: {q1_id: "yes"}}},
                       headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 422
    assert "Required field missing" in str(resp.get_json())
    
    # Case 3: Q1='yes', Q2 present -> OK
    resp = client.post(f'/form/api/v1/form/{form_id}/responses', 
                       json={"data": {s_id: {q1_id: "yes", q2_id: "val"}}},
                       headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 201

def test_history_tracking(client):
    admin_token, user_token = get_tokens(client)
    
    form_payload = {
        "title": "Hist Form", "slug": f"hist-{uuid.uuid4().hex[:6]}", "status": "published", "is_public": True,
        "versions": [{"version": "1.0", "sections": [{"id": str(uuid.uuid4()), "title": "S1", "questions": []}]}]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    form_id = create_resp.get_json()["form_id"]
    
    # Submit
    sub_resp = client.post(f'/form/api/v1/form/{form_id}/responses', json={"data": {"foo": "bar"}}, headers={"Authorization": f"Bearer {user_token}"})
    resp_id = sub_resp.get_json()["response_id"]
    
    # Update
    upd_resp = client.put(f'/form/api/v1/form/{form_id}/responses/{resp_id}', json={"data": {"foo": "baz"}}, headers={"Authorization": f"Bearer {user_token}"})
    assert upd_resp.status_code == 200, f"Update Failed (form={form_id}, resp={resp_id}): {upd_resp.get_json()}"
    
    # Get History
    hist_resp = client.get(f'/form/api/v1/form/{form_id}/responses/{resp_id}/history', headers={"Authorization": f"Bearer {admin_token}"})
    assert hist_resp.status_code == 200
    history = hist_resp.get_json()
    assert len(history) >= 1
    assert history[0]["change_type"] == "update"
    # Although data structure in history depends on how it was saved (nested or flat data block), we checked existence.

@patch('app.utils.webhooks.requests.post')
def test_webhooks(mock_post, client):
    # Use patch context is tricky with pytest fixtures, so using argument patch
    admin_token, user_token = get_tokens(client)
    
    webhook_url = "http://mock-hook.com"
    form_payload = {
        "title": "Hook Form", "slug": f"hook-{uuid.uuid4().hex[:6]}", "status": "published", "is_public": True,
        "webhooks": [{"url": webhook_url, "events": ["submitted"], "secret": "xyz"}],
        "versions": [{"version": "1.0", "sections": [{"id": str(uuid.uuid4()), "title": "S1", "questions": []}]}]
    }
    
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    form_id = create_resp.get_json()["form_id"]
    
    # Submit -> Should trigger webhook
    client.post(f'/form/api/v1/form/{form_id}/responses', json={"data": {}}, headers={"Authorization": f"Bearer {user_token}"})
    
    mock_post.assert_called()
    args, kwargs = mock_post.call_args
    assert args[0] == webhook_url
    assert kwargs['headers']['X-Form-Event'] == 'submitted'
