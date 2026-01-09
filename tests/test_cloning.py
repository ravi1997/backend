
import pytest
import uuid
import json
from app.models.Form import Form

def get_admin_token(client):
    email = f"clone_admin_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"77{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "clone_admin", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_cloning_and_templates(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Original Form
    s1_id = str(uuid.uuid4())
    form_payload = {
        "title": "Original Form", 
        "slug": f"orig-{uuid.uuid4().hex[:6]}", 
        "status": "published", 
        "is_public": True,
        "is_template": True, # Mark as template
        "versions": [{
            "version": "1.0", 
            "sections": [{"id": s1_id, "title": "Section 1", "questions": []}]
        }]
    }
    
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    assert res.status_code == 201
    orig_id = res.get_json()["form_id"]
    
    # 2. Clone it (Override is_template=False for new form)
    clone_payload = {
        "title": "Cloned Form",
        "is_template": False
    }
    res_clone = client.post(f"/form/api/v1/form/{orig_id}/clone", json=clone_payload, headers=headers)
    assert res_clone.status_code == 201
    clone_data = res_clone.get_json()
    new_id = clone_data["form_id"]
    
    assert new_id != orig_id
    
    # 3. Verify Clone State
    res_get = client.get(f"/form/api/v1/form/{new_id}", headers=headers)
    assert res_get.status_code == 200
    new_form = res_get.get_json()
    
    assert new_form["title"] == "Cloned Form"
    assert new_form["status"] == "draft" # Should differ from "published"
    assert new_form["is_public"] == False
    assert new_form["is_template"] == False
    assert len(new_form["versions"]) == 1
    assert new_form["versions"][0]["version"] == "1.0"
    assert new_form["versions"][0]["sections"][0]["title"] == "Section 1" # Structure preserved

    # 4. Test List Filtering
    # We have Orig (Template=True) and Clone (Template=False)
    
    # Get Templates Only
    res_tmpls = client.get("/form/api/v1/form/?is_template=true", headers=headers)
    assert res_tmpls.status_code == 200
    tmpls = res_tmpls.get_json()
    # Check if Orig in list, Clone NOT in list
    assert any(f["id"] == orig_id for f in tmpls)
    assert not any(f["id"] == new_id for f in tmpls)
