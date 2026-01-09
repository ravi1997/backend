import pytest
import uuid

def test_ai_moderation(client):
    # Setup: Login
    user_data = {
        "username": "mod_tester",
        "email": "mod@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "9990001112"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "mod@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a form
    form_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    q1_id = str(uuid.uuid4())
    
    client.post("/form/api/v1/form/", json={
        "id": form_id,
        "title": "Moderation Test Form",
        "slug": f"mod-test-{uuid.uuid4().hex[:6]}",
        "status": "published",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [{"id": q1_id, "label": "Text", "field_type": "textarea"}]
            }]
        }]
    }, headers=headers)

    # 2. Submit Response with multiple flags
    # PII: SSN (000-00-0000)
    # PHI: Medical (diabetes)
    # Profanity: offensive
    # Injection: <script
    text_data = "Patient has diabetes. SSN is 111-22-3333. This comment is offensive. <script>alert(1)</script>"
    res = client.post(f"/form/api/v1/form/{form_id}/responses", 
                      json={"data": {s1_id: {q1_id: text_data}}}, 
                      headers=headers)
    rid = res.get_json()["response_id"]

    # 3. Trigger Moderation
    mod_res = client.post(f"/form/api/v1/ai/{form_id}/responses/{rid}/moderate", headers=headers)
    assert mod_res.status_code == 200
    data = mod_res.get_json()["moderation"]
    
    assert data["is_safe"] is False
    assert "PII Detected: SSN" in data["flags"]
    assert "PHI Potential: diabetes" in data["flags"]
    assert "Warning: Profane" in str(data["flags"])
    assert "CRITICAL: Potential Code/SQL Injection" in str(data["flags"])
    assert data["pii_summary"]["ssn"] == 1
    assert "diabetes" in data["phi_detected"]

    # 4. Verify data stored in response
    get_res = client.get(f"/form/api/v1/form/{form_id}/responses/{rid}", headers=headers)
    resp_data = get_res.get_json()
    assert "moderation" in resp_data["ai_results"]
    assert resp_data["ai_results"]["moderation"]["is_safe"] is False
