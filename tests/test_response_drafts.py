import pytest
import json
from app.models import Form, FormResponse

def get_admin_headers(client):
    payload = {
        "username": "admin_drafts",
        "email": "admin_drafts@example.com",
        "password": "AdminPassword123",
        "employee_id": "DRAFT001",
        "user_type": "employee",
        "mobile": "7788990011",
        "roles": ["admin"]
    }
    try:
        client.post("/form/api/v1/auth/register", json=payload)
    except:
        pass
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "admin_drafts@example.com", "password": "AdminPassword123"})
    token = login_resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_draft_lifecycle(client):
    headers = get_admin_headers(client)
    
    # 1. Create form with required fields
    s1_id = "11111111-1111-1111-1111-111111111111"
    q1_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    
    form_data = {
        "title": "Draft Form",
        "slug": "draft-form",
        "status": "published",
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
    form_id = resp.get_json()["form_id"]
    
    # 2. Save as draft (missing required field)
    draft_payload = {
        "data": {
            s1_id: {} # Empty, missing Q1
        }
    }
    
    # Attempt normal submit -> should fail
    submit_resp = client.post(f"/form/api/v1/form/{form_id}/responses", json=draft_payload, headers=headers)
    assert submit_resp.status_code == 422
    
    # Save as draft -> should succeed
    draft_resp = client.post(f"/form/api/v1/form/{form_id}/responses?draft=true", json=draft_payload, headers=headers)
    assert draft_resp.status_code == 201
    response_id = draft_resp.get_json()["response_id"]
    
    # Verify is_draft in DB
    resp_obj = FormResponse.objects.get(id=response_id)
    assert resp_obj.is_draft is True
    
    # 3. Update draft (still draft)
    update_payload = {
        "data": {
            s1_id: {q1_id: "Partially filled"}
        }
    }
    update_resp = client.post(f"/form/api/v1/form/{form_id}/responses/{response_id}?draft=true", json=update_payload, headers=headers)
    # Note: earlier I might have seen PUT/POST for update. responses.py has PUT for update_submission.
    # Wait, my replace_file_content earlier updated update_submission which is @form_bp.route("/<form_id>/responses/<response_id>", methods=["PUT"])
    
    update_resp = client.put(f"/form/api/v1/form/{form_id}/responses/{response_id}?draft=true", json=update_payload, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.get_json()["is_draft"] is True
    
    # 4. Finish and Submit Draft
    finish_payload = {
        "data": {
            s1_id: {q1_id: "Fully filled"}
        }
    }
    finish_resp = client.put(f"/form/api/v1/form/{form_id}/responses/{response_id}", json=finish_payload, headers=headers)
    assert finish_resp.status_code == 200
    assert finish_resp.get_json()["is_draft"] is False
    
    # Verify in DB
    resp_obj.reload()
    assert resp_obj.is_draft is False
    assert resp_obj.data[s1_id][q1_id] == "Fully filled"

def test_draft_filtering(client):
    headers = get_admin_headers(client)
    
    # Create form
    form_data = {
        "title": "Filter Form",
        "slug": "filter-form",
        "status": "published",
        "versions": [{"version": "1.0", "sections": []}]
    }
    resp = client.post("/form/api/v1/form/", json=form_data, headers=headers)
    form_id = resp.get_json()["form_id"]
    
    # Create 1 draft, 1 submission
    client.post(f"/form/api/v1/form/{form_id}/responses?draft=true", json={"data": {}}, headers=headers)
    client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {}}, headers=headers)
    
    # List submissions (default)
    list_resp = client.get(f"/form/api/v1/form/{form_id}/responses", headers=headers)
    responses = list_resp.get_json()
    assert len(responses) == 1
    assert responses[0]["is_draft"] is False
    
    # List drafts
    list_drafts_resp = client.get(f"/form/api/v1/form/{form_id}/responses?is_draft=true", headers=headers)
    drafts = list_drafts_resp.get_json()
    assert len(drafts) == 1
    assert drafts[0]["is_draft"] is True
