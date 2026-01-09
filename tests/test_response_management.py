import pytest
import uuid
import json

def test_response_history_and_comments(client):
    # Setup: Login
    user_data = {
        "username": "resp_admin",
        "email": "resp_admin@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "1112223334"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "resp_admin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a form
    form_id = str(uuid.uuid4())
    section_id = str(uuid.uuid4())
    question_id = str(uuid.uuid4())
    
    client.post("/form/api/v1/form/", json={
        "id": form_id,
        "title": "History Test Form",
        "slug": f"hist-test-{uuid.uuid4().hex[:6]}",
        "status": "published",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": section_id,
                "title": "S1",
                "questions": [{
                    "id": question_id,
                    "label": "Name",
                    "field_type": "input"
                }]
            }]
        }]
    }, headers=headers)

    # 2. Submit Response (History: create)
    submit_res = client.post(f"/form/api/v1/form/{form_id}/responses", 
                            json={"data": {section_id: {question_id: "Initial Name"}}}, 
                            headers=headers)
    assert submit_res.status_code == 201
    response_id = submit_res.get_json()["response_id"]

    # 3. Update Response (History: update)
    client.put(f"/form/api/v1/form/{form_id}/responses/{response_id}", 
              json={"data": {section_id: {question_id: "Updated Name"}}}, 
              headers=headers)

    # 4. Update Status (History: update)
    client.patch(f"/form/api/v1/form/{form_id}/responses/{response_id}/status", 
                json={"status": "approved", "comment": "Good job"}, 
                headers=headers)

    # 5. Delete Response (History: delete)
    client.delete(f"/form/api/v1/form/{form_id}/responses/{response_id}", headers=headers)

    # 6. Restore Response (History: restore)
    client.patch(f"/form/api/v1/form/{form_id}/responses/{response_id}/restore", headers=headers)

    # 7. Check History
    hist_res = client.get(f"/form/api/v1/form/{form_id}/responses/{response_id}/history", headers=headers)
    assert hist_res.status_code == 200
    history = hist_res.get_json()
    
    # We expect 5 entries: restore, delete, update(status), update(data), create
    assert len(history) == 5
    types = [h["change_type"] for h in history]
    assert "create" in types
    assert "update" in types
    assert "delete" in types
    assert "restore" in types
    
    # Latest is restore
    assert history[0]["change_type"] == "restore"

    # 8. Add Comments
    comment_res = client.post(f"/form/api/v1/form/{form_id}/responses/{response_id}/comments", 
                             json={"content": "This is a comment"}, 
                             headers=headers)
    assert comment_res.status_code == 201
    
    # 9. List Comments
    comments_res = client.get(f"/form/api/v1/form/{form_id}/responses/{response_id}/comments", headers=headers)
    assert comments_res.status_code == 200
    comments = comments_res.get_json()
    assert len(comments) == 1
    assert comments[0]["content"] == "This is a comment"
    assert comments[0]["user_name"] == "resp_admin"
