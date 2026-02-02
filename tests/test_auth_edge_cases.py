import pytest
import json

def test_unauthorized_access_to_admin_route(client):
    # Register as a normal user
    payload = {
        "username": "normaluser",
        "email": "user@example.com",
        "password": "Password123!",
        "employee_id": "EMP_NORM_01",
        "user_type": "employee",
        "mobile": "1112223334",
        "roles": ["user"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    
    # Login to get token
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "user@example.com", "password": "Password123!"})
    token = login_resp.get_json()["access_token"]
    
    # Try to access an admin-only route (e.g., list all users)
    # The route is /form/api/v1/user/users based on route_documentation.md
    response = client.get("/form/api/v1/user/users", headers={"Authorization": f"Bearer {token}"})
    
    # Assert Forbidden
    assert response.status_code == 403
    assert "insufficient permissions" in response.get_json()["error"].lower()

def test_expired_or_invalid_token(client):
    # Invalid token string
    response = client.get("/form/api/v1/user/status", headers={"Authorization": "Bearer invalid_token_string"})
    assert response.status_code in [401, 422] # Flask-JWT-Extended might return 422 for malformed tokens

def test_token_reuse_after_logout(client):
    # Register and Login
    payload = {
        "username": "reuseuser",
        "email": "reuse@example.com",
        "password": "Password123!",
        "employee_id": "EMP_REUSE_01",
        "user_type": "employee",
        "mobile": "9998887776",
        "roles": ["user"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "reuse@example.com", "password": "Password123!"})
    token = login_resp.get_json()["access_token"]
    
    # Logout
    logout_resp = client.post("/form/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_resp.status_code == 200
    
    # Try to reuse the token
    response = client.get("/form/api/v1/user/status", headers={"Authorization": f"Bearer {token}"})
    
    # Assert Unauthorized (Token should be in blocklist)
    assert response.status_code == 401
    # Depending on implementation, message might vary
    # assert response.get_json()["msg"] == "Token has been revoked" 
