import pytest
import uuid
from datetime import datetime, timezone, timedelta
from app.models.Form import FormResponse

def get_admin_token(client):
    email = f"analytics_full_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"77{uuid.uuid4().int % 100000000:08d}"
    res = client.post("/form/api/v1/auth/register", json={
        "username": "analytics_full", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": mobile
    })
    assert res.status_code in [201, 200], f"Registration failed: {res.get_json()}"
    
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    assert resp.status_code == 200, f"Login failed: {resp.get_json()}"
    return resp.get_json()["access_token"]

def test_full_analytics_endpoint(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Setup Form
    q1_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    
    form_payload = {
        "title": "Full Analytics Form", 
        "slug": f"full-ana-{uuid.uuid4().hex[:6]}", 
        "status": "published", 
        "versions": [{
            "version": "1.0", "sections": [{
                "id": s1_id, 
                "title": "S1",
                "questions": [
                    {
                        "id": q1_id, 
                        "label": "Satisfaction", 
                        "field_type": "radio", 
                        "options": [{"option_label": "High", "option_value": "High"}, {"option_label": "Low", "option_value": "Low"}],
                    }
                ]
            }]
        }]
    }
    
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    assert res.status_code == 201
    form_id = res.get_json()["form_id"]
    
    # 2. Seed Data
    # 2 High, 1 Low
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {s1_id: {q1_id: "High"}}}, headers=headers)
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {s1_id: {q1_id: "High"}}}, headers=headers)
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {s1_id: {q1_id: "Low"}}}, headers=headers)
    
    # 3. Call New Endpoint
    res = client.get(f"/form/api/v1/form/{form_id}/analytics", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    
    # 4. Verify Structure
    assert "totalSubmissions" in data
    assert "completionRate" in data
    assert "trends" in data
    assert "fieldDistributions" in data
    
    assert data["totalSubmissions"] == 3
    
    # Verify Trends (should have today's date)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_trend = next((t for t in data["trends"] if t["date"] == today_str), None)
    assert today_trend is not None
    assert today_trend["value"] == 3
    
    # Verify Distribution
    assert "Satisfaction" in data["fieldDistributions"]
    sat_dist = data["fieldDistributions"]["Satisfaction"]
    
    high_entry = next((i for i in sat_dist if i["label"] == "High"), None)
    low_entry = next((i for i in sat_dist if i["label"] == "Low"), None)
    
    assert high_entry["count"] == 2
    assert low_entry["count"] == 1
