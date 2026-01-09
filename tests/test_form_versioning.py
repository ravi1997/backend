import pytest
import uuid

def test_form_versioning(client):
    # Setup: Login
    user_data = {
        "username": "v_admin",
        "email": "v_admin@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "5556667778"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "v_admin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a form (v1.0)
    form_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    q1_id = str(uuid.uuid4())
    
    client.post("/form/api/v1/form/", json={
        "id": form_id,
        "title": "Version Form",
        "slug": f"v-test-{uuid.uuid4().hex[:6]}",
        "status": "published",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [{"id": q1_id, "label": "Q1", "field_type": "input"}]
            }]
        }]
    }, headers=headers)

    # 2. Add New Version (v2.0)
    version_data = {
        "version": "2.0",
        "sections": [{
            "id": s1_id,
            "title": "S1 Updated",
            "questions": [{"id": q1_id, "label": "Q1 Updated", "field_type": "input"}]
        }],
        "activate": True
    }
    client.post(f"/form/api/v1/form/{form_id}/versions", json=version_data, headers=headers)

    # 3. Verify Active Version Fetch
    res = client.get(f"/form/api/v1/form/{form_id}", headers=headers)
    data = res.get_json()
    assert data["active_version"] == "2.0"
    assert data["versions"][1]["sections"][0]["title"] == "S1 Updated"

    # 4. Fetch Specific Version (v1.0)
    res = client.get(f"/form/api/v1/form/{form_id}?v=1.0", headers=headers)
    data = res.get_json()
    assert len(data["versions"]) == 1
    assert data["versions"][0]["version"] == "1.0"
    assert data["versions"][0]["sections"][0]["title"] == "S1"

    # 5. Rollback to v1.0
    client.patch(f"/form/api/v1/form/{form_id}/versions/1.0/activate", headers=headers)
    res = client.get(f"/form/api/v1/form/{form_id}", headers=headers)
    assert res.get_json()["active_version"] == "1.0"

    # 6. Verify Submission Uses Active Version
    client.post(f"/form/api/v1/form/{form_id}/responses", 
               json={"data": {s1_id: {q1_id: "val"}}}, 
               headers=headers)
    
    # 7. List responses for the form to check version
    res = client.get(f"/form/api/v1/form/{form_id}/responses", headers=headers)
    responses = res.get_json()
    assert responses[0]["version"] == "1.0"
