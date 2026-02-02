import pytest
import uuid

def get_admin_token(client):
    email = f"cf_admin_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/form/api/v1/auth/register", json={
        "username": "cf_admin", "email": email, "password": "Pass", 
        "employee_id": f"CF_{uuid.uuid4().hex[:4]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": f"33{uuid.uuid4().int % 100000000:08d}"
    })
    return client.post("/form/api/v1/auth/login", json={"email": email, "password": "Pass"}).get_json()["access_token"]

def test_custom_fields_library(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Save New Template
    payload = {
        "name": "NPS Score",
        "category": "metrics",
        "question_data": {
            "label": "How likely are you to recommend us?",
            "field_type": "rating",
            "meta_data": {"max": 10}
        }
    }
    
    res = client.post("/form/api/v1/custom-fields/", json=payload, headers=headers)
    assert res.status_code == 201
    template_id = res.get_json()["id"]
    
    # 2. List Templates (verify category filter)
    res = client.get("/form/api/v1/custom-fields/?category=metrics", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) >= 1
    assert data[0]["name"] == "NPS Score"
    assert data[0]["question_data"]["label"] == "How likely are you to recommend us?"
    
    # 3. Delete Template
    res = client.delete(f"/form/api/v1/custom-fields/{template_id}", headers=headers)
    assert res.status_code == 200
    
    # Verify deletion
    res = client.get("/form/api/v1/custom-fields/?category=metrics", headers=headers)
    # The list might contain other tests' data if not cleaned, but ours should be gone.
    # Since we use a fresh DB or mock usually, it should be empty.
    # We can check specific ID absence if list is non-empty.
    ids = [item["id"] for item in res.get_json()]
    assert template_id not in ids
