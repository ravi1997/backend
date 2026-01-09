
import pytest
import uuid
import time
from datetime import datetime, timedelta, timezone
from app.models.Form import Form

def get_admin_token(client):
    email = f"sched_admin_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"77{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "sched_admin", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def get_user_token(client):
    email = f"sched_user_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"66{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "sched_user", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["user"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_scheduled_publishing_future(client):
    admin_token = get_admin_token(client)
    user_token = get_user_token(client)
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # 1. Create Future Scheduled Form (Status=published but publish_at=Future)
    # Using replace(microsecond=0, tzinfo=None) to see if naive ISO works
    future_date = (datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0, tzinfo=None).isoformat()
    form_payload = {
        "title": "Future Form", 
        "slug": f"future-form-{uuid.uuid4().hex[:6]}", 
        "status": "published",
        "publish_at": future_date,
        "is_public": True,
        "versions": [{"version": "1.0", "sections": [{"id": str(uuid.uuid4()), "title": "S1", "questions": []}]}]
    }
    form_res = client.post("/form/api/v1/form/", json=form_payload, headers=admin_headers)
    assert form_res.status_code == 201
    form_id = form_res.get_json()["form_id"]
    
    # 2. Admin should see it
    res_admin = client.get(f"/form/api/v1/form/{form_id}", headers=admin_headers)
    assert res_admin.status_code == 200
    
    # 3. User should NOT see it
    res_user = client.get(f"/form/api/v1/form/{form_id}", headers=user_headers)
    assert res_user.status_code == 403
    assert "not yet available" in res_user.get_json()["error"]
    
    # 4. User should NOT be able to submit
    sub_res = client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {}}, headers=user_headers)
    assert sub_res.status_code == 403
    assert "not yet available" in sub_res.get_json()["error"]

def test_scheduled_publishing_past(client):
    admin_token = get_admin_token(client)
    user_token = get_user_token(client)
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # 1. Create Past Scheduled Form
    past_date = (datetime.now(timezone.utc) - timedelta(days=1)).replace(microsecond=0, tzinfo=None).isoformat()
    form_payload = {
        "title": "Past Form", 
        "slug": f"past-form-{uuid.uuid4().hex[:6]}", 
        "status": "published",
        "publish_at": past_date,
        "is_public": False,
        "submitters": [],
        "versions": [{"version": "1.0", "sections": [{"id": str(uuid.uuid4()), "title": "S1", "questions": []}]}]
    }
    # To properly test Date logic vs Permission logic:
    # Let's make it public=True for simplicity of permission, but check Date.
    form_payload["is_public"] = True
    
    form_res = client.post("/form/api/v1/form/", json=form_payload, headers=admin_headers)
    assert form_res.status_code == 201
    form_id = form_res.get_json()["form_id"]
    
    # 2. User should see it
    res_user = client.get(f"/form/api/v1/form/{form_id}", headers=user_headers)
    assert res_user.status_code == 200
    
    # 3. User should submit
    sub_res = client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {}}, headers=user_headers)
    assert sub_res.status_code == 201
