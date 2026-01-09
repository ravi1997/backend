import pytest
import json
from app.models import Form

def get_admin_headers(client):
    payload = {
        "username": "admin_script",
        "email": "admin_script@example.com",
        "password": "AdminPassword123",
        "employee_id": "SCRPT001",
        "user_type": "employee",
        "mobile": "9988776655",
        "roles": ["admin"]
    }
    client.post("/form/api/v1/auth/register", json=payload)
    login_resp = client.post("/form/api/v1/auth/login", json={"email": "admin_script@example.com", "password": "AdminPassword123"})
    token = login_resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_custom_script_success(client):
    """Test successful execution of a custom script with input"""
    admin_headers = get_admin_headers(client)
    
    # 1. Create form with custom script question
    form_data = {
        "title": "Script Form",
        "slug": "script-form",
        "ui": "flex",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "title": "Main",
                "questions": [{
                    "label": "Calc",
                    "field_type": "input",
                    "field_api_call": "custom",
                    "custom_script": "result = input['a'] + input['b']"
                }]
            }]
        }]
    }
    
    resp = client.post("/form/api/v1/form/", json=form_data, headers=admin_headers)
    assert resp.status_code == 201, f"Failed to create form: {resp.data}"
    form_id = resp.get_json()['form_id']
    
    # Reload form to get fresh IDs
    form = Form.objects.get(id=form_id)
    version = form.versions[-1]
    section = version.sections[0]
    question = section.questions[0]
    
    section_id = str(section.id)
    question_id = str(question.id)
    
    # 2. Call API
    payload = json.dumps({"a": 10, "b": 20})
    api_url = f"/form/api/v1/form/{form_id}/section/{section_id}/question/{question_id}/api?value={payload}"
    
    resp = client.get(api_url, headers=admin_headers)
    assert resp.status_code == 200, f"API call failed: {resp.data}"
    assert resp.get_json()["data"] == 30

def test_custom_script_security(client):
    """Test that dangerous imports are blocked"""
    admin_headers = get_admin_headers(client)
    
    # Try to import os
    form_data = {
        "title": "Security Form",
        "slug": "sec-form",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "title": "Main",
                "questions": [{
                    "label": "Hack",
                    "field_type": "input",
                    "field_api_call": "custom",
                    "custom_script": "import os; result = os.listdir('.')"
                }]
            }]
        }]
    }
    resp = client.post("/form/api/v1/form/", json=form_data, headers=admin_headers)
    form_id = resp.get_json()['form_id']
    
    form = Form.objects.get(id=form_id)
    section = form.versions[-1].sections[0]
    question = section.questions[0]
    
    section_id = str(section.id)
    question_id = str(question.id)
    
    api_url = f"/form/api/v1/form/{form_id}/section/{section_id}/question/{question_id}/api"
    resp = client.get(api_url, headers=admin_headers)
    
    # Should fail with 500 (Script execution failed)
    assert resp.status_code == 500
    err_msg = resp.get_json()["error"]
    assert "Script execution failed" in err_msg

def test_custom_script_math_module(client):
    """Test that allowed modules (math) work"""
    admin_headers = get_admin_headers(client)
    
    # Test allowed module
    form_data = {
        "title": "Math Form",
        "slug": "math-form",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "title": "Main",
                "questions": [{
                    "label": "Math",
                    "field_type": "input",
                    "field_api_call": "custom",
                    "custom_script": "result = math.sqrt(input['val'])"
                }]
            }]
        }]
    }
    resp = client.post("/form/api/v1/form/", json=form_data, headers=admin_headers)
    form_id = resp.get_json()['form_id']
    
    form = Form.objects.get(id=form_id)
    section = form.versions[-1].sections[0]
    question = section.questions[0]
    
    section_id = str(section.id)
    question_id = str(question.id)
    
    payload = json.dumps({"val": 16})
    api_url = f"/form/api/v1/form/{form_id}/section/{section_id}/question/{question_id}/api?value={payload}"
    
    resp = client.get(api_url, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.get_json()["data"] == 4.0

def test_custom_script_implicit_return(client):
    """Test returning calculated variables without explicit 'result'"""
    admin_headers = get_admin_headers(client)
    
    form_data = {
        "title": "Implicit Form",
        "slug": "implicit-form",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "title": "Main",
                "questions": [{
                    "label": "Implicit",
                    "field_type": "input",
                    "field_api_call": "custom",
                    "custom_script": "x = 5; y = 10; z = x * y"
                }]
            }]
        }]
    }
    resp = client.post("/form/api/v1/form/", json=form_data, headers=admin_headers)
    form_id = resp.get_json()['form_id']
    
    form = Form.objects.get(id=form_id)
    section = form.versions[-1].sections[0]
    question = section.questions[0]
    
    section_id = str(section.id)
    question_id = str(question.id)
    
    api_url = f"/form/api/v1/form/{form_id}/section/{section_id}/question/{question_id}/api"
    
    resp = client.get(api_url, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    
    # Should contain x, y, z
    assert data["x"] == 5
    assert data["y"] == 10
    assert data["z"] == 50
    # Should NOT contain protected vars like __builtins__
    assert "__builtins__" not in data
