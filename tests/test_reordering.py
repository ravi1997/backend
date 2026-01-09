import pytest
import json
from app.models import Form

def get_admin_headers(client):
    payload = {
        "username": "admin_order",
        "email": "admin_order@example.com",
        "password": "AdminPassword123",
        "employee_id": "ORD001",
        "user_type": "employee",
        "mobile": "6655443322",
        "roles": ["admin"]
    }
    # Attempt registration, ignore if exists (might run multiple tests)
    try:
        client.post("/form/api/v1/auth/register", json=payload)
    except:
        pass
        
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "admin_order@example.com", "password": "AdminPassword123"})
    token = login_resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_reorder_sections(client):
    """Test reordering of sections"""
    headers = get_admin_headers(client)
    
    # Create form with 2 sections
    s1_id = "11111111-1111-1111-1111-111111111111"
    s2_id = "22222222-2222-2222-2222-222222222222"
    
    form_data = {
        "title": "Reorder Form",
        "slug": "reorder-form",
        "versions": [{
            "version": "1.0",
            "sections": [
                {"id": s1_id, "title": "Section 1", "questions": []},
                {"id": s2_id, "title": "Section 2", "questions": []}
            ]
        }]
    }
    
    create_resp = client.post("/form/api/v1/form/", json=form_data, headers=headers)
    assert create_resp.status_code == 201, create_resp.data
    form_id = create_resp.get_json()["form_id"]
    
    # Verify initial order
    form = Form.objects.get(id=form_id)
    assert str(form.versions[-1].sections[0].id) == s1_id
    
    # Reorder S2 then S1
    resp = client.patch(
        f"/form/api/v1/form/{form_id}/reorder-sections",
        json={"order": [s2_id, s1_id]},
        headers=headers
    )
    assert resp.status_code == 200, resp.data
    
    # Verify new order
    form.reload()
    assert str(form.versions[-1].sections[0].id) == s2_id
    assert str(form.versions[-1].sections[1].id) == s1_id
    
    # Negative test: mismatch length
    resp = client.patch(
        f"/form/api/v1/form/{form_id}/reorder-sections",
        json={"order": [s1_id]},
        headers=headers
    )
    assert resp.status_code == 400

def test_reorder_questions(client):
    """Test reordering of questions within a section"""
    headers = get_admin_headers(client)
    
    # Create form with 1 section and 3 questions
    s1_id = "33333333-3333-3333-3333-333333333333"
    q1_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    q2_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    q3_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    
    form_data = {
        "title": "Question Reorder Form",
        "slug": "q-reorder-form",
        "versions": [{
            "version": "1.0",
            "sections": [
                {
                    "id": s1_id,
                    "title": "Section 1",
                    "questions": [
                        {"id": q1_id, "label": "Q1", "field_type": "input"},
                        {"id": q2_id, "label": "Q2", "field_type": "input"},
                        {"id": q3_id, "label": "Q3", "field_type": "input"}
                    ]
                }
            ]
        }]
    }
    
    create_resp = client.post("/form/api/v1/form/", json=form_data, headers=headers)
    assert create_resp.status_code == 201, create_resp.data
    form_id = create_resp.get_json()["form_id"]
    
    # Reorder q3, q1, q2
    resp = client.patch(
        f"/form/api/v1/form/{form_id}/section/{s1_id}/reorder-questions",
        json={"order": [q3_id, q1_id, q2_id]},
        headers=headers
    )
    assert resp.status_code == 200, resp.data
    
    # Verify new order
    form = Form.objects.get(id=form_id)
    questions = form.versions[-1].sections[0].questions
    assert str(questions[0].id) == q3_id
    assert str(questions[1].id) == q1_id
    assert str(questions[2].id) == q2_id
    
    # Negative test: Invalid ID
    resp = client.patch(
        f"/form/api/v1/form/{form_id}/section/{s1_id}/reorder-questions",
        json={"order": [q3_id, q1_id, "invalid-uuid"]},
        headers=headers
    )
    assert resp.status_code == 400
