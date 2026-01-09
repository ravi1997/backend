import pytest
import uuid

def test_response_merge(client):
    # Setup: Login
    user_data = {
        "username": "merge_admin",
        "email": "merge_admin@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "9990001112"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "merge_admin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a form
    form_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    q1_id = str(uuid.uuid4())
    q2_id = str(uuid.uuid4())
    
    client.post("/form/api/v1/form/", json={
        "id": form_id,
        "title": "Merge Test Form",
        "slug": f"merge-test-{uuid.uuid4().hex[:6]}",
        "status": "published",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [
                    {"id": q1_id, "label": "Q1", "field_type": "input"},
                    {"id": q2_id, "label": "Q2", "field_type": "input"}
                ]
            }]
        }]
    }, headers=headers)

    # 2. Submit Response 1 (only Q1)
    res1 = client.post(f"/form/api/v1/form/{form_id}/responses", 
                      json={"data": {s1_id: {q1_id: "Val 1"}}}, 
                      headers=headers)
    rid1 = res1.get_json()["response_id"]

    # 3. Submit Response 2 (only Q2)
    res2 = client.post(f"/form/api/v1/form/{form_id}/responses", 
                      json={"data": {s1_id: {q2_id: "Val 2"}}}, 
                      headers=headers)
    rid2 = res2.get_json()["response_id"]

    # 4. Merge R1 and R2 into a new one
    merge_res = client.post(f"/form/api/v1/form/{form_id}/responses/merge", json={
        "source_response_ids": [rid1, rid2],
        "delete_sources": True
    }, headers=headers)
    assert merge_res.status_code == 200
    target_id = merge_res.get_json()["target_id"]

    # 5. Verify target has both Q1 and Q2
    target_res = client.get(f"/form/api/v1/form/{form_id}/responses/{target_id}", headers=headers)
    target_data = target_res.get_json()["data"]
    assert target_data[s1_id][q1_id] == "Val 1"
    assert target_data[s1_id][q2_id] == "Val 2"

    # 6. Verify sources are deleted
    list_res = client.get(f"/form/api/v1/form/{form_id}/responses", headers=headers)
    responses = list_res.get_json()
    ids = [str(r["_id"]) for r in responses]
    assert rid1 not in ids
    assert rid2 not in ids
    assert target_id in ids
