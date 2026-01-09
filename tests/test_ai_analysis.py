import pytest
import uuid

def test_ai_analysis(client):
    # Setup: Login
    user_data = {
        "username": "ai_tester",
        "email": "ai@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "1112223334"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "ai@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a form
    form_id = str(uuid.uuid4())
    s1_id = str(uuid.uuid4())
    q1_id = str(uuid.uuid4())
    
    client.post("/form/api/v1/form/", json={
        "id": form_id,
        "title": "AI Test Form",
        "slug": f"ai-test-{uuid.uuid4().hex[:6]}",
        "status": "published",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id,
                "title": "S1",
                "questions": [{"id": q1_id, "label": "Feedback", "field_type": "textarea"}]
            }]
        }]
    }, headers=headers)

    # 2. Submit Response with text
    # Including an email and positive words
    text_data = "This system is amazing! Contact me at test@example.com or 9998887776."
    res = client.post(f"/form/api/v1/form/{form_id}/responses", 
                      json={"data": {s1_id: {q1_id: text_data}}}, 
                      headers=headers)
    rid = res.get_json()["response_id"]

    # 3. Trigger AI Analysis
    ai_res = client.post(f"/form/api/v1/ai/{form_id}/responses/{rid}/analyze", headers=headers)
    assert ai_res.status_code == 200
    results = ai_res.get_json()["results"]
    
    # 4. Verify Sentiment
    assert results["sentiment"]["label"] == "positive"
    assert results["sentiment"]["score"] > 0
    
    # 5. Verify PII Scan
    assert results["pii_scan"]["found_count"] >= 2
    assert "test@example.com" in results["pii_scan"]["details"]["emails"]
    assert "9998887776" in results["pii_scan"]["details"]["phones"]

    # 6. Verify data stored in response
    get_res = client.get(f"/form/api/v1/form/{form_id}/responses/{rid}", headers=headers)
    resp_data = get_res.get_json()
    assert "ai_results" in resp_data
    assert resp_data["ai_results"]["sentiment"]["label"] == "positive"

    # 7. Verify Bulk Sentiment
    bulk_res = client.get(f"/form/api/v1/ai/{form_id}/sentiment", headers=headers)
    assert bulk_res.status_code == 200
    bulk_data = bulk_res.get_json()
    assert bulk_data["distribution"]["positive"] == 1
    assert bulk_data["average_score"] > 0
