import pytest
import uuid
import time
from datetime import datetime, timezone, timedelta

def get_admin_token(client):
    email = f"admin_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/form/api/v1/auth/register", json={
        "username": "admin_user", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": str(int(time.time()))[-10:]
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_full_response_lifecycle_flow(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Form with specific version
    form_payload = {
        "title": "Lifecycle Form", "slug": f"slug-{uuid.uuid4().hex[:6]}", "status": "published",
        "versions": [{"version": "2.1.0", "sections": [{"id": str(uuid.uuid4()), "title": "S1", "questions": []}]}]
    }
    form_res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    form_id = form_res.get_json()["form_id"]
    
    # 2. Submit Response and verify version
    sub_res = client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {}}, headers=headers)
    resp_id = sub_res.get_json()["response_id"]
    
    get_res = client.get(f"/form/api/v1/form/{form_id}/responses/{resp_id}", headers=headers)
    response_data = get_res.get_json()
    assert response_data["version"] == "2.1.0"
    assert response_data["deleted"] is False
    
    # 3. List responses (should show 1)
    list_res = client.get(f"/form/api/v1/form/{form_id}/responses", headers=headers)
    assert len(list_res.get_json()) == 1
    
    # 4. Soft Delete (Archive)
    client.patch(f"/form/api/v1/form/{form_id}/responses/{resp_id}/archive", headers=headers)
    
    # 5. List responses (should be empty now due to filtering)
    list_res_after = client.get(f"/form/api/v1/form/{form_id}/responses", headers=headers)
    assert len(list_res_after.get_json()) == 0
    
    # 6. Restore Response
    client.patch(f"/form/api/v1/form/{form_id}/responses/{resp_id}/restore", headers=headers)
    
    # 7. List responses (should show 1 again)
    list_res_final = client.get(f"/form/api/v1/form/{form_id}/responses", headers=headers)
    assert len(list_res_final.get_json()) == 1
    
    # 8. Delete response (also soft delete now)
    client.delete(f"/form/api/v1/form/{form_id}/responses/{resp_id}", headers=headers)
    list_res_deleted = client.get(f"/form/api/v1/form/{form_id}/responses", headers=headers)
    assert len(list_res_deleted.get_json()) == 0

def test_account_lockout_integration(client):
    # Register a user
    email = f"lockout_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/form/api/v1/auth/register", json={
        "username": "lockout_user", "email": email, "password": "CorrectPassword",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["user"], "mobile": str(int(time.time()))[-10:]
    })
    
    # Fail login 5 times
    for _ in range(5):
        resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "WrongPassword"})
        assert resp.status_code == 401
    
    # 6th attempt should return 403 Forbidden (Locked)
    locked_resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "CorrectPassword"})
    assert locked_resp.status_code == 403
    assert "Account is locked" in locked_resp.get_json()["msg"]

def test_password_expiration_integration(client):
    from app.models.User import User
    
    email = f"expire_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/form/api/v1/auth/register", json={
        "username": "expire_user", "email": email, "password": "SecurePassword",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["user"], "mobile": str(int(time.time()))[-10:]
    })
    
    # Manually backdate password expiration in DB
    user = User.objects.get(email=email)
    user.password_expiration = datetime.now(timezone.utc) - timedelta(days=1)
    user.save()
    
    # Login should fail with 403 Expired
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword"})
    assert resp.status_code == 403
    assert "Password expired" in resp.get_json()["msg"]
