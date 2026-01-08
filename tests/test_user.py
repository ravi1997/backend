import pytest

def get_admin_token(client):
    # Helper to get admin token
    payload = {
        "username": "admin_user",
        "email": "admin_test@example.com",
        "password": "AdminPassword123",
        "employee_id": "ADM001",
        "user_type": "employee",
        "mobile": "9988776655",
        "roles": ["admin"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "admin_test@example.com", "password": "AdminPassword123"})
    return login_resp.get_json()["access_token"]

def test_list_users_admin(client):
    token = get_admin_token(client)
    response = client.get("/form/api/v1/user/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_list_users_unauthorized(client):
    # Register regular user
    payload = {
        "username": "reg_user",
        "email": "reg@example.com",
        "password": "UserPassword123",
        "employee_id": "UR001",
        "user_type": "employee",
        "mobile": "8877665544",
        "roles": ["user"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "reg@example.com", "password": "UserPassword123"})
    token = login_resp.get_json()["access_token"]
    
    response = client.get("/form/api/v1/user/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403 # Unauthorized for non-admin

def test_create_user_admin(client):
    token = get_admin_token(client)
    payload = {
        "username": "new_user",
        "email": "new@example.com",
        "mobile": "0987654321",
        "user_type": "employee",
        "roles": ["user"],
        "password": "Password123!"
    }
    response = client.post("/form/api/v1/user/users", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201, response.get_json()
    assert response.get_json()["username"] == "new_user"

def test_lock_unlock_user(client):
    token = get_admin_token(client)
    # Create a user to lock
    create_resp = client.post("/form/api/v1/user/users", json={
        "username": "lockme", 
        "email": "lock@ex.com", 
        "user_type":"employee",
        "mobile": "7766554433",
        "roles": ["user"],
        "password": "Password123!"
    }, headers={"Authorization": f"Bearer {token}"})
    assert create_resp.status_code == 201, create_resp.get_json()
    
    user_list_resp = client.get("/form/api/v1/user/users", headers={"Authorization": f"Bearer {token}"})
    assert user_list_resp.status_code == 200
    user_list = user_list_resp.get_json()
    user_id = next(u["id"] for u in user_list if u["username"] == "lockme")
    
    # Lock
    response = client.post(f"/form/api/v1/user/users/{user_id}/lock", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    # Check status
    status_resp = client.get(f"/form/api/v1/user/security/lock-status/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert status_resp.get_json()["locked"] == True
    
    # Unlock
    response = client.post(f"/form/api/v1/user/users/{user_id}/unlock", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    status_resp = client.get(f"/form/api/v1/user/security/lock-status/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert status_resp.get_json()["locked"] == False

def test_change_password(client):
    # Register and login
    payload = {
        "username": "pwuser",
        "email": "pw@example.com",
        "password": "OldPassword123",
        "employee_id": "PW001",
        "user_type": "employee",
        "mobile": "6655443322",
        "roles": ["user"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "pw@example.com", "password": "OldPassword123"})
    token = login_resp.get_json()["access_token"]
    
    # Change password
    cp_payload = {
        "current_password": "OldPassword123",
        "new_password": "NewPassword123!"
    }
    response = client.post("/form/api/v1/user/change-password", json=cp_payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    # Verify login with new password
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "pw@example.com", "password": "NewPassword123!"})
    assert login_resp.status_code == 200
