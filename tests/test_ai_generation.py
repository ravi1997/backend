import pytest

def test_ai_form_generation(client):
    # Setup: Login
    user_data = {
        "username": "gen_tester",
        "email": "gen@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "9998881112"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "gen@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Generate Patient Form
    res = client.post("/form/api/v1/ai/generate", json={
        "prompt": "I need a medical patient intake form"
    }, headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert "Patient Intake" in data["suggestion"]["title"]
    assert len(data["suggestion"]["sections"]) > 0
    assert "Full Name" in str(data["suggestion"])

    # 2. Generate Job Form
    res = client.post("/form/api/v1/ai/generate", json={
        "prompt": "Create a job application"
    }, headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert "Job Application" in data["suggestion"]["title"]
    assert "Resume Upload" in str(data["suggestion"])

    # 3. Generate Fallback Form
    res = client.post("/form/api/v1/ai/generate", json={
        "prompt": "Something random"
    }, headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert "Feedback" in data["suggestion"]["title"]
