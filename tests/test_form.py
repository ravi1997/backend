import pytest

def get_creator_token(client):
    payload = {
        "username": "form_creator",
        "email": "creator@example.com",
        "password": "CreatorPassword123",
        "employee_id": "CR001",
        "user_type": "employee",
        "mobile": "5544332211",
        "roles": ["creator"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "creator@example.com", "password": "CreatorPassword123"})
    return login_resp.get_json()["access_token"]

def get_admin_token(client):
    payload = {
        "username": "admin_user_form",
        "email": "admin_form@example.com",
        "password": "AdminPassword123",
        "employee_id": "ADM002",
        "user_type": "employee",
        "mobile": "4433221100",
        "roles": ["admin"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "admin_form@example.com", "password": "AdminPassword123"})
    return login_resp.get_json()["access_token"]

def test_create_form_success(client):
    token = get_creator_token(client)
    s1_id = "77777777-7777-7777-7777-777777777777"
    q1_id = "88888888-8888-8888-8888-888888888888"
    payload = {
        "title": "New Form",
        "slug": "new-form",
        "is_public": True,
        "versions": [
            {
                "version": "1.0",
                "sections": [
                    {
                        "id": s1_id,
                        "title": "Section 1",
                        "questions": [
                            {"id": q1_id, "label": "Question 1", "field_type": "input"}
                        ]
                    }
                ]
            }
        ]
    }
    response = client.post("/form/api/v1/form/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201, response.get_json()
    assert "form_id" in response.get_json()

def test_list_forms(client):
    token = get_creator_token(client)
    # Create two forms
    client.post("/form/api/v1/form/", json={"title": "F1", "slug": "f1"}, headers={"Authorization": f"Bearer {token}"})
    client.post("/form/api/v1/form/", json={"title": "F2", "slug": "f2"}, headers={"Authorization": f"Bearer {token}"})
    
    response = client.get("/form/api/v1/form/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    forms = response.get_json()
    assert len(forms) >= 2

def test_get_form_details(client):
    token = get_creator_token(client)
    create_resp = client.post("/form/api/v1/form/", json={"title": "Details Form", "slug": "details-form"}, headers={"Authorization": f"Bearer {token}"})
    form_id = create_resp.get_json()["form_id"]
    
    response = client.get(f"/form/api/v1/form/{form_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["title"] == "Details Form"

def test_update_form(client):
    token = get_creator_token(client)
    create_resp = client.post("/form/api/v1/form/", json={"title": "Old Title", "slug": "old-slug"}, headers={"Authorization": f"Bearer {token}"})
    form_id = create_resp.get_json()["form_id"]
    
    response = client.put(f"/form/api/v1/form/{form_id}", json={"title": "New Title"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    get_resp = client.get(f"/form/api/v1/form/{form_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.get_json()["title"] == "New Title"

def test_delete_form_admin(client):
    creator_token = get_creator_token(client)
    admin_token = get_admin_token(client)
    
    create_resp = client.post("/form/api/v1/form/", json={"title": "Delete Me", "slug": "delete-me"}, headers={"Authorization": f"Bearer {creator_token}"})
    form_id = create_resp.get_json()["form_id"]
    
    # Try deleting as creator (should fail if only admin can delete)
    # The SRS says admin or superadmin required for delete.
    response = client.delete(f"/form/api/v1/form/{form_id}", headers={"Authorization": f"Bearer {creator_token}"})
    assert response.status_code == 403
    
    # Delete as admin
    response = client.delete(f"/form/api/v1/form/{form_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    
    # Verify deleted
    response = client.get(f"/form/api/v1/form/{form_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404
