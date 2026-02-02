import pytest
import json
from datetime import datetime
from app.models.Form import Form, FormResponse
from app.models.User import User

@pytest.fixture
def auth_headers(client):
    # Register and Login
    payload = {
        "username": "aiuser",
        "email": "aiuser@example.com",
        "password": "Password123!",
        "employee_id": "EMP_AI_001",
        "user_type": "employee",
        "mobile": "9988776655",
        "roles": ["creator"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    
    login_payload = {
        "email": "aiuser@example.com",
        "password": "Password123!"
    }
    resp = client.post("/form/api/v1/auth/login", json=login_payload)
    token = resp.get_json()["access_token"]
    user_id = User.objects.get(email="aiuser@example.com").id
    return {"Authorization": f"Bearer {token}"}, user_id

def test_cross_analysis_success(client, auth_headers):
    headers, user_id = auth_headers
    
    # Create Form 1
    form1 = Form(
        title="Form 1",
        slug="form-1",
        description="Test Form 1",
        created_by=user_id,
        status="published",
        versions=[{
            "version": "1.0",
            "sections": []
        }]
    ).save()
    
    # Create Form 2
    form2 = Form(
        title="Form 2",
        slug="form-2",
        description="Test Form 2",
        created_by=user_id,
        status="published",
        versions=[{
            "version": "1.0",
            "sections": []
        }]
    ).save()
    
    # Create Responses for Form 1 (2 positive, 1 negative)
    FormResponse(form=form1.id, submitted_by=user_id, data={"q1": "good"}, 
                 ai_results={"sentiment": {"label": "positive", "score": 2}}).save()
    FormResponse(form=form1.id, submitted_by=user_id, data={"q1": "great"}, 
                 ai_results={"sentiment": {"label": "positive", "score": 3}}).save()
    FormResponse(form=form1.id, submitted_by=user_id, data={"q1": "bad"}, 
                 ai_results={"sentiment": {"label": "negative", "score": -2}}).save()
                 
    # Create Responses for Form 2 (1 positive, 1 neutral)
    FormResponse(form=form2.id, submitted_by=user_id, data={"q1": "okay"}, 
                 ai_results={"sentiment": {"label": "neutral", "score": 0}}).save()
    FormResponse(form=form2.id, submitted_by=user_id, data={"q1": "good"}, 
                 ai_results={"sentiment": {"label": "positive", "score": 2}}).save()

    # Call API
    payload = {"form_ids": [str(form1.id), str(form2.id)]}
    response = client.post("/form/api/v1/ai/cross-analysis", json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Check Global Stats
    summary = data["summary"]
    assert summary["total_forms"] == 2
    assert summary["total_responses"] == 5 # 3 + 2
    
    # Avg Score Calculation: 
    # Form 1 Avg: (2 + 3 - 2) / 3 = 1.0
    # Form 2 Avg: (0 + 2) / 2 = 1.0
    # Global Avg: (1.0 + 1.0) / 2 = 1.0
    assert summary["average_sentiment_score"] == 1.0
    
    # Check Details
    details = data["details"]
    assert len(details) == 2
    
    f1_det = next(d for d in details if d["form_id"] == str(form1.id))
    assert f1_det["response_count"] == 3
    assert f1_det["sentiment_distribution"]["positive"] == 2
    assert f1_det["sentiment_distribution"]["negative"] == 1

def test_cross_analysis_unauthorized(client, auth_headers):
    headers, user_id = auth_headers
    
    # Create another user and a form owned by them
    other_user = User(
        username="other", 
        email="other@example.com", 
        roles=["creator"],
        user_type="employee",
        employee_id="OTH001",
        mobile="1111111111"
    )
    other_user.set_password("pass")
    other_user.save()
    
    other_form = Form(
        title="Other Form",
        slug="other-form",
        created_by=other_user.id,
        status="draft", # Not public
        versions=[{"version": "1.0", "sections": []}]
    ).save()
    
    payload = {"form_ids": [str(other_form.id)]}
    response = client.post("/form/api/v1/ai/cross-analysis", json=payload, headers=headers)
    
    assert response.status_code == 403
    assert "Unauthorized" in response.get_json()["error"]

def test_cross_analysis_not_found(client, auth_headers):
    headers, _ = auth_headers
    fake_id = "000000000000000000000000"
    
    payload = {"form_ids": [fake_id]}
    response = client.post("/form/api/v1/ai/cross-analysis", json=payload, headers=headers)
    
    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]
