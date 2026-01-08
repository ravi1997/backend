import pytest
from unittest.mock import patch

def get_tokens(client):
    client.post("/form/api/v1/auth/register", json={
        "username": "api_user", "email": "api@ex.com", "password": "Pass", 
        "employee_id": "API1", "user_type": "employee", "roles": ["admin"], "mobile": "5544332211"
    })
    admin_token = client.post("/form/api/v1/auth/login", json={"email": "api@ex.com", "password": "Pass"}).get_json()["access_token"]
    return admin_token

def test_handle_uhid_api(client):
    token = get_tokens(client)
    s1_id = "99999999-9999-9999-9999-999999999999"
    q1_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    form_payload = {
        "title": "UHID Form", "slug": "uhid-form", "is_public": True,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id, "title": "S1",
                "questions": [{
                    "id": q1_id, "label": "UHID", "field_type": "input", 
                    "field_api_call": "uhid"
                }]
            }]
        }]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {token}"})
    assert create_resp.status_code == 201
    form_id = create_resp.get_json()["form_id"]
    
    # Mock the send_ehospital_uhid call
    with patch("app.routes.v1.form.api.send_ehospital_uhid") as mock_uhid:
        mock_uhid.return_value = {"name": "Test Patient", "age": 30}
        
        url = f"/form/api/v1/form/{form_id}/section/{s1_id}/question/{q1_id}/api?value=123456"
        response = client.get(url, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.get_json()["data"]["name"] == "Test Patient"

def test_handle_otp_api(client):
    token = get_tokens(client)
    s1_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    q1_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    form_payload = {
        "title": "OTP Form", "slug": "otp-form", "is_public": True,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id, "title": "S1",
                "questions": [{
                    "id": q1_id, "label": "Mobile", "field_type": "input", 
                    "field_api_call": "otp"
                }]
            }]
        }]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {token}"})
    assert create_resp.status_code == 201
    form_id = create_resp.get_json()["form_id"]
    
    with patch("app.routes.v1.form.api.send_OTP_sms") as mock_sms:
        mock_sms.return_value = True
        
        url = f"/form/api/v1/form/{form_id}/section/{s1_id}/question/{q1_id}/api?value=9876543210"
        response = client.get(url, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "otp" in response.get_json()["data"]

def test_handle_form_api(client):
    token = get_tokens(client)
    # Target form to search
    target_form_payload = {
        "title": "Target", "slug": "target", "is_public": True, "status": "published",
        "versions": [{"version": "1.0", "sections": [{"id": "ffffffff-ffff-ffff-ffff-ffffffffffff", "title": "S1", "questions": []}]}]
    }
    target_form_id = client.post("/form/api/v1/form/", json=target_form_payload, headers={"Authorization": f"Bearer {token}"}).get_json()["form_id"]
    
    s1_id = "dddddddd-dddd-dddd-dddd-dddddddddddd"
    q1_id = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
    # Caller form
    form_payload = {
        "title": "Caller Form", "slug": "caller-form", "is_public": True,
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": s1_id, "title": "S1",
                "questions": [{
                    "id": q1_id, "label": "Search", "field_type": "input", 
                    "field_api_call": "form"
                }]
            }]
        }]
    }
    create_resp = client.post("/form/api/v1/form/", json=form_payload, headers={"Authorization": f"Bearer {token}"})
    assert create_resp.status_code == 201
    form_id = create_resp.get_json()["form_id"]
    
    # The 'form' API call expects a JSON string value which is the search payload
    import json
    search_val = json.dumps({"form_id": target_form_id, "data": {}})
    url = f"/form/api/v1/form/{form_id}/section/{s1_id}/question/{q1_id}/api?value={search_val}"
    
    response = client.get(url, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.get_json()
    assert "data" in response.get_json()
