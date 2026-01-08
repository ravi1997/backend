import pytest
import json

def test_register_success(client):
    payload = {
        "username": "testadmin",
        "email": "admin@example.com",
        "password": "Password123!",
        "employee_id": "EMP001",
        "user_type": "employee",
        "mobile": "1234567890",
        "roles": ["admin"]
    }
    response = client.post("/form/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered"

def test_register_duplicate_email(client):
    payload = {
        "username": "user1",
        "email": "user@example.com",
        "password": "Password123!",
        "employee_id": "EMP002",
        "user_type": "employee",
        "mobile": "1122334455",
        "roles": ["user"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    
    # Repeat registration with same email
    response = client.post("/form/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.get_json()["message"] == "Email already exists"

def test_login_success(client):
    # Register first
    payload = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "SecretPassword123",
        "employee_id": "EMP003",
        "user_type": "employee",
        "mobile": "2233445566",
        "roles": ["user"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    
    # Login
    login_payload = {
        "email": "login@example.com",
        "password": "SecretPassword123"
    }
    response = client.post("/form/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_login_invalid_credentials(client):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/form/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.get_json()["msg"] == "Invalid credentials"

def test_generate_otp_success(client):
    # Register with mobile
    payload = {
        "username": "otp_user",
        "email": "otp@example.com",
        "password": "Password123!",
        "mobile": "1234567890",
        "user_type": "employee",
        "roles": ["user"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    
    response = client.post("/form/api/v1/auth/generate-otp", json={"mobile": "1234567890"})
    assert response.status_code == 200
    assert response.get_json()["msg"] == "OTP sent successfully"

def test_logout(client):
    # Login to get token
    payload = {
        "username": "logoutuser",
        "email": "logout@example.com",
        "password": "Password123!",
        "employee_id": "EMP004",
        "user_type": "employee",
        "mobile": "4455667788",
        "roles": ["user"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "logout@example.com", "password": "Password123!"})
    token = login_resp.get_json()["access_token"]
    
    response = client.post("/form/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["msg"] == "Successfully logged out"
