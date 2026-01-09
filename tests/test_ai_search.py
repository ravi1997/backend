import pytest
import uuid

def test_ai_search(client):
    # Setup: Login
    user_data = {
        "username": "search_tester",
        "email": "search@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "9992223334"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "search@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a form
    form_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    q1_id = str(uuid.uuid4()) # Name
    q2_id = str(uuid.uuid4()) # Age
    q3_id = str(uuid.uuid4()) # Condition
    
    client.post("/form/api/v1/form/", json={
        "id": form_id,
        "title": "Search Test Form",
        "slug": f"search-test-{uuid.uuid4().hex[:6]}",
        "status": "published",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [
                    {"id": q1_id, "label": "Name", "field_type": "input"},
                    {"id": q2_id, "label": "Age", "field_type": "input"},
                    {"id": q3_id, "label": "Condition", "field_type": "input"}
                ]
            }]
        }]
    }, headers=headers)

    # 2. Submit Responses
    # R1: 65, Diabetes
    client.post(f"/form/api/v1/form/{form_id}/responses", 
                json={"data": {s1_id: {q1_id: "John", q2_id: 65, q3_id: "Diabetes"}}}, 
                headers=headers)
    # R2: 25, Healthy
    client.post(f"/form/api/v1/form/{form_id}/responses", 
                json={"data": {s1_id: {q1_id: "Jane", q2_id: 25, q3_id: "Healthy"}}}, 
                headers=headers)
    # R3: 70, Flu
    client.post(f"/form/api/v1/form/{form_id}/responses", 
                json={"data": {s1_id: {q1_id: "Bob", q2_id: 70, q3_id: "Flu"}}}, 
                headers=headers)

    # 3. Test Search: "Find all patients over 60 with diabetes"
    search_res = client.post(f"/form/api/v1/ai/{form_id}/search", json={
        "query": "Find all patients over 60 with diabetes"
    }, headers=headers)
    assert search_res.status_code == 200
    data = search_res.get_json()
    assert data["count"] == 1 # Only John
    
    # 4. Test Search: "over 60"
    search_res = client.post(f"/form/api/v1/ai/{form_id}/search", json={
        "query": "over 60"
    }, headers=headers)
    assert search_res.get_json()["count"] == 2 # John (65) and Bob (70)

    # 5. Test Search: "under 30"
    search_res = client.post(f"/form/api/v1/ai/{form_id}/search", json={
        "query": "under 30"
    }, headers=headers)
    assert search_res.get_json()["count"] == 1 # Jane (25)
