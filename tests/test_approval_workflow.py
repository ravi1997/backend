import pytest
import uuid

def test_approval_workflow(client):
    # Setup: Login as admin
    admin_data = {
        "username": "final_boss",
        "email": "admin@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "1231231234"
    }
    client.post("/form/api/v1/auth/register", json=admin_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "AdminPassword123"
    })
    atoken = login_res.get_json()["access_token"]
    aheaders = {"Authorization": f"Bearer {atoken}"}

    # Setup: Login as manager
    mgr_data = {
        "username": "manager_joe",
        "email": "joe@example.com",
        "password": "ManagerPassword123",
        "roles": ["manager"],
        "user_type": "employee",
        "mobile": "4324324321"
    }
    client.post("/form/api/v1/auth/register", json=mgr_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "joe@example.com",
        "password": "ManagerPassword123"
    })
    mtoken = login_res.get_json()["access_token"]
    mheaders = {"Authorization": f"Bearer {mtoken}"}

    # 1. Create a form with 2-step approval
    s1_id = str(uuid.uuid4())
    q1_id = str(uuid.uuid4())
    
    create_res = client.post("/form/api/v1/form/", json={
        "title": "Approval Form",
        "slug": f"app-test-{uuid.uuid4().hex[:6]}",
        "status": "published",
        "is_public": True,
        "approval_enabled": True,
        "approval_steps": [
            {"name": "Manager Review", "required_role": "manager", "order": 1},
            {"name": "Admin Review", "required_role": "admin", "order": 2}
        ],
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [{"id": q1_id, "label": "Q1", "field_type": "input"}]
            }]
        }]
    }, headers=aheaders)
    assert create_res.status_code == 201
    form_id = create_res.get_json()["form_id"]

    # 2. Submit Response
    res = client.post(f"/form/api/v1/form/{form_id}/responses", 
                      json={"data": {s1_id: {q1_id: "Submit"}}}, 
                      headers=mheaders)
    assert res.status_code in [200, 201]
    rid = res.get_json()["response_id"]

    # 3. Check status (should be pending)
    res = client.get(f"/form/api/v1/form/{form_id}/responses/{rid}", headers=aheaders)
    assert res.get_json()["status"] == "pending"

    # 4. Try to approve as admin (should work because admin is superuser in my logic)
    # Actually let's test the manager first
    # 4a. Manager approves Step 1
    res = client.post(f"/form/api/v1/form/{form_id}/responses/{rid}/approve", 
                      json={"comment": "Manager OK"}, headers=mheaders)
    assert res.status_code == 200
    assert res.get_json()["completed_steps"] == 1
    assert res.get_json()["status"] == "pending" # Still pending because step 2 exists

    # 5. Try to approve step 2 as Manager (should fail)
    res = client.post(f"/form/api/v1/form/{form_id}/responses/{rid}/approve", 
                      json={"comment": "Manager OK again"}, headers=mheaders)
    assert res.status_code == 403 # Manager doesn't have 'admin' role

    # 6. Admin approves Step 2 (Final)
    res = client.post(f"/form/api/v1/form/{form_id}/responses/{rid}/approve", 
                      json={"comment": "Admin Final OK"}, headers=aheaders)
    assert res.status_code == 200
    assert res.get_json()["completed_steps"] == 2
    assert res.get_json()["status"] == "approved"

    # 7. Verification
    res = client.get(f"/form/api/v1/form/{form_id}/responses/{rid}", headers=aheaders)
    data = res.get_json()
    assert len(data["approval_history"]) == 2
    assert data["approval_history"][0]["status"] == "approved"
    assert data["approval_history"][1]["status"] == "approved"
