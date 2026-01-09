
import pytest
import json
from app.models.Workflow import FormWorkflow

def get_admin_token(client):
    payload = {
        "username": "admin_wf",
        "email": "admin_wf@example.com",
        "password": "Password123",
        "employee_id": "ADM_WF",
        "user_type": "employee",
        "mobile": "9998887771",
        "roles": ["admin"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "admin_wf@example.com", "password": "Password123"})
    return login_resp.get_json()["access_token"]

def get_user_token(client):
    payload = {
        "username": "user_wf",
        "email": "user_wf@example.com",
        "password": "Password123",
        "employee_id": "USR_WF",
        "user_type": "employee",
        "mobile": "9998887772",
        "roles": ["user"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "user_wf@example.com", "password": "Password123"})
    return login_resp.get_json()["access_token"]

def create_test_form(client, token, title="Test Form"):
    form_data = {
        "title": title,
        "slug": title.lower().replace(" ", "-"),
        "status": "published",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "title": "Section 1",
                "questions": [
                    {"field_type": "input", "label": "Name", "is_required": False},
                    {"field_type": "input", "label": "Age", "is_required": False}
                ]
            }]
        }]
    }
    resp = client.post("/form/api/v1/form/", json=form_data, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    form_id = resp.get_json()["form_id"]
    
    # Fetch form to get IDs
    resp = client.get(f"/form/api/v1/form/{form_id}", headers={"Authorization": f"Bearer {token}"})
    data = resp.get_json()
    
    mapping = {}
    sections = data.get("versions", [])[0].get("sections", [])
    sec_id = None
    for sec in sections:
        sec_id = sec.get("id") or sec.get("_id")
        for q in sec.get("questions", []):
            qid = q.get("_id") or q.get("id")
            mapping[q["label"]] = qid
            
    return form_id, mapping, sec_id

def test_workflow_crud(client):
    admin_token = get_admin_token(client)
    form_id, src_map, _ = create_test_form(client, admin_token, "Workflow Source")
    target_form_id, tgt_map, _ = create_test_form(client, admin_token, "Workflow Target")
    
    msg = "Creating workflow..."
    # 1. Create Workflow
    payload = {
        "name": "Age Check Workflow",
        "trigger_form_id": form_id,
        "trigger_condition": f"int(answers.get('{src_map['Age']}', 0)) > 18",
        "actions": [
            {
                "type": "redirect_to_form",
                "target_form_id": target_form_id,
                "data_mapping": {tgt_map['Name']: src_map['Name']}
            }
        ]
    }
    
    resp = client.post("/form/api/v1/workflows/", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    wf_id = resp.get_json()["id"]
    
    # 2. Get Workflow
    resp = client.get(f"/form/api/v1/workflows/{wf_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Age Check Workflow"
    
    # 3. List Workflows
    resp = client.get("/form/api/v1/workflows/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1
    
    # 4. Update Workflow
    resp = client.put(f"/form/api/v1/workflows/{wf_id}", json={"name": "Updated Workflow"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    
    # 5. Delete Workflow
    resp = client.delete(f"/form/api/v1/workflows/{wf_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200

def test_workflow_execution(client):
    admin_token = get_admin_token(client)
    source_form_id, src_map, src_sec_id = create_test_form(client, admin_token, "Source Form Exec")
    target_form_id, tgt_map, _ = create_test_form(client, admin_token, "Target Form Exec")
    
    # Create Workflow: If Age > 18, redirect
    payload = {
        "name": "Adult Redirect",
        "trigger_form_id": source_form_id,
        "trigger_condition": f"int(answers.get('{src_map['Age']}', 0)) > 18",
        "actions": [{
            "type": "redirect_to_form",
            "target_form_id": target_form_id,
            "data_mapping": {tgt_map['Name']: src_map['Name']}
        }]
    }
    client.post("/form/api/v1/workflows/", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    
    # Test submission that DOES trigger
    submission_data = {
        "data": {
            src_sec_id: {
                src_map['Name']: "Alice",
                src_map['Age']: 25
            }
        }
    }
    resp = client.post(f"/form/api/v1/form/{source_form_id}/responses", json=submission_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    json_data = resp.get_json()
    assert "workflow_action" in json_data
    assert json_data["workflow_action"]["actions"][0]["type"] == "redirect_to_form"
    
    # Test submission that DOES NOT trigger
    submission_data_young = {
        "data": {
            src_sec_id: {
                 src_map['Name']: "Bob",
                 src_map['Age']: 15
            }
        }
    }
    resp = client.post(f"/form/api/v1/form/{source_form_id}/responses", json=submission_data_young, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 201
    json_data = resp.get_json()
    assert "workflow_action" not in json_data
