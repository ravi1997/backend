import pytest
from flask_jwt_extended import create_access_token
from app.models.Form import Form, FormVersion, Section, Question, Option
import uuid

def test_multi_language_form(client):
    # 0. Setup: Register and Login to get auth headers
    user_data = {
        "username": "lang_admin",
        "email": "lang_admin@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "1234567890"
    }
    reg_res = client.post("/form/api/v1/auth/register", json=user_data)
    print(f"Reg Response: {reg_res.status_code}, {reg_res.data}")
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "lang_admin@example.com",
        "password": "AdminPassword123"
    })
    print(f"Login Response: {login_res.status_code}, {login_res.data}")
    token = login_res.get_json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a form with translations
    form_id = str(uuid.uuid4())
    section_id = str(uuid.uuid4())
    question_id = str(uuid.uuid4())
    option_id = str(uuid.uuid4())
    
    form_data = {
        "title": "Registration Form",
        "slug": f"lang-test-{uuid.uuid4().hex[:6]}",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": section_id,
                "title": "Personal Info",
                "questions": [{
                    "id": question_id,
                    "label": "Name",
                    "field_type": "input",
                    "options": [{
                        "id": option_id,
                        "option_label": "Male",
                        "option_value": "male"
                    }]
                }]
            }],
            "translations": {
                "hi": {
                    "title": "पंजीकरण फॉर्म",
                    "sections": {
                        section_id: { "title": "व्यक्तिगत जानकारी" }
                    },
                    "questions": {
                        question_id: {
                            "label": "नाम",
                            "options": {
                                option_id: "पुरुष"
                            }
                        }
                    }
                }
            }
        }]
    }
    
    response = client.post("/form/api/v1/form/", json=form_data, headers=auth_headers)
    assert response.status_code == 201
    created_form_id = response.get_json()["form_id"]
    
    # 2. Get form without lang parameter (default English)
    response = client.get(f"/form/api/v1/form/{created_form_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Registration Form"
    assert data["versions"][0]["sections"][0]["title"] == "Personal Info"
    assert data["versions"][0]["sections"][0]["questions"][0]["label"] == "Name"
    assert data["versions"][0]["sections"][0]["questions"][0]["options"][0]["option_label"] == "Male"
    
    # 3. Get form with lang=hi
    response = client.get(f"/form/api/v1/form/{created_form_id}?lang=hi", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "पंजीकरण फॉर्म"
    assert data["versions"][0]["sections"][0]["title"] == "व्यक्तिगत जानकारी"
    assert data["versions"][0]["sections"][0]["questions"][0]["label"] == "नाम"
    assert data["versions"][0]["sections"][0]["questions"][0]["options"][0]["option_label"] == "पुरुष"
    
    # 4. Get form with unsupported lang (should fallback to default)
    response = client.get(f"/form/api/v1/form/{created_form_id}?lang=fr", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Registration Form"

    # 5. Add translations via dedicated endpoint
    new_translations = {
        "title": "Spanish Reg",
        "questions": {
            question_id: {
                "label": "Nombre"
            }
        }
    }
    response = client.post(f"/form/api/v1/form/{created_form_id}/translations", 
                          json={"lang_code": "es", "translations": new_translations}, 
                          headers=auth_headers)
    assert response.status_code == 200
    
    # Verify Spanish fetch
    response = client.get(f"/form/api/v1/form/{created_form_id}?lang=es", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Spanish Reg"
    assert data["versions"][0]["sections"][0]["questions"][0]["label"] == "Nombre"
