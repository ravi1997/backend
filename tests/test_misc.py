import pytest

def get_tokens(client):
    client.post("/form/api/v1/auth/register", json={
        "username": "admin_misc", "email": "admin_misc@ex.com", "password": "Pass", 
        "employee_id": "AMISC1", "user_type": "employee", "roles": ["admin"], "mobile": "7766554433"
    })
    admin_token = client.post("/form/api/v1/auth/login", json={"email": "admin_misc@ex.com", "password": "Pass"}).get_json()["access_token"]
    
    client.post("/form/api/v1/auth/register", json={
        "username": "user_misc", "email": "user_misc@ex.com", "password": "Pass", 
        "employee_id": "UMISC1", "user_type": "employee", "roles": ["user"], "mobile": "6655443322"
    })
    user_token = client.post("/form/api/v1/auth/login", json={"email": "user_misc@ex.com", "password": "Pass"}).get_json()["access_token"]
    
    return admin_token, user_token

def test_get_form_analytics(client):
    admin_token, user_token = get_tokens(client)
    s1_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    form_payload = {
        "title": "Analytic Form", "slug": "ana-form", "status":"published", "is_public": True,
        "versions": [{"version": "1.0", "sections": [{"id": s1_id, "title": "S1", "questions": []}]}]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_resp.status_code == 201, create_resp.get_json()
    form_id = create_resp.get_json()["form_id"]
    submit_resp = client.post(f"/form/api/v1/form/{form_id}/responses", json={"data":{s1_id: {}}}, headers={"Authorization": f"Bearer {user_token}"})
    assert submit_resp.status_code == 201
    
    # Updated to use specific endpoint
    response = client.get(f"/form/api/v1/form/{form_id}/analytics/summary", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.get_json()["total_responses"] == 1

def test_public_submit_success(client):
    admin_token, _ = get_tokens(client)
    s1_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    q1_id = "dddddddd-dddd-dddd-dddd-dddddddddddd"
    
    # Must provide versions for validation
    form_payload = {
        "title": "Public Form", "slug": "pub-form-misc", "status":"published", "is_public": True,
        "versions": [{"version": "1.0", "sections": [{"id": s1_id, "title": "S1", "questions": [{"id": q1_id, "label": "Q1", "field_type": "input"}]}]}]
    }
    
    form_id = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"}).get_json()["form_id"]
    
    response = client.post(f"/form/api/v1/form/{form_id}/public-submit", json={"data":{s1_id:{q1_id:"Public Answer"}}})
    assert response.status_code == 201
    assert response.get_json()["message"] == "Response submitted anonymously"

def test_public_submit_failure_non_public(client):
    admin_token, _ = get_tokens(client)
    form_id = client.post("/form/api/v1/form/", json={
        "title": "Private Form", "slug": "priv-form", "status":"published", "is_public": False
    }, headers={"Authorization": f"Bearer {admin_token}"}).get_json()["form_id"]
    
    response = client.post(f"/form/api/v1/form/{form_id}/public-submit", json={"data":{}})
    assert response.status_code == 403
    assert "Form is not public" in response.get_json()["error"]

def test_set_form_expiration(client):
    admin_token, _ = get_tokens(client)
    form_id = client.post("/form/api/v1/form/", json={
        "title": "Exp Form", "slug": "exp-form", "is_public": True
    }, headers={"Authorization": f"Bearer {admin_token}"}).get_json()["form_id"]
    
    expires_at = "2026-12-31T23:59:59Z"
    response = client.patch(f"/form/api/v1/form/{form_id}/expire", json={"expires_at": expires_at}, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    
    get_resp = client.get(f"/form/api/v1/form/{form_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert get_resp.get_json()["expires_at"] is not None

def test_list_expired_forms(client):
    admin_token, _ = get_tokens(client)
    # Create an already expired form is tricky via API if validation exists, 
    # but the list_expired_forms just queries the DB.
    # We'll just check if the endpoint works.
    response = client.get("/form/api/v1/form/expired", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_export_responses(client):
    admin_token, user_token = get_tokens(client)
    form_payload = {
        "title": "Export Form", "slug": "ex-form", "status":"published", "is_public": True,
        "versions": [{"version": "1.0", "sections": [{"id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "title": "S1", "questions": []}]}]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_resp.status_code == 201, create_resp.get_json()
    form_id = create_resp.get_json()["form_id"]
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data":{}}, headers={"Authorization": f"Bearer {user_token}"})
    
    # CSV
    response = client.get(f"/form/api/v1/form/{form_id}/export/csv", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "text/csv" in response.content_type
    
    # JSON
    response = client.get(f"/form/api/v1/form/{form_id}/export/json", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "application/json" in response.content_type
    assert "form_metadata" in response.get_json()
