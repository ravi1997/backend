
import pytest
import uuid
import json
from app.models.Form import Form, FormResponse, ResponseComment

def get_admin_token(client):
    email = f"comm_admin_{uuid.uuid4().hex[:6]}@test.com"
    mobile = f"77{uuid.uuid4().int % 100000000:08d}"
    client.post("/form/api/v1/auth/register", json={
        "username": "comm_admin", "email": email, "password": "SecurePassword123",
        "employee_id": f"EMP_{uuid.uuid4().hex[:6]}", "user_type": "employee", 
        "roles": ["admin"], "mobile": mobile
    })
    resp = client.post("/form/api/v1/auth/login", json={"email": email, "password": "SecurePassword123"})
    return resp.get_json()["access_token"]

def test_response_comments(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Form
    form_payload = {
        "title": "Comment Form", 
        "slug": f"comm-form-{uuid.uuid4().hex[:6]}", 
        "status": "published", 
        "is_public": True,
        "versions": [{"version": "1.0", "sections": []}]
    }
    res = client.post("/form/api/v1/form/", json=form_payload, headers=headers)
    form_id = res.get_json()["form_id"]
    
    # Submit Response
    res_sub = client.post(f"/form/api/v1/form/{form_id}/responses", json={"data": {}}, headers=headers)
    resp_id = res_sub.get_json()["response_id"]
    
    # 1. Add Comment
    comment_payload = {"content": "This response looks good."}
    res_comm = client.post(f"/form/api/v1/form/{form_id}/responses/{resp_id}/comments", json=comment_payload, headers=headers)
    assert res_comm.status_code == 201
    created_comment = res_comm.get_json()
    assert created_comment["content"] == "This response looks good."
    assert created_comment["user_name"] == "comm_admin"
    
    # 2. Get Comments
    res_list = client.get(f"/form/api/v1/form/{form_id}/responses/{resp_id}/comments", headers=headers)
    assert res_list.status_code == 200
    comments = res_list.get_json()
    assert len(comments) == 1
    assert comments[0]["content"] == "This response looks good."

    # 3. Unauthorized access check (e.g. creating bad comment without View permission?)
    # Reuse token since admin has view permission. 
    # TODO: Could test with new user without permission.
