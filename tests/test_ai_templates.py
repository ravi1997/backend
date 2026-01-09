import pytest

def test_ai_template_generation(client):
    # Setup: Login
    user_data = {
        "username": "tpl_tester",
        "email": "tpl@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "9997771112"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "tpl@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List Templates
    res = client.get("/form/api/v1/ai/templates", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["templates"]) == 6
    assert data["templates"][0]["id"] == "patient_reg"

    # 2. Get Specific Template (Incident Report)
    res = client.get("/form/api/v1/ai/templates/incident_report", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["template"]["title"] == "Incident Report"
    assert len(data["template"]["sections"]) == 1
    assert "Describe what happened" in str(data["template"])
    
    # 3. Verify IDs are generated
    section = data["template"]["sections"][0]
    assert "id" in section
    assert "id" in section["questions"][0]
