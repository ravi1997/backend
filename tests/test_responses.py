import pytest
from datetime import datetime, timedelta, timezone

def get_tokens(client):
    # Register admin and creator
    client.post("/form/api/v1/auth/register", json={
        "username": "admin_resp", "email": "admin_resp@ex.com", "password": "Pass", 
        "employee_id": "ARESP1", "user_type": "employee", "roles": ["admin"], "mobile": "9988776655"
    })
    admin_token = client.post("/form/api/v1/auth/login", json={"email": "admin_resp@ex.com", "password": "Pass"}).get_json()["access_token"]
    
    client.post("/form/api/v1/auth/register", json={
        "username": "submitter", "email": "sub@ex.com", "password": "Pass", 
        "employee_id": "SUB1", "user_type": "employee", "roles": ["user"], "mobile": "8877665544"
    })
    user_token = client.post("/form/api/v1/auth/login", json={"email": "sub@ex.com", "password": "Pass"}).get_json()["access_token"]
    
    return admin_token, user_token

def test_submit_response_success(client):
    admin_token, user_token = get_tokens(client)
    
    s1_id = "11111111-1111-1111-1111-111111111111"
    q1_id = "22222222-2222-2222-2222-222222222222"
    form_payload = {
        "title": "Published Form",
        "slug": "pub-form",
        "status": "published",
        "is_public": True,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id, "title": "S1",
                "questions": [
                    {"id": q1_id, "label": "Q1", "field_type": "input", "is_required": True}
                ]
            }]
        }]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_resp.status_code == 201, create_resp.get_json()
    form_id = create_resp.get_json()["form_id"]
    
    # Submit response
    resp_payload = {
        "data": {
            s1_id: {q1_id: "Answer 1"}
        }
    }
    response = client.post(f"/form/api/v1/form/{form_id}/responses", json=resp_payload, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 201
    assert "response_id" in response.get_json()

def test_submit_response_validation_failure(client):
    admin_token, user_token = get_tokens(client)
    
    s1_id = "33333333-3333-3333-3333-333333333333"
    q1_id = "44444444-4444-4444-4444-444444444444"
    form_payload = {
        "title": "Val Form", "slug": "val-form", "status": "published",
        "is_public": True,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id, "title": "S1",
                "questions": [{"id": q1_id, "label": "Q1", "field_type": "input", "is_required": True}]
            }]
        }]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_resp.status_code == 201
    form_id = create_resp.get_json()["form_id"]
    
    # Missing required field
    resp_payload = {"data": {s1_id: {q1_id: ""}}}
    response = client.post(f"/form/api/v1/form/{form_id}/responses", json=resp_payload, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 422
    assert "Validation failed" in response.get_json()["error"]

def test_submit_to_draft_form(client):
    admin_token, user_token = get_tokens(client)
    
    form_payload = {"title": "Draft Form", "slug": "draft-form", "status": "draft", "is_public": True}
    form_id = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"}).get_json()["form_id"]
    
    response = client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {}}, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    assert "not accepting submissions" in response.get_json()["error"]

def test_search_responses(client):
    admin_token, user_token = get_tokens(client)
    
    s1_id = "55555555-5555-5555-5555-555555555555"
    q1_id = "66666666-6666-6666-6666-666666666666"
    form_payload = {
        "title": "Search Form", "slug": "search-form", "status": "published",
        "is_public": True,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id, "title": "S1",
                "questions": [{"id": q1_id, "label": "Q1", "field_type": "input"}]
            }]
        }]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_resp.status_code == 201
    form_id = create_resp.get_json()["form_id"]
    
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data":{s1_id:{q1_id:"Apple"}}}, headers={"Authorization": f"Bearer {user_token}"})
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data":{s1_id:{q1_id:"Banana"}}}, headers={"Authorization": f"Bearer {user_token}"})
    
    # Search
    search_payload = {
        "data": {
            q1_id: {"value": "Apple", "type": "string", "op": "eq"}
        }
    }
    response = client.post(f"/form/api/v1/form/{form_id}/responses/search", json=search_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    results = response.get_json()["responses"]
    assert len(results) == 1
    # Note: Search returns section-nested data but flattened key in the return might vary based on filter_response_data implementation
    # Let's check if the value exists in one of the sections
    found = False
    for sid, sdata in results[0]["data"].items():
        if sdata.get(q1_id) == "Apple":
            found = True
    assert found

def test_archive_response(client):
    admin_token, user_token = get_tokens(client)
    form_payload = {
        "title": "Arc Form", "slug": "arc-form", "status":"published", "is_public": True,
        "versions": [{"version": "1.0", "sections": [{"id": "cccccccc-cccc-cccc-cccc-cccccccccccc", "title": "S1", "questions": []}]}]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_resp.status_code == 201, create_resp.get_json()
    form_id = create_resp.get_json()["form_id"]
    
    submit_resp = client.post(f"/form/api/v1/form/{form_id}/responses", json={"data":{}}, headers={"Authorization": f"Bearer {user_token}"})
    assert submit_resp.status_code == 201, submit_resp.get_json()
    resp_id = submit_resp.get_json()["response_id"]
    
    response = client.patch(f"/form/api/v1/form/{form_id}/responses/{resp_id}/archive", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    
    get_resp = client.get(f"/form/api/v1/form/{form_id}/responses/{resp_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert get_resp.get_json()["deleted"] is True
