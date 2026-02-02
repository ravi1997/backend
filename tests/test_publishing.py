import pytest
import uuid
from datetime import datetime

def get_admin_token(client):
    email = f"pub_admin_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"66{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "pub_admin", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_publishing_lifecycle(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Draft Form (v1.0)
    s1_id = str(uuid.uuid4())
    form_payload = {
        "title": "Publish Logic Form", 
        "slug": f"pub-logic-{uuid.uuid4().hex[:6]}", 
        "status": "draft",
        "versions": [{
            "version": "1.0", 
            "sections": [{"id": s1_id, "title": "S1", "questions": []}]
        }]
    }
    
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    assert res.status_code == 201
    form_id = res.get_json()["form_id"]
    
    # 2. Publish (Should make v1.0 active/published and create v1.1 draft)
    res = client.post(f"/form/api/v1/form/{form_id}/publish", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    
    assert data["published_version"] == "1.0"
    assert data["next_draft_version"] == "1.1"
    
    # 3. Verify Form State
    res = client.get(f"/form/api/v1/form/{form_id}", headers=headers)
    form_data = res.get_json()
    
    assert form_data["status"] == "published"
    assert form_data["active_version"] == "1.0"
    assert len(form_data["versions"]) == 2
    assert form_data["versions"][-1]["version"] == "1.1" # The new draft
    
    # 4. Attempt Publish again (Should increment to 1.2)
    res = client.post(f"/form/api/v1/form/{form_id}/publish", headers=headers)
    assert res.status_code == 200
    assert res.get_json()["published_version"] == "1.1" # Now 1.1 is published
    assert res.get_json()["next_draft_version"] == "1.2"
