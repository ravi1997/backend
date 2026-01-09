import pytest
import io
import csv
import zipfile
import uuid
from app.models.Form import Form

def test_bulk_response_export(client):
    # Setup: Login
    user_data = {
        "username": "bulk_admin",
        "email": "bulk_admin@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "9998887770"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "bulk_admin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create 2 forms
    f1_id = str(uuid.uuid4())
    f2_id = str(uuid.uuid4())
    
    for fid, title in [(f1_id, "Form One"), (f2_id, "Form Two")]:
        client.post("/form/api/v1/form/", json={
            "id": fid,
            "title": title,
            "slug": f"slug-{fid[:8]}",
            "status": "published",
            "versions": [{
                "version": "1.0",
                "sections": [{"title": "S1", "questions": [{"label": "Q1", "field_type": "input"}]}]
            }]
        }, headers=headers)
        
        # Submit 1 response each
        client.post(f"/form/api/v1/form/{fid}/responses", json={
            "data": { "section_id_placeholder": {"question_id_placeholder": "answer"} }
        }, headers=headers)

    # 2. Bulk Export
    export_res = client.post("/form/api/v1/form/export/bulk", json={"form_ids": [f1_id, f2_id]}, headers=headers)
    assert export_res.status_code == 200
    assert export_res.mimetype == "application/zip"
    
    # 3. Verify ZIP
    with zipfile.ZipFile(io.BytesIO(export_res.data)) as z:
        file_list = z.namelist()
        print(f"ZIP files: {file_list}")
        assert len(file_list) == 2
        assert any("Form One" in f for f in file_list)
        assert any("Form Two" in f for f in file_list)

def test_bulk_option_import(client):
    # Setup: Login (Need to register again because clean_db is autouse=True)
    user_data = {
        "username": "bulk_admin",
        "email": "bulk_admin@example.com",
        "password": "AdminPassword123",
        "roles": ["admin"],
        "user_type": "employee",
        "mobile": "9998887770"
    }
    client.post("/form/api/v1/auth/register", json=user_data)
    login_res = client.post("/form/api/v1/auth/login", json={
        "email": "bulk_admin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a form with a radio question
    form_id = str(uuid.uuid4())
    section_id = str(uuid.uuid4())
    question_id = str(uuid.uuid4())
    
    client.post("/form/api/v1/form/", json={
        "id": form_id,
        "title": "Option Import Test",
        "slug": f"opt-test-{uuid.uuid4().hex[:6]}",
        "versions": [{
            "version": "1.0",
            "sections": [{
                "id": section_id,
                "title": "Section",
                "questions": [{
                    "id": question_id,
                    "label": "Select Category",
                    "field_type": "radio",
                    "options": []
                }]
            }]
        }]
    }, headers=headers)

    # 2. Prepare CSV
    csv_data = "label,value,description\nRed,red_val,Danger color\nBlue,blue_val,Calm color\nGreen,green_val,Nature color"
    csv_file = (io.BytesIO(csv_data.encode("utf-8")), "options.csv")
    
    # 3. Import Options
    import_url = f"/form/api/v1/form/{form_id}/section/{section_id}/question/{question_id}/options/import"
    res = client.post(import_url, data={"file": csv_file}, headers=headers, content_type="multipart/form-data")
    assert res.status_code == 200
    assert "Imported 3 options" in res.get_json()["message"]
    
    # 4. Verify Fetch
    get_res = client.get(f"/form/api/v1/form/{form_id}", headers=headers)
    form_data = get_res.get_json()
    options = form_data["versions"][0]["sections"][0]["questions"][0]["options"]
    assert len(options) == 3
    assert options[0]["option_label"] == "Red"
    assert options[1]["option_value"] == "blue_val"
    assert options[2]["description"] == "Nature color"

    # 5. Test Replace
    csv_data_2 = "label,value\nPurple,purple_val"
    csv_file_2 = (io.BytesIO(csv_data_2.encode("utf-8")), "options2.csv")
    res = client.post(import_url + "?replace=true", data={"file": csv_file_2}, headers=headers, content_type="multipart/form-data")
    assert res.status_code == 200
    
    get_res = client.get(f"/form/api/v1/form/{form_id}", headers=headers)
    options = get_res.get_json()["versions"][0]["sections"][0]["questions"][0]["options"]
    assert len(options) == 1
    assert options[0]["option_label"] == "Purple"
