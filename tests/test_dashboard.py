
import pytest
import json

def get_admin_token(client):
    payload = {
        "username": "admin_dash",
        "email": "admin_dash@example.com",
        "password": "Password123",
        "employee_id": "ADM_DASH",
        "user_type": "employee",
        "mobile": "1234567890",
        "roles": ["admin"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "admin_dash@example.com", "password": "Password123"})
    if login_resp.status_code != 200:
        print(f"Admin login failed: {login_resp.get_json()}")
        raise Exception("Admin login failed")
    return login_resp.get_json()["access_token"]

def get_deo_token(client):
    payload = {
        "username": "deo_user",
        "email": "deo@example.com",
        "password": "Password123",
        "employee_id": "DEO001",
        "user_type": "employee",
        "mobile": "0987654321",
        "roles": ["deo"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "deo@example.com", "password": "Password123"})
    if login_resp.status_code != 200:
        print(f"DEO login failed: {login_resp.get_json()}")
        raise Exception("DEO login failed")
    return login_resp.get_json()["access_token"]

def get_other_token(client):
    payload = {
        "username": "other_user",
        "email": "other@example.com",
        "password": "Password123",
        "employee_id": "OTH001",
        "user_type": "employee",
        "mobile": "1122334455",
        "roles": ["user"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "other@example.com", "password": "Password123"})
    if login_resp.status_code != 200:
        print(f"Other login failed: {login_resp.get_json()}")
        raise Exception("Other login failed")
    return login_resp.get_json()["access_token"]

def test_dashboard_lifecycle(client):
    admin_token = get_admin_token(client)
    deo_token = get_deo_token(client)
    other_token = get_other_token(client)
    
    # 1. Create Dashboard
    payload = {
        "title": "DEO Dashboard",
        "slug": "deo-home",
        "roles": ["deo"],
        "widgets": [
           {
               "title": "My Tasks",
               "type": "shortcut",
               "target_link": "/tasks"
           } 
        ]
    }
    resp = client.post("/form/api/v1/dashboards/", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    
    # 2. List Dashboards - Admin sees all
    resp = client.get("/form/api/v1/dashboards/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1
    
    # 3. List Dashboards - DEO sees it
    resp = client.get("/form/api/v1/dashboards/", headers={"Authorization": f"Bearer {deo_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(d['slug'] == 'deo-home' for d in data)
    
    # 4. List Dashboards - Other should NOT see it
    resp = client.get("/form/api/v1/dashboards/", headers={"Authorization": f"Bearer {other_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert not any(d['slug'] == 'deo-home' for d in data)
    
    # 5. Get Dashboard - DEO
    resp = client.get("/form/api/v1/dashboards/deo-home", headers={"Authorization": f"Bearer {deo_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['title'] == "DEO Dashboard"
    assert len(data['widgets']) == 1
    
    # 6. Get Dashboard - Other (Forbidden)
    resp = client.get("/form/api/v1/dashboards/deo-home", headers={"Authorization": f"Bearer {other_token}"})
    assert resp.status_code == 403
    
    # 7. Update Dashboard
    update_payload = {"title": "Updated Dashboard"}
    dashboard_id = Dashboard.objects(slug='deo-home').first().id
    resp = client.put(f"/form/api/v1/dashboards/{dashboard_id}", json=update_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    
    # Verify update
    resp = client.get("/form/api/v1/dashboards/deo-home", headers={"Authorization": f"Bearer {deo_token}"})
    assert resp.get_json()['title'] == "Updated Dashboard"

from app.models.Dashboard import Dashboard
