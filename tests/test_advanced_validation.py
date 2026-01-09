
import pytest
import uuid
import time
from datetime import datetime
from app.models.Form import Form, FormResponse

def get_admin_token(client):
    email = f"adv_admin_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"77{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "adv_admin", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_global_custom_validation(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    start_id = str(uuid.uuid4())
    end_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    
    # Python eval uses sanitised keys: v_{uuid_replaced}
    v_start = f"v_{start_id.replace('-', '_')}"
    v_end = f"v_{end_id.replace('-', '_')}"
    
    form_payload = {
        "title": "Cross Validation Form", 
        "slug": f"cross-val-{uuid.uuid4().hex[:6]}", 
        "status": "published", 
        "is_public": True,
        "versions": [{
            "version": "1.0", 
            "custom_validations": [
                {
                    "expression": f"{v_start} < {v_end}",
                    "error_message": "Start must be before End"
                }
            ],
            "sections": [{
                "id": s1_id, 
                "title": "Dates",
                "questions": [
                    {"id": start_id, "label": "Start", "field_type": "input", "is_required": True},
                    {"id": end_id, "label": "End", "field_type": "input", "is_required": True}
                ]
            }]
        }]
    }
    
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    assert res.status_code == 201
    form_id = res.get_json()["form_id"]
    
    # 1. Valid Submission (Start < End)
    # ISO strings compare correctly
    payload_valid = {
        "data": {
            s1_id: {
                start_id: "2023-01-01",
                end_id: "2023-01-02"
            }
        }
    }
    res_val = client.post(f"/form/api/v1/form/{form_id}/responses", json=payload_valid, headers=headers)
    assert res_val.status_code == 201
    
    # 2. Invalid Submission (Start > End)
    payload_invalid = {
        "data": {
            s1_id: {
                start_id: "2023-02-01",
                end_id: "2023-01-01"
            }
        }
    }
    res_inv = client.post(f"/form/api/v1/form/{form_id}/responses", json=payload_invalid, headers=headers)
    assert res_inv.status_code == 422
    errs = res_inv.get_json()["details"]
    # Check for global error
    assert any(e.get("global") and "Start must be before End" in e.get("error") for e in errs)

