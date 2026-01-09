import pytest
import uuid

def test_ai_anomaly_detection(client):
    # Setup: Login
    user_data = {
        "username": "anomaly_tester",
        "email": "anomaly@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "9993334445"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "anomaly@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a form
    form_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    q1_id = str(uuid.uuid4()) # Score (numerical)
    q2_id = str(uuid.uuid4()) # Comment (text)
    
    client.post("/form/api/v1/form/", json={
        "id": form_id,
        "title": "Anomaly Test Form",
        "slug": f"anomaly-test-{uuid.uuid4().hex[:6]}",
        "status": "published",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [
                    {"id": q1_id, "label": "Score", "field_type": "input"},
                    {"id": q2_id, "label": "Comment", "field_type": "textarea"}
                ]
            }]
        }]
    }, headers=headers)

    # 2. Submit Normal Responses
    for i in range(5):
        client.post(f"/form/api/v1/form/{form_id}/responses", 
                    json={"data": {s1_id: {q1_id: 10, q2_id: "Everything is working fine."}}}, 
                    headers=headers)

    # 3. Submit Anomalous Responses
    # R6: Outlier (Score 500 when others are 10)
    client.post(f"/form/api/v1/form/{form_id}/responses", 
                json={"data": {s1_id: {q1_id: 500, q2_id: "Outlier data"}}}, 
                headers=headers)
    
    # R7: Duplicate (Matches normal response)
    client.post(f"/form/api/v1/form/{form_id}/responses", 
                json={"data": {s1_id: {q1_id: 10, q2_id: "Everything is working fine."}}}, 
                headers=headers)

    # R8: Gibberish (Low vowels)
    client.post(f"/form/api/v1/form/{form_id}/responses", 
                json={"data": {s1_id: {q1_id: 10, q2_id: "qwrtpsdfghjklzxcvbnm"}}}, 
                headers=headers)

    # 4. Run Anomaly Detection
    res = client.post(f"/form/api/v1/ai/{form_id}/anomalies", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    
    types = [a["type"] for a in data["anomalies"]]
    assert "outlier" in types
    assert "duplicate" in types
    assert "low_quality" in types
    assert data["anomaly_count"] >= 3
