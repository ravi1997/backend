import pytest
import json
from app.models import Form, FormResponse

def get_admin_headers(client):
    payload = {
        "username": "admin_preview",
        "email": "admin_preview@example.com",
        "password": "AdminPassword123",
        "employee_id": "PREV001",
        "user_type": "employee",
        "mobile": "6655443311",
        "roles": ["admin"]
    }
    try:
        client.post("/form/api/v1/auth/register", json=payload)
    except:
        pass
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "admin_preview@example.com", "password": "AdminPassword123"})
    token = login_resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_preview_valid_submission(client):
    headers = get_admin_headers(client)
    
    # Create simple form
    s1_id = "11111111-1111-1111-1111-111111111111"
    q1_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    
    form_data = {
        "title": "Preview Form",
        "slug": "preview-form",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [
                    {"id": q1_id, "label": "Q1", "field_type": "input", "is_required": True}
                ]
            }]
        }]
    }
    
    resp = client.post("/form/api/v1/form/", json=form_data, headers=headers)
    assert resp.status_code == 201
    form_id = resp.get_json()["form_id"]
    
    # Valid payload
    payload = {
        "data": {
            s1_id: {q1_id: "Hello World"}
        }
    }
    
    preview_resp = client.post(f"/form/api/v1/form/{form_id}/preview", json=payload, headers=headers)
    assert preview_resp.status_code == 200
    res = preview_resp.get_json()
    assert res["valid"] is True
    assert res["message"] == "Validation successful"
    assert res["data"][s1_id][q1_id] == "Hello World"
    
    # Ensure NOT saved
    saved_count = FormResponse.objects(form=form_id).count()
    assert saved_count == 0

def test_preview_invalid_submission(client):
    headers = get_admin_headers(client)
    
    # Create new form
    s1_id = "22222222-2222-2222-2222-222222222222"
    q1_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    
    form_data = {
        "title": "Preview Invalid Form",
        "slug": "prev-inv-form",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [
                    {"id": q1_id, "label": "Q1", "field_type": "input", "is_required": True}
                ]
            }]
        }]
    }
    
    resp = client.post("/form/api/v1/form/", json=form_data, headers=headers)
    assert resp.status_code == 201
    form_id = resp.get_json()["form_id"]
    
    # Invalid payload (missing required field)
    payload = {
        "data": {
            s1_id: {}
        }
    }
    
    preview_resp = client.post(f"/form/api/v1/form/{form_id}/preview", json=payload, headers=headers)
    assert preview_resp.status_code == 200
    res = preview_resp.get_json()
    assert res["valid"] is False
    assert len(res["errors"]) > 0
    # Error structure is list of dicts: {'id': ..., 'error': ...}
    errors_str = str(res["errors"])
    assert "Required field missing" in errors_str
