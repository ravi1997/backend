
import pytest
import uuid
import csv
import io
import json
from datetime import datetime, timezone

def get_admin_token(client):
    email = f"export_admin_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"77{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "export_admin", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_csv_export_flattening(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    q1_id = str(uuid.uuid4())
    q2_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    
    form_payload = {
        "title": "Export Form", 
        "slug": f"export-form-{uuid.uuid4().hex[:6]}", 
        "status": "published", 
        "is_public": True,
        "versions": [{
            "version": "1.0", "sections": [{
                "id": s1_id, 
                "title": "Main",
                "questions": [
                    {"id": q1_id, "label": "Full Name", "field_type": "input", "is_required": True},
                    {"id": q2_id, "label": "Age", "field_type": "input", "is_required": True}
                ]
            }]
        }]
    }
    
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    form_id = res.get_json()["form_id"]
    
    # Submit Response
    payload = {
        "data": {
            s1_id: {
                q1_id: "John Doe",
                q2_id: "30"
            }
        }
    }
    client.post(f"/form/api/v1/form/{form_id}/responses", json=payload, headers=headers)
    
    # Export CSV
    res_csv = client.get(f"/form/api/v1/form/{form_id}/export/csv", headers=headers)
    assert res_csv.status_code == 200
    assert res_csv.mimetype == "text/csv"
    
    csv_content = res_csv.data.decode("utf-8")
    lines = csv_content.strip().split("\n")
    
    # Check headers
    header_row = lines[0].split(",")
    # Headers logic: Main - Full Name, Main - Age (assuming prefix due to >1 section check? No, checking length > 1... if only 1 section, no prefix?)
    # "prefix = f"{section.title} - " if len(latest_version.sections) > 1 else """
    # Here only 1 section. So Headers should be ["response_id", "submitted_by", "submitted_at", "status", "Full Name", "Age"]
    
    assert "Full Name" in lines[0]
    assert "Age" in lines[0]
    
    # Check data row
    data_row = lines[1]
    assert "John Doe" in data_row
    assert "30" in data_row

def test_csv_export_repeatable(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    q1_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    
    form_payload = {
        "title": "Export Repeatable", 
        "slug": f"export-rep-{uuid.uuid4().hex[:6]}", 
        "status": "published", 
        "is_public": True,
        "versions": [{
            "version": "1.0", "sections": [{
                "id": s1_id, 
                "title": "Family",
                "is_repeatable_section": True,
                "questions": [
                    {"id": q1_id, "label": "Name", "field_type": "input", "is_required": True}
                ]
            }]
        }]
    }
    
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    form_id = res.get_json()["form_id"]
    
    # Submit Response (Repeatable)
    payload = {
        "data": {
            s1_id: [
                {q1_id: "Alice"},
                {q1_id: "Bob"}
            ]
        }
    }
    client.post(f"/form/api/v1/form/{form_id}/responses", json=payload, headers=headers)
    
    res_csv = client.get(f"/form/api/v1/form/{form_id}/export/csv", headers=headers)
    assert res_csv.status_code == 200
    
    csv_content = res_csv.data.decode("utf-8")
    # Expected: "Alice | Bob" in the column
    assert "Alice | Bob" in csv_content
