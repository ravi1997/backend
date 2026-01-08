import pytest
import json
from datetime import datetime, timezone

def get_tokens(client):
    # Register admin and creator
    client.post("/form/api/v1/auth/register", json={
        "username": "admin_cond", "email": "admin_cond@ex.com", "password": "Pass", 
        "employee_id": "ACOND1", "user_type": "employee", "roles": ["admin"], "mobile": "9988770011"
    })
    admin_token = client.post("/form/api/v1/auth/login", json={"email": "admin_cond@ex.com", "password": "Pass"}).get_json()["access_token"]
    
    client.post("/form/api/v1/auth/register", json={
        "username": "user_cond", "email": "user_cond@ex.com", "password": "Pass", 
        "employee_id": "UCOND1", "user_type": "employee", "roles": ["user"], "mobile": "8877660022"
    })
    user_token = client.post("/form/api/v1/auth/login", json={"email": "user_cond@ex.com", "password": "Pass"}).get_json()["access_token"]
    
    return admin_token, user_token

def test_conditional_required_logic(client):
    admin_token, user_token = get_tokens(client)
    
    s1_id = "11111111-1111-1111-1111-111111111111"
    q_trig_id = "22222222-2222-2222-2222-222222222222"
    q_cond_id = "33333333-3333-3333-3333-333333333333"
    
    form_payload = {
        "title": "Conditional Form",
        "slug": "cond-form",
        "status": "published",
        "is_public": True,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id, 
                "title": "S1",
                "questions": [
                    {
                        "id": q_trig_id, 
                        "label": "Do you need extra info?", 
                        "field_type": "radio", 
                        "options": [
                            {"option_label": "Yes", "option_value": "yes"},
                            {"option_label": "No", "option_value": "no"}
                        ]
                    },
                    {
                        "id": q_cond_id, 
                        "label": "Please specify", 
                        "field_type": "input",
                        "is_required": False,  # Not required by default
                        "required_condition": f"{q_trig_id} == 'yes'"  # BUT required if trigger is 'yes'
                    }
                ]
            }]
        }]
    }
    
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_resp.status_code == 201, f"Create failed: {create_resp.get_json()}"
    form_id = create_resp.get_json()["form_id"]
    
    # Case 1: Trigger is 'no', conditional field empty -> Should PASS
    payload_pass = {
        "data": {
            s1_id: {
                q_trig_id: "no",
                q_cond_id: ""
            }
        }
    }
    resp = client.post(f"/form/api/v1/form/{form_id}/responses", json=payload_pass, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 201, f"Should pass when condition not met. Error: {resp.get_json()}"

    # Case 2: Trigger is 'yes', conditional field empty -> Should FAIL
    payload_fail = {
        "data": {
            s1_id: {
                q_trig_id: "yes",
                q_cond_id: ""
            }
        }
    }
    resp = client.post(f"/form/api/v1/form/{form_id}/responses", json=payload_fail, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 422
    assert "Required field missing" in str(resp.get_json())

    # Case 3: Trigger is 'yes', conditional field filled -> Should PASS
    payload_pass_2 = {
        "data": {
            s1_id: {
                q_trig_id: "yes",
                q_cond_id: "Some info"
            }
        }
    }
    resp = client.post(f"/form/api/v1/form/{form_id}/responses", json=payload_pass_2, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 201

def test_public_submission_validation(client):
    """Verify that public submissions now also have validation"""
    admin_token, _ = get_tokens(client)
    
    s1_id = "44444444-4444-4444-4444-444444444444"
    q1_id = "55555555-5555-5555-5555-555555555555"
    
    form_payload = {
        "title": "Public Val Form", "slug": "pub-val-form", "status": "published", "is_public": True,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id, "title": "S1",
                "questions": [{"id": q1_id, "label": "Req", "field_type": "input", "is_required": True}]
            }]
        }]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {admin_token}"})
    form_id = create_resp.get_json()["form_id"]
    
    # Submit empty required field to public endpoint
    resp = client.post(f"/form/api/v1/form/{form_id}/public-submit", json={"data": {s1_id: {q1_id: ""}}})
    
    # Before the fix, this might have passed (201). Now it should fail (422)
    assert resp.status_code == 422
    assert "Validation failed" in resp.get_json()["error"]
