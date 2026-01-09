
import pytest
import uuid
import time
from datetime import datetime
from app.models.Form import Form, FormResponse

def get_admin_token(client):
    email = f"status_admin_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"99{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "status_admin", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def get_user_token(client):
    email = f"status_user_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"88{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "status_user", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["user"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_response_status_workflow(client):
    admin_token = get_admin_token(client)
    user_token = get_user_token(client)
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # 1. Admin creates form and allows user to submit
    form_payload = {
        "title": "Status Workflow Form", 
        "slug": f"status-form-{uuid.uuid4().hex[:6]}", 
        "status": "published",
        "is_public": True,
        "versions": [{"version": "1.0", "sections": [{"id": str(uuid.uuid4()), "title": "S1", "questions": []}]}]
    }
    form_res = client.post("/form/api/v1/form/", json=form_payload, headers=admin_headers)
    assert form_res.status_code == 201
    form_id = form_res.get_json()["form_id"]
    
    # 2. User submits response (defaults to 'pending')
    sub_res = client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {"foo": "bar"}}, headers=user_headers)
    assert sub_res.status_code == 201
    resp_id = sub_res.get_json()["response_id"]
    
    # Verify initial status
    get_res = client.get(f"/form/api/v1/form/{form_id}/responses/{resp_id}", headers=admin_headers)
    assert get_res.get_json()["status"] == "pending"
    
    # 3. User tries to approve (Should Fail - 403)
    status_payload = {"status": "approved", "comment": "Hacking it"}
    fail_res = client.patch(f"/form/api/v1/form/{form_id}/responses/{resp_id}/status", json=status_payload, headers=user_headers)
    assert fail_res.status_code == 403
    
    # 4. Admin Approves (Should Succeed)
    approve_payload = {"status": "approved", "comment": "Looks good"}
    ok_res = client.patch(f"/form/api/v1/form/{form_id}/responses/{resp_id}/status", json=approve_payload, headers=admin_headers)
    assert ok_res.status_code == 200
    
    # 5. Verify Status and Log
    final_res = client.get(f"/form/api/v1/form/{form_id}/responses/{resp_id}", headers=admin_headers)
    data = final_res.get_json()
    assert data["status"] == "approved"
    assert len(data["status_log"]) == 1
    assert data["status_log"][0]["status"] == "approved"
    assert data["status_log"][0]["comment"] == "Looks good"
    
    # 6. Admin Rejects (Should Succeed)
    reject_payload = {"status": "rejected", "comment": "Changed mind"}
    client.patch(f"/form/api/v1/form/{form_id}/responses/{resp_id}/status", json=reject_payload, headers=admin_headers)
    
    final_res_2 = client.get(f"/form/api/v1/form/{form_id}/responses/{resp_id}", headers=admin_headers)
    data_2 = final_res_2.get_json()
    assert data_2["status"] == "rejected"
    assert len(data_2["status_log"]) == 2
