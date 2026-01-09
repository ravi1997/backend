
import pytest
import uuid
import time
from datetime import datetime, timedelta, timezone

def get_admin_token(client):
    email = f"integrity_admin_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"77{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "integrity_admin", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_hidden_field_stripping(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Form
    # Q1: choice (Yes/No)
    # Q2: text (Reason), visible if Q1 == 'Yes'
    
    q1_id = str(uuid.uuid4())
    q2_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    
    form_payload = {
        "title": "Integrity Form", 
        "slug": f"integrity-form-{uuid.uuid4().hex[:6]}", 
        "status": "published",
        "is_public": True,
        "versions": [{
            "version": "1.0", 
            "sections": [{
                "id": s1_id, 
                "title": "S1", 
                "questions": [
                    {
                        "id": q1_id,
                        "label": "Do you agree?",
                        "field_type": "radio",
                        "options": [{"option_label": "Yes", "option_value": "Yes"}, {"option_label": "No", "option_value": "No"}],
                        "is_required": True
                    },
                    {
                        "id": q2_id,
                        "label": "Reason",
                        "field_type": "input",
                        "is_required": False,
                        # Condition: Q1 == 'Yes'
                        # v_{q1_id} needs to be sanitised. 
                        # Ideally user inputs 'v_<uuid>'. 
                        # But let's rely on standard python eval with replaced keys.
                        # Condition: "v_... == 'Yes'"
                        "visibility_condition": f"v_{q1_id.replace('-', '_')} == 'Yes'"
                    }
                ]
            }]
        }]
    }
    
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    assert res.status_code == 201
    form_id = res.get_json()["form_id"]
    
    # 2. Submit with Q1='No' and Q2='ShouldBeHidden'
    # Since Q1 is No, Q2 is hidden. Data for Q2 should be stripped.
    payload_hidden = {
        "data": {
            s1_id: {
                q1_id: "No",
                q2_id: "ShouldBeHidden"
            }
        }
    }
    
    res_sub = client.post(f"/form/api/v1/form/{form_id}/responses", json=payload_hidden, headers=headers)
    assert res_sub.status_code == 201
    resp_id = res_sub.get_json()["response_id"]
    
    # Verify stored data
    from app.models.Form import FormResponse
    saved_resp = FormResponse.objects.get(id=resp_id)
    saved_data = saved_resp.data
    
    # Q1 should be present
    assert saved_data[s1_id][q1_id] == "No"
    # Q2 should be ABSENT
    assert q2_id not in saved_data[s1_id], f"Hidden field Q2 was not stripped! Data: {saved_data}"
    
    # 3. Submit with Q1='Yes' and Q2='VisibleReason'
    payload_visible = {
        "data": {
            s1_id: {
                q1_id: "Yes",
                q2_id: "VisibleReason"
            }
        }
    }
    res_sub2 = client.post(f"/form/api/v1/form/{form_id}/responses", json=payload_visible, headers=headers)
    assert res_sub2.status_code == 201
    resp_id2 = res_sub2.get_json()["response_id"]
    
    saved_resp2 = FormResponse.objects.get(id=resp_id2)
    saved_data2 = saved_resp2.data
    
    assert saved_data2[s1_id][q1_id] == "Yes"
    assert saved_data2[s1_id][q2_id] == "VisibleReason"

def test_validation_blockcheck(client):
    # Verify validation still works
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    q1_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    
    form_payload = {
        "title": "Validation Form", 
        "slug": f"val-form-{uuid.uuid4().hex[:6]}", 
        "status": "published", 
        "is_public": True,
        "versions": [{
            "version": "1.0", "sections": [{
                "id": s1_id, 
                "title": "S1",
                "questions": [
                    {"id": q1_id, "label": "Req", "field_type": "input", "is_required": True}
                ]
            }]
        }]
    }
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    form_id = res.get_json()["form_id"]
    
    # Submit empty
    payload = {"data": {s1_id: {q1_id: ""}}}
    res_sub = client.post(f"/form/api/v1/form/{form_id}/responses", json=payload, headers=headers)
    assert res_sub.status_code == 422
