
import pytest
import uuid
import time
from datetime import datetime, timedelta, timezone
from app.models.Form import Form, FormResponse

def get_admin_token(client):
    email = f"analytics_admin_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"77{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "analytics_admin", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_analytics_endpoints(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Form with Choice Question
    q1_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    
    form_payload = {
        "title": "Analytics Form", 
        "slug": f"analytics-form-{uuid.uuid4().hex[:6]}", 
        "status": "published", 
        "is_public": True,
        "versions": [{
            "version": "1.0", "sections": [{
                "id": s1_id, 
                "title": "S1",
                "questions": [
                    {
                        "id": q1_id, 
                        "label": "Favorite Color", 
                        "field_type": "radio", 
                        "options": [{"option_label": "Red", "option_value": "Red"}, {"option_label": "Blue", "option_value": "Blue"}],
                        "is_required": True
                    }
                ]
            }]
        }]
    }
    
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    assert res.status_code == 201
    form_id = res.get_json()["form_id"]
    
    # 2. Submit Responses
    # 2x Red, 1x Blue
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {s1_id: {q1_id: "Red"}}}, headers=headers)
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {s1_id: {q1_id: "Red"}}}, headers=headers)
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {s1_id: {q1_id: "Blue"}}}, headers=headers)
    
    # 3. Test Summary
    res_summary = client.get(f"/form/api/v1/form/{form_id}/analytics/summary", headers=headers)
    assert res_summary.status_code == 200
    summary = res_summary.get_json()
    assert summary["total_responses"] == 3
    assert summary["status_breakdown"]["pending"] == 3
    
    # 4. Test Timeline
    res_timeline = client.get(f"/form/api/v1/form/{form_id}/analytics/timeline", headers=headers)
    assert res_timeline.status_code == 200
    timeline = res_timeline.get_json()["timeline"]
    # Should have entry for today
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_entry = next((item for item in timeline if item["date"] == today), None)
    assert today_entry is not None
    assert today_entry["count"] == 3

    # 5. Test Distribution
    res_dist = client.get(f"/form/api/v1/form/{form_id}/analytics/distribution", headers=headers)
    assert res_dist.status_code == 200
    dist = res_dist.get_json()["distribution"]
    
    q_dist = next((item for item in dist if item["question_id"] == q1_id), None)
    assert q_dist is not None
    assert q_dist["label"] == "Favorite Color"
    assert q_dist["counts"]["Red"] == 2
    assert q_dist["counts"]["Blue"] == 1
