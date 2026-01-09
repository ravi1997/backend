import pytest
import uuid

def test_ai_security_scan(client):
    # Setup: Login
    user_data = {
        "username": "sec_tester",
        "email": "sec@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "9998881112"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "sec@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create an insecure form (Public + asking for SSN + many text fields)
    form_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    
    client.post("/form/api/v1/form/", json={
        "id": form_id,
        "title": "Insecure Form",
        "slug": f"sec-test-{uuid.uuid4().hex[:6]}",
        "status": "published",
        "is_public": True,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [
                    {"id": str(uuid.uuid4()), "label": "Full Name", "field_type": "input"},
                    {"id": str(uuid.uuid4()), "label": "Address", "field_type": "textarea"},
                    {"id": str(uuid.uuid4()), "label": "SSN", "field_type": "input"},
                    {"id": str(uuid.uuid4()), "label": "Comments", "field_type": "textarea"},
                    {"id": str(uuid.uuid4()), "label": "Notes", "field_type": "textarea"},
                    {"id": str(uuid.uuid4()), "label": "Feedback", "field_type": "textarea"}
                ]
            }]
        }]
    }, headers=headers)

    # 2. Run Security Scan
    scan_res = client.post(f"/form/api/v1/ai/{form_id}/security-scan", headers=headers)
    assert scan_res.status_code == 200
    data = scan_res.get_json()
    
    assert data["security_score"] < 100
    assert data["status"] in ["WARNING", "FAILED"]
    
    issues = [f["issue"] for f in data["findings"]]
    assert any("Sensitive field" in i and "SSN" in i for i in issues)
    assert "High Spam Risk" in issues
    assert len(data["recommendations"]) > 0

    # 3. Secure the form (Not public, sensitive info removed, validation added) - For testing logic
    secure_form_id = str(uuid.uuid4())
    client.post("/form/api/v1/form/", json={
        "id": secure_form_id,
        "title": "Secure Form",
        "slug": f"secure-test-{uuid.uuid4().hex[:6]}",
        "status": "published",
        "is_public": False,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [
                    {
                        "id": str(uuid.uuid4()), 
                        "label": "Name", 
                        "field_type": "input",
                        "is_required": True
                    }
                ]
            }]
        }]
    }, headers=headers)

    scan_res_2 = client.post(f"/form/api/v1/ai/{secure_form_id}/security-scan", headers=headers)
    assert scan_res_2.status_code == 200
    data_2 = scan_res_2.get_json()
    assert data_2["security_score"] == 100
    assert data_2["status"] == "PASSED"
    assert len(data_2["findings"]) == 0
