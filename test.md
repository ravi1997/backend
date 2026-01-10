# Test Documentation and Mapping

This document maps the project features (as defined in `SRS.md` and `PROJECT_STATUS.md`) to their corresponding test files in the `tests/` directory.

## 1. Authentication Module

| Feature ID | Feature Name | Test File | Test Type |
| ------------ | ------------ | ----------- | ----------- |
| FR-AUTH-001 | User Registration | `tests/test_auth.py` | Integration |
| FR-AUTH-002 | Employee Login | `tests/test_auth.py` | Integration |
| FR-AUTH-003 | OTP Login | `tests/test_auth.py` | Integration |
| FR-AUTH-004 | OTP Generation | `tests/test_api.py` | Integration |
| FR-AUTH-005 | Logout | `tests/test_auth.py` | Integration |

## 2. User Management Module

| Feature ID | Feature Name | Test File | Test Type |
| ------------ | ------------ | ----------- | ----------- |
| FR-USER-001 | List All Users | `tests/test_user.py` | Integration |
| FR-USER-002 | Get User Details | `tests/test_user.py` | Integration |
| FR-USER-003 | Create User | `tests/test_user.py` | Integration |
| FR-USER-004 | Update User | `tests/test_user.py` | Integration |
| FR-USER-005 | Delete User | `tests/test_user.py` | Integration |
| FR-USER-006 | Lock User Account | `tests/test_user.py` | Integration |
| FR-USER-007 | Unlock User Account | `tests/test_user.py` | Integration |
| FR-USER-008 | Change Password | `tests/test_user.py` | Integration |
| FR-USER-009 | Reset Password | `tests/test_auth.py` | Integration |
| FR-USER-010 | Extend Password Expiry | `tests/test_auth.py` | Integration |

## 3. Form Management Module

| Feature ID | Feature Name | Test File | Test Type |
| ------------ | ------------ | ----------- | ----------- |
| FR-FORM-001 | Create Form | `tests/test_form.py` | Integration |
| FR-FORM-002 | List Forms | `tests/test_form.py` | Integration |
| FR-FORM-003 | Get Form Details | `tests/test_form.py` | Integration |
| FR-FORM-004 | Update Form | `tests/test_form.py` | Integration |
| FR-FORM-005 | Delete Form | `tests/test_form.py` | Integration |
| FR-FORM-006 | Publish Form | `tests/test_form.py` | Integration |
| FR-FORM-007 | Clone Form | `tests/test_cloning.py` | Integration |
| FR-FORM-008 | Share Form | `tests/test_form.py` | Integration |
| FR-FORM-009 | Archive Form | `tests/test_misc.py` | Integration |
| FR-FORM-010 | Restore Form | `tests/test_misc.py` | Integration |
| FR-FORM-011 | Toggle Public Access | `tests/test_misc.py` | Integration |
| FR-FORM-012 | Check Slug Availability | `tests/test_form.py` | Integration |
| FR-FORM-013 | Set Form Expiration | `tests/test_misc.py` | Integration |
| FR-FORM-014 | List Expired Forms | `tests/test_misc.py` | Integration |

## 4. Form Response Module

| Feature ID | Feature Name | Test File | Test Type |
| ------------ | ------------ | ----------- | ----------- |
| FR-RESP-001 | Submit Response | `tests/test_responses.py` | Integration |
| FR-RESP-002 | Public Submit Response | `tests/test_responses.py` | Integration |
| FR-RESP-003 | List Responses | `tests/test_responses.py` | Integration |
| FR-RESP-004 | Get Single Response | `tests/test_responses.py` | Integration |
| FR-RESP-005 | Update Response | `tests/test_responses.py` | Integration |
| FR-RESP-006 | Delete Response | `tests/test_responses.py` | Integration |
| FR-RESP-007 | Paginated Responses | `tests/test_responses.py` | Integration |
| FR-RESP-008 | Archive Response | `tests/test_responses.py` | Integration |
| FR-RESP-009 | Search Responses | `tests/test_responses.py` | Integration |
| FR-RESP-010 | Delete All Responses | `tests/test_responses.py` | Integration |
| FR-RESP-011 | Count Responses | `tests/test_analytics.py` | Integration |
| FR-RESP-012 | Get Last Response | `tests/test_analytics.py` | Integration |
| FR-RESP-013 | Check Duplicate Submission | `tests/test_responses.py` | Integration |
| FR-RESP-014 | Response Drafts / Auto-save | `tests/test_response_drafts.py` | Integration |

## 5. Export Module

| Feature ID | Feature Name | Test File | Test Type |
| ------------ | ------------ | ----------- | ----------- |
| FR-EXPORT-001 | Export Responses to CSV | `tests/test_export.py` | Unit/Integration |
| FR-EXPORT-002 | Export Form to JSON | `tests/test_export.py` | Unit/Integration |

## 6. File Management Module

| Feature ID | Feature Name | Test File | Test Type |
| ------------ | ------------ | ----------- | ----------- |
| FR-FILE-001 | Upload File | `tests/test_responses.py` | Integration |
| FR-FILE-002 | Retrieve Uploaded File | `tests/test_responses.py` | Integration |

## 7. Analytics Module

| Feature ID | Feature Name | Test File | Test Type |
| ------------ | ------------ | ----------- | ----------- |
| FR-ANALYTICS-001 | Form Analytics | `tests/test_analytics.py` | Integration |
| FR-ANALYTICS-002 | Submission History | `tests/test_analytics.py` | Integration |

## 8. API Integration & Advanced Features

| Feature ID | Feature Name | Test File | Test Type |
| ------------ | ------------ | ----------- | ----------- |
| FR-API-001 | UHID Lookup | `tests/test_api.py` | Integration |
| FR-API-002 | OTP SMS | `tests/test_api.py` | Integration |
| FR-API-003 | Cross-Form Lookup | `tests/test_api.py` | Integration |
| FR-API-004 | Custom Script | `tests/test_custom_scripts.py` | Integration |
| FR-COND-001 | Conditional Validation | `tests/test_conditional_validation.py` | Unit |
| FR-HIST-001 | Response Edit History | `tests/test_advanced_features.py` | Integration |
| FR-HOOK-001 | Webhook Integration | `tests/test_advanced_features.py` | Integration |
| FR-EMAIL-001 | Email Notifications | `tests/test_email_notifications.py` | Integration |
| FR-STAT-001 | Response Status Workflow | `tests/test_response_status.py` | Flow |
| FR-SCHED-001 | Scheduled Publishing | `tests/test_scheduled_publishing.py` | Integration |
| FR-DASH-001 | Dashboards | `tests/test_dashboard.py` | Integration |
| FR-WORK-001 | Workflow Configuration | `tests/test_workflow.py` | Integration |
| FR-AI-001 | AI Generation | `tests/test_ai_generation.py` | Integration |
| FR-AI-002 | AI Moderation | `tests/test_ai_moderation.py` | Integration |
| FR-AI-003 | AI Search | `tests/test_ai_search.py` | Integration |
| FR-AI-004 | AI Security Scan | `tests/test_ai_security_scan.py` | Integration |
| FR-AI-005 | AI Templates | `tests/test_ai_templates.py` | Integration |
| FR-AI-006 | AI Analysis | `tests/test_ai_analysis.py` | Integration |
| FR-AI-007 | AI Anomalies | `tests/test_ai_anomalies.py` | Integration |

## Test Strategy Overview

The test suite is built using `pytest` and `flask.testing`.

- **Unit Tests**: Focus on specific functions (e.g., validation logic) without database interaction.
- **Integration Tests**: Focus on API endpoints, interacting with a test MongoDB database.
- **Flow Tests**: Simulate a user journey involving multiple steps (Login → Create Form → Submit → View → Export).

---

### `tests/test_auth.py`

- **Description**: Verifies the full authentication lifecycle – registration, duplicate‑email handling, login (valid & invalid), OTP generation, and logout.
- **Need**: Guarantees that only authorised users can access the system and that security‑critical flows behave correctly.
- **Inputs**:
  - **Registration payload** (JSON schema):

    ```json
    {
      "username": "string",
      "email": "string",
      "password": "string",
      "employee_id": "string",
      "user_type": "string",
      "mobile": "string",
      "roles": ["string"]
    }
    ```

    *Explanation of each field*:
    - `username`: Human‑readable identifier for the user; must be unique within the organisation.
    - `email`: Primary contact address; used for login and OTP delivery; must be unique.
    - `password`: Plain‑text password; the API hashes it before storage.
    - `employee_id`: Internal employee identifier; optional but useful for audit trails.
    - `user_type`: Role category (e.g., `employee`, `admin`). Determines default permissions.
    - `mobile`: Mobile phone number for OTP SMS delivery.
    - `roles`: List of role strings (e.g., `"admin"`, `"user"`). Allows fine‑grained RBAC.
  - **Login payload**:

    ```json
    {"email": "string", "password": "string"}
    ```

    - `email`: Must match a registered user.
    - `password`: Plain‑text password; validated against stored hash.
  - **OTP request payload**:

    ```json
    {"mobile": "string"}
    ```

    - `mobile`: The phone number to which the OTP will be sent; must belong to a registered user.
- **Output schema (successful cases)**:
  - Registration: `{"message": "User registered"}` with HTTP **201**.
  - Login: `{"access_token": "<jwt>"}` with HTTP **200**.
  - OTP generation: `{"message": "OTP sent successfully"}` with HTTP **200**.
  - Logout: `{"message": "Successfully logged out"}` with HTTP **200**.
  - *Field explanations*:
    - `message`: Human‑readable status text.
    - `access_token`: JSON Web Token string that must be sent in `Authorization: Bearer <token>` header for protected endpoints.
- **Error results & possible causes**:
  - **409 Conflict** on registration – email already exists. *Cause*: duplicate email in DB. *Fix*: use a unique email (e.g., include a UUID) or clean the test DB before the run.
  - **401 Unauthorized** on login – invalid credentials. *Cause*: wrong password or email. *Fix*: ensure the payload matches a user created earlier in the test.
  - **400 Bad Request** on OTP – missing or malformed mobile number. *Fix*: provide a non‑empty string that matches the registered user's mobile.
- **Examples (Python with Flask test client)**:

  ```python
  # 1. Register a new user
  reg_payload = {
      "username": "alice",
      "email": "alice@example.com",
      "password": "Secret123!",
      "employee_id": "EMP001",
      "user_type": "employee",
      "mobile": "1234567890",
      "roles": ["admin"]
  }
  resp = client.post('/form/api/v1/auth/register', json=reg_payload)
  assert resp.status_code == 201

  # 2. Login with the newly created user
  login_payload = {"email": "alice@example.com", "password": "Secret123!"}
  resp = client.post('/form/api/v1/auth/login', json=login_payload)
  assert resp.status_code == 200
  token = resp.get_json()['access_token']

  # 3. Request OTP for the user's mobile
  resp = client.post('/form/api/v1/auth/generate-otp', json={"mobile": "1234567890"})
  assert resp.status_code == 200

  # 4. Logout using the token
  resp = client.post('/form/api/v1/auth/logout', headers={"Authorization": f"Bearer {token}"})
  assert resp.status_code == 200
  ```

  *Explanation*: Each step mirrors a real client interaction. The payloads follow the schemas above, and the assertions verify both HTTP status and response content.

---

### `tests/test_user.py`

- **Description**: Exercises CRUD operations for user management – list, retrieve, create, update, delete, lock/unlock, password changes.
- **Inputs**:
  - **Create/Update payload** (JSON schema):

    ```json
    {
      "username": "string",
      "email": "string",
      "roles": ["string"],
      "is_locked": false,
      "password": "string"   // only required on create
    }
    ```

    *Field details*:
    - `username`: Desired login name; must be unique.
    - `email`: Contact address; unique constraint.
    - `roles`: Array of role identifiers; controls permissions.
    - `is_locked`: Boolean flag; true prevents login.
    - `password`: Plain password; only needed when creating a user (hashed on server).
  - **Password change payload**:

    ```json
    {"current_password": "string", "new_password": "string"}
    ```

    - `current_password`: Must match stored hash; prevents unauthorized changes.
    - `new_password`: New password that will be hashed and stored.
- **Output schema**:
  - List: `{"users": [{...}], "total": int}` with **200**.
  - Get: single user object with **200** or **404** if not found.
  - Create: created user object with **201**.
  - Update: updated user object with **200**.
  - Delete: empty body with **204**.
  - Lock/Unlock: `{"message": "User locked"}` or `{"message": "User unlocked"}` with **200**.
- **Error results**:
  - **400** – validation error (e.g., missing required fields, invalid email format).
  - **404** – user ID does not exist.
  - **409** – email already in use when creating.
- **Fixes**:
  - Use a fresh, unique email for each test (e.g., `f"user_{uuid4()}@example.com"`).
  - Validate payload locally before sending to reduce 400 errors.
  - Clean up created users after the test suite (fixture `teardown`).
- **Example (Python)**:

  ```python
  # Create a new user
  payload = {
      "username": "bob",
      "email": "bob@example.com",
      "roles": ["user"],
      "password": "StrongPass!"
  }
  resp = client.post('/form/api/v1/users', json=payload)
  assert resp.status_code == 201
  user_id = resp.get_json()['id']

  # Update the user (e.g., add a role)
  update_payload = {"roles": ["user", "editor"]}
  resp = client.put(f'/form/api/v1/users/{user_id}', json=update_payload)
  assert resp.status_code == 200

  # Lock the user account
  resp = client.post(f'/form/api/v1/users/{user_id}/lock')
  assert resp.status_code == 200
  assert resp.get_json()['message'] == 'User locked'

  # Change password
  pwd_payload = {"current_password": "StrongPass!", "new_password": "NewPass123"}
  resp = client.post(f'/form/api/v1/users/{user_id}/change-password', json=pwd_payload)
  assert resp.status_code == 200
  ```

---

### `tests/test_form.py`

- **Description**: Validates form CRUD operations, publishing, sharing, slug checking, and expiration handling.
- **Inputs**:
  - **Form definition schema**:

    ```json
    {
      "title": "string",
      "description": "string",
      "fields": [
        {"name": "string", "type": "string", "required": true}
      ],
      "settings": {
        "is_public": false,
        "is_published": false
      }
    }
    ```

    *Field breakdown*:
    - `title`: Human‑readable name shown to respondents.
    - `description`: Optional longer text explaining the form.
    - `fields`: Array of field definitions; each field must contain:
      - `name`: Identifier used in response payloads.
      - `type`: Data type (`string`, `number`, `date`, etc.).
      - `required`: Boolean indicating if the field must be present.
    - `settings`:
      - `is_public`: If true, the form can be accessed without authentication.
      - `is_published`: If true, the form is live and can accept submissions.
  - **Publish payload**: No body required; the endpoint simply toggles `is_published` to true.
  - **Share payload**:

    ```json
    {"recipients": ["email1@example.com", "email2@example.com"]}
    ```

    - `recipients`: List of email addresses that will receive a shareable link.
  - **Slug check query**: `GET /form/api/v1/forms/slug-available?slug=my-form`
    - `slug`: URL‑friendly string; must be unique across all forms.
  - **Expiration payload**:

    ```json
    {"expire_at": "2026-12-31T23:59:59Z"}
    ```

    - `expire_at`: ISO‑8601 timestamp after which the form becomes invisible.
- **Output schema**:
  - Create: `{"id": "<uuid>", "title": "..."}` with **201**.
  - Get/List: full form object(s) with **200**.
  - Update: updated form object with **200**.
  - Delete: empty body **204**.
  - Publish: `{"message": "Form published"}` **200**.
  - Share: `{"share_link": "https://..."}` **200**.
  - Slug check: `{"available": true}` **200**.
  - Expiration: `{"message": "Expiration set"}` **200**.
- **Error cases**:
  - **400** – missing required fields (`title`, `fields`), invalid field types, malformed ISO dates.
  - **404** – form ID not found.
  - **409** – slug already taken (duplicate).
- **Fixes**:
  - Validate the JSON against the schema locally (e.g., using `jsonschema` library) before sending.
  - Generate a unique slug per test, perhaps by appending a timestamp or UUID.
  - Ensure the form is successfully created before attempting publish, share, or expiration actions.
- **Example (Python)**:

  ```python
  # 1. Create a form
  form_payload = {
      "title": "Customer Feedback",
      "description": "Gather feedback after purchase",
      "fields": [
          {"name": "rating", "type": "number", "required": True},
          {"name": "comments", "type": "string", "required": False}
      ],
      "settings": {"is_public": False, "is_published": False}
  }
  resp = client.post('/form/api/v1/forms', json=form_payload)
  assert resp.status_code == 201
  form_id = resp.get_json()['id']

  # 2. Publish the form
  resp = client.post(f'/form/api/v1/forms/{form_id}/publish')
  assert resp.status_code == 200
  assert resp.get_json()['message'] == 'Form published'

  # 3. Check slug availability (use a unique slug)
  slug = f"feedback-{uuid4().hex[:6]}"
  resp = client.get(f'/form/api/v1/forms/slug-available?slug={slug}')
  assert resp.status_code == 200
  assert resp.get_json()['available'] is True

  # 4. Set expiration date
  resp = client.post(f'/form/api/v1/forms/{form_id}/set-expiration', json={"expire_at": "2026-12-31T23:59:59Z"})
  assert resp.status_code == 200
  ```

---

### `tests/test_cloning.py`

- **Description**: Tests cloning of a form, preserving structure and settings.
- **Inputs**:
  - **Clone payload** (optional overrides):

    ```json
    {"title": "Cloned Form"}
    ```

    - `title`: New title for the cloned form; if omitted, the original title is kept.
- **Outputs**:
  - **201** with cloned form JSON containing a new `id` and an identical `fields` array.
- **Error cases**:
  - **404** if the source form does not exist.
  - **403** if the authenticated user lacks cloning permission.
- **Fixes**:
  - Create the source form in a preceding step and capture its `id`.
  - Use a token belonging to a user with the `clone_form` role.
- **Example (Python)**:

  ```python
  # Create source form
  src_resp = client.post('/form/api/v1/forms', json=form_payload)
  src_id = src_resp.get_json()['id']

  # Clone the form with a new title
  clone_resp = client.post(f'/form/api/v1/forms/{src_id}/clone', json={"title": "My Clone"})
  assert clone_resp.status_code == 201
  clone_data = clone_resp.get_json()
  assert clone_data['id'] != src_id
  assert clone_data['fields'] == src_resp.get_json()['fields']
  ```

---

### `tests/test_responses.py`

- **Description**: Covers the full response lifecycle – submit, retrieve, update, delete, pagination, archive, search, duplicate detection, draft auto‑save.
- **Inputs**:
  - **Response payload schema** (must match the form's field definitions):

    ```json
    {
      "answers": {"field_name": "value", "another_field": 123},
      "metadata": {"submitted_at": "2026-01-01T12:00:00Z"}
    }
    ```

    - `answers`: Object where each key corresponds to a field `name` defined in the form; the value must respect the field's `type`.
    - `metadata`: Optional auxiliary information; `submitted_at` is an ISO‑8601 timestamp.
- **Outputs**:
  - Submit: `{"response_id": "<uuid>", "status": "submitted"}` **201**.
  - Get single response: full response object **200**.
  - Update: updated response object **200**.
  - Delete: empty body **204**.
  - Archive: `{"message": "Archived"}` **202**.
  - Search: `{"results": [{...}]}` **200**.
  - Draft save: `{"draft_id": "<uuid>"}` **200**.
- **Error cases**:
  - **400** – validation failure (e.g., missing required answer, wrong type).
  - **404** – form or response not found.
  - **409** – duplicate submission detected (same answers submitted twice).
- **Fixes**:
  - Ensure the payload's `answers` keys exactly match the form's field names.
  - Convert numbers, dates, booleans to the correct JSON types before sending.
  - For duplicate‑submission tests, deliberately resend the same payload and assert the **409** response.
- **Example (Python)**:

  ```python
  # Assume a form with fields "rating" (number) and "comment" (string) exists
  response_payload = {
      "answers": {"rating": 5, "comment": "Great!"},
      "metadata": {"submitted_at": "2026-01-10T10:00:00Z"}
  }
  # Submit response
  resp = client.post(f'/form/api/v1/forms/{form_id}/responses', json=response_payload)
  assert resp.status_code == 201
  resp_id = resp.get_json()['response_id']

  # Retrieve the same response
  resp = client.get(f'/form/api/v1/responses/{resp_id}')
  assert resp.status_code == 200
  data = resp.get_json()
  assert data['answers']['rating'] == 5

  # Update the comment field
  update_payload = {"answers": {"comment": "Excellent service"}}
  resp = client.put(f'/form/api/v1/responses/{resp_id}', json=update_payload)
  assert resp.status_code == 200
  assert resp.get_json()['answers']['comment'] == "Excellent service"
  ```

---

### `tests/test_export.py`

- **Description**: Validates export of responses (CSV) and forms (JSON).
- **Inputs**: Query parameters `format=csv|json`, optional `start_date`, `end_date` (ISO‑8601).
- **Outputs**:
  - **200** with `Content-Type: text/csv` (for CSV) or `application/json` (for JSON).
  - CSV body includes a header row matching the form's field names followed by rows of response data.
  - JSON body contains an array of response objects mirroring the form schema.
- **Error cases**:
  - **400** – unsupported format value or invalid date range (e.g., `start_date` after `end_date`).
  - **404** – form ID does not exist.
- **Fixes**:
  - Pass a valid `format` (`csv` or `json`).
  - Ensure dates are correctly formatted (`YYYY‑MM‑DDTHH:MM:SSZ`).
  - Verify that the form has at least one response before exporting.
- **Example (Python)**:

  ```python
  # Export responses as CSV for the last month
  resp = client.get(f'/form/api/v1/forms/{form_id}/export/csv?start_date=2026-01-01&end_date=2026-01-31')
  assert resp.status_code == 200
  assert resp.headers['Content-Type'] == 'text/csv'
  csv_content = resp.data.decode('utf-8')
  # First line should be the header
  header = csv_content.split('\n')[0]
  assert 'rating' in header and 'comment' in header

  # Export the form definition as JSON
  resp = client.get(f'/form/api/v1/forms/{form_id}/export/json')
  assert resp.status_code == 200
  assert resp.headers['Content-Type'] == 'application/json'
  form_json = resp.get_json()
  assert form_json['title'] == 'Customer Feedback'
  ```

---

### `tests/test_api.py`

- **Description**: Tests auxiliary utilities – UHID lookup, OTP SMS, cross‑form lookup, custom script execution.
- **Inputs**:
  - **UHID lookup** payload:

    ```json
    {"uhid": "U12345"}
    ```

    - `uhid`: Unique Health Identifier string.
  - **OTP SMS** payload:

    ```json
    {"mobile": "1234567890"}
    ```

    - `mobile`: Phone number to receive OTP.
  - **Cross‑form lookup** payload:

    ```json
    {"source_form_id": "<uuid>", "target_form_id": "<uuid>"}
    ```

    - `source_form_id`: Form from which data is taken.
    - `target_form_id`: Form to which data is mapped.
  - **Custom script execution** payload:

    ```json
    {"script_id": "<uuid>", "input": {"key": "value"}}
    ```

    - `script_id`: Identifier of an uploaded script.
    - `input`: Arbitrary JSON that will be passed to the script.
- **Outputs**:
  - All utilities return **200** with a JSON body specific to the service (e.g., lookup result, OTP status, script output).
  - Errors: **400** for malformed payload, **404** if the referenced entity does not exist.
- **Fixes**:
  - Ensure IDs (`uhid`, `script_id`, form IDs) are generated in prior test steps.
  - Mock external services (SMS gateway, UHID registry) so the tests remain deterministic.
- **Example (Python)**:

  ```python
  # UHID lookup
  resp = client.post('/form/api/v1/uhid/lookup', json={"uhid": "U12345"})
  assert resp.status_code == 200
  assert 'patient_name' in resp.get_json()

  # OTP SMS
  resp = client.post('/form/api/v1/otp/sms', json={"mobile": "9876543210"})
  assert resp.status_code == 200
  assert resp.get_json()['status'] == 'sent'

  # Custom script execution (assuming script already uploaded)
  resp = client.post(f'/form/api/v1/scripts/{script_id}/execute', json={"input": {"x": 10}})
  assert resp.status_code == 200
  assert resp.get_json()['result']['x'] == 10
  ```

---

### `tests/test_custom_scripts.py`

- **Description**: Ensures user‑provided scripts can be uploaded and executed safely.
- **Inputs**:
  - **Upload**: multipart/form‑data with a file field named `script`.
  - **Execute** payload:

    ```json
    {"script_id": "<uuid>", "input": {"value": 42}}
    ```

- **Outputs**:
  - Upload **201** with `{"script_id": "<uuid>"}`.
  - Execute **200** with `{"result": {...}}` where `result` is whatever the script returns.
- **Error cases**:
  - **400** – missing file or malformed JSON.
  - **403** – script attempts disallowed operations (e.g., file system access, network calls).
- **Fixes**:
  - Keep scripts small and pure‑Python; avoid imports that are not whitelisted.
  - In tests, use `unittest.mock` to replace the sandbox runner and assert that a `PermissionError` is raised for prohibited actions.
- **Example (Python)**:

  ```python
  # Upload a simple script that adds two numbers
  script_content = b"def run(data): return {'sum': data['a'] + data['b']}"
  files = {'script': ('add.py', script_content, 'text/x-python')}
  resp = client.post('/form/api/v1/scripts/upload', data=files, content_type='multipart/form-data')
  assert resp.status_code == 201
  script_id = resp.get_json()['script_id']

  # Execute the uploaded script
  exec_payload = {"script_id": script_id, "input": {"a": 5, "b": 7}}
  resp = client.post(f'/form/api/v1/scripts/{script_id}/execute', json=exec_payload)
  assert resp.status_code == 200
  assert resp.get_json()['result']['sum'] == 12
  ```

---

### `tests/test_conditional_validation.py`

- **Description**: Validates conditional field requirements based on other field values.
- **Inputs**:
  - **Form schema** includes a `conditional_rules` array, e.g.:

    ```json
    [{"if": {"field": "type", "equals": "special"}, "then": {"required": ["extra_info"]}}]
    ```

    - `if.field`: The field whose value triggers the rule.
    - `if.equals`: The value that activates the condition.
    - `then.required`: List of additional fields that become mandatory when the condition is true.
  - **Response payloads**:
    - *Passing*: `{"type": "special", "extra_info": "details"}`.
    - *Failing*: `{"type": "special"}` (missing `extra_info`).
- **Outputs**:
  - **201** for passing payload.
  - **400** with an error message such as `"Field 'extra_info' is required when 'type' == 'special'"`.
- **Fixes**:
  - When constructing a response, check the conditional rules defined in the form and include any required dependent fields.
- **Example (Python)**:

  ```python
  # Create a form with a conditional rule
  form_payload = {
      "title": "Conditional Form",
      "fields": [
          {"name": "type", "type": "string", "required": True},
          {"name": "extra_info", "type": "string", "required": False}
      ],
      "conditional_rules": [
          {"if": {"field": "type", "equals": "special"}, "then": {"required": ["extra_info"]}}
      ]
  }
  resp = client.post('/form/api/v1/forms', json=form_payload)
  form_id = resp.get_json()['id']

  # Passing response (includes extra_info)
  passing = {"type": "special", "extra_info": "needed"}
  resp = client.post(f'/form/api/v1/forms/{form_id}/responses', json=passing)
  assert resp.status_code == 201

  # Failing response (missing extra_info)
  failing = {"type": "special"}
  resp = client.post(f'/form/api/v1/forms/{form_id}/responses', json=failing)
  assert resp.status_code == 400
  assert "extra_info" in resp.get_json()['error']
  ```

---

### `tests/test_advanced_features.py`

- **Description**: Tests response edit history and webhook callbacks.
- **Inputs**:
  - **History request**: `GET /form/api/v1/responses/<id>/history` (no body).
  - **Webhook trigger payload**:

    ```json
    {"event": "response_updated", "payload": {"response_id": "<uuid>", "changes": {"field": "new value"}}}
    ```

    - `event`: Name of the event that should fire a webhook.
    - `payload`: Data sent to the external webhook endpoint.
- **Outputs**:
  - History **200** with `{"history": [{"changed_at": "...", "diff": {...}}]}`.
  - Webhook **202** with `{"status": "queued"}`.
- **Error cases**:
  - **404** if the response ID does not exist.
  - **400** if the webhook payload is malformed.
- **Fixes**:
  - Ensure the response exists before requesting its history.
  - Mock the external webhook endpoint (e.g., using `responses` library) so the test does not perform real network calls.
- **Example (Python)**:

  ```python
  # Assume a response has been created and its ID is resp_id
  # Update the response to generate a history entry
  client.put(f'/form/api/v1/responses/{resp_id}', json={"answers": {"rating": 4}})

  # Retrieve edit history
  hist = client.get(f'/form/api/v1/responses/{resp_id}/history')
  assert hist.status_code == 200
  history = hist.get_json()['history']
  assert any(entry['diff']['rating'] == 4 for entry in history)

  # Trigger a webhook (mocked)
  webhook_payload = {"event": "response_updated", "payload": {"response_id": resp_id, "changes": {"rating": 4}}}
  resp = client.post('/form/api/v1/webhooks/trigger', json=webhook_payload)
  assert resp.status_code == 202
  assert resp.get_json()['status'] == 'queued'
  ```

---

### `tests/test_email_notifications.py`

- **Description**: Verifies email notifications on key events.
- **Inputs**: Triggered indirectly by actions such as form submission; the test patches the email service.
- **Outputs**: The test asserts that the mocked email sender was called with correct arguments (recipient, subject, body).
- **Error cases**: If the mock is not set up, the test will raise an `AssertionError`.
- **Fixes**: Use `unittest.mock.patch` to replace the email sending function with a mock and assert `mock_send.called`.
- **Example (Python)**:

  ```python
  from unittest.mock import patch

  with patch('app.email.send_email') as mock_send:
      # Submit a response that should trigger an email
      client.post(f'/form/api/v1/forms/{form_id}/responses', json=response_payload)
      # Verify the email service was invoked
      assert mock_send.called
      args, kwargs = mock_send.call_args
      assert kwargs['to'] == 'admin@example.com'
      assert 'New response submitted' in kwargs['subject']
  ```

---

### `tests/test_response_status.py`

- **Description**: Tests workflow moving a response through statuses.
- **Inputs**: Payload with a `status` field, e.g. `{"status": "reviewed"}`.
- **Outputs**: **200** with the updated response object; **400** on illegal transition.
- **Fixes**: Follow the defined state‑machine order (`submitted` → `reviewed` → `approved` → `rejected`). Attempting to jump from `submitted` directly to `approved` will produce a **400**.
- **Example (Python)**:

  ```python
  # Valid transition
  resp = client.post(f'/form/api/v1/responses/{resp_id}/status', json={"status": "reviewed"})
  assert resp.status_code == 200
  assert resp.get_json()['status'] == 'reviewed'

  # Invalid transition (skip 'reviewed')
  resp = client.post(f'/form/api/v1/responses/{resp_id}/status', json={"status": "approved"})
  assert resp.status_code == 400
  ```

---

### `tests/test_scheduled_publishing.py`

- **Description**: Checks that forms can be scheduled to become public at a future datetime.
- **Inputs**: Payload with `publish_at` ISO‑8601 timestamp, e.g. `{"publish_at": "2026-02-01T00:00:00Z"}`.
- **Outputs**: **202** on schedule creation; after the scheduled time, a **GET** on the form returns `"is_public": true`.
- **Fixes**: In tests, mock the scheduler or fast‑forward time (e.g., using `freezegun`) so the scheduled job runs instantly.
- **Example (Python)**:

  ```python
  from freezegun import freeze_time

  # Schedule publishing
  schedule_payload = {"publish_at": "2026-02-01T00:00:00Z"}
  resp = client.post(f'/form/api/v1/forms/{form_id}/schedule-publish', json=schedule_payload)
  assert resp.status_code == 202

  # Fast‑forward time to after the schedule
  with freeze_time('2026-02-02'):
      resp = client.get(f'/form/api/v1/forms/{form_id}')
      assert resp.status_code == 200
      assert resp.get_json()['is_public'] is True
  ```

---

### `tests/test_dashboard.py`

- **Description**: Validates dashboard analytics endpoints.
- **Inputs**: Query parameters `start_date`, `end_date`, optional `form_id`.
- **Outputs**: **200** with JSON containing metrics such as `total_submissions`, `unique_respondents`, and a `trend` array of `{date, count}`.
- **Error cases**: **400** for malformed dates.
- **Fixes**: Provide ISO‑8601 dates; seed the test database with known response counts before calling the endpoint.
- **Example (Python)**:

  ```python
  # Seed DB with 5 responses for form_id
  for i in range(5):
      client.post(f'/form/api/v1/forms/{form_id}/responses', json=response_payload)

  resp = client.get('/form/api/v1/dashboard/summary?start_date=2026-01-01&end_date=2026-01-31')
  assert resp.status_code == 200
  data = resp.get_json()
  assert data['total_submissions'] == 5
  assert isinstance(data['trend'], list)
  ```

---

### `tests/test_workflow.py`

- **Description**: Tests custom workflow configuration and execution.
- **Inputs**:
  - **Create workflow** payload:

    ```json
    {"name": "ApprovalFlow", "steps": [{"action": "send_email", "params": {"to": "admin@example.com"}}]}
    ```

    - `name`: Human‑readable identifier for the workflow.
    - `steps`: Ordered array of step objects; each step defines an `action` and its `params`.
  - **Trigger payload**:

    ```json
    {"input": {"form_id": "<uuid>", "response_id": "<uuid>"}}
    ```

    - `input`: Data that will be passed to the first step of the workflow.
- **Outputs**:
  - Creation **201** with `{"workflow_id": "<uuid>"}`.
  - Trigger **202** with `{"instance_id": "<uuid>"}` indicating the running instance.
- **Error cases**:
  - **400** if the workflow definition is missing required fields (`name`, `steps`).
- **Fixes**: Validate the JSON against the workflow schema before posting; ensure step actions are supported by the system.
- **Example (Python)**:

  ```python
  # Define a simple workflow that sends an email when a response is approved
  wf_def = {
      "name": "NotifyOnApprove",
      "steps": [
          {"action": "send_email", "params": {"to": "admin@example.com", "subject": "Response approved"}}
      ]
  }
  resp = client.post('/form/api/v1/workflows/create', json=wf_def)
  assert resp.status_code == 201
  wf_id = resp.get_json()['workflow_id']

  # Trigger the workflow with a response ID
  trigger = {"input": {"response_id": resp_id}}
  resp = client.post(f'/form/api/v1/workflows/{wf_id}/trigger', json=trigger)
  assert resp.status_code == 202
  assert 'instance_id' in resp.get_json()
  ```

---

### `tests/test_ai_generation.py`

- **Description**: Tests AI content generation.
- **Inputs**: Payload with a `prompt` string, e.g. `{"prompt": "Create a feedback form"}`.
- **Outputs**: **200** with `{"content": "<generated text>"}`.
- **Error cases**: **400** if `prompt` is missing or empty; **500** if the AI service crashes.
- **Fixes**: Provide a non‑empty prompt; mock the AI backend in tests to return a deterministic string.
- **Example (Python)**:

  ```python
  resp = client.post('/form/api/v1/ai/generation', json={"prompt": "Create a survey about product satisfaction"})
  assert resp.status_code == 200
  generated = resp.get_json()['content']
  assert 'question' in generated.lower()
  ```

---

### `tests/test_ai_moderation.py`

- **Description**: Tests AI moderation of content.
- **Inputs**: Payload with `content` string, e.g. `{"content": "some user text"}`.
- **Outputs**: **200** with `{"allowed": true, "reasons": []}` or `{"allowed": false, "reasons": ["profanity"]}`.
- **Error cases**: **400** if `content` missing.
- **Fixes**: Ensure `content` is present; mock moderation service to return expected verdicts.
- **Example (Python)**:

  ```python
  resp = client.post('/form/api/v1/ai/moderation', json={"content": "Hello world"})
  assert resp.status_code == 200
  result = resp.get_json()
  assert result['allowed'] is True
  ```

---

### `tests/test_ai_search.py`

- **Description**: Tests AI semantic search.
- **Inputs**: Payload with `query` string, e.g. `{"query": "find health forms"}`.
- **Outputs**: **200** with `{"results": [{"form_id": "<uuid>", "score": 0.93}]}`.
- **Error cases**: **400** if `query` empty.
- **Fixes**: Provide a meaningful query; mock the search service.
- **Example (Python)**:

  ```python
  resp = client.post('/form/api/v1/ai/search', json={"query": "insurance"})
  assert resp.status_code == 200
  results = resp.get_json()['results']
  assert any(r['score'] > 0.8 for r in results)
  ```

---

### `tests/test_ai_security_scan.py`

- **Description**: Tests AI security scanning of form definitions.
- **Inputs**: Full form definition JSON (same schema as `test_form.py`).
- **Outputs**: **200** with `{"issues": [{"type": "XSS", "field": "description"}]}`.
- **Error cases**: **400** if the definition is malformed.
- **Fixes**: Send a valid form JSON; mock the security scanner.
- **Example (Python)**:

  ```python
  resp = client.post('/form/api/v1/ai/security-scan', json=form_payload)
  assert resp.status_code == 200
  issues = resp.get_json()['issues']
  assert isinstance(issues, list)
  ```

---

### `tests/test_ai_templates.py`

- **Description**: Tests AI template generation.
- **Inputs**: Payload with a natural‑language `description`, e.g. `{"description": "A short survey for event feedback"}`.
- **Outputs**: **200** with generated template JSON under `"template"` key.
- **Error cases**: **400** if `description` missing.
- **Fixes**: Provide a clear description; mock the template service.
- **Example (Python)**:

  ```python
  resp = client.post('/form/api/v1/ai/templates', json={"description": "Feedback form for webinars"})
  assert resp.status_code == 200
  tmpl = resp.get_json()['template']
  assert 'fields' in tmpl
  ```

---

### `tests/test_ai_analysis.py`

- **Description**: Tests AI analysis of form usage patterns.
- **Inputs**: Payload with `form_id`, e.g. `{"form_id": "<uuid>"}`.
- **Outputs**: **200** with analysis report JSON, e.g. `{"average_completion_time": 42, "drop_off_rate": 0.12}`.
- **Error cases**: **404** if the form does not exist.
- **Fixes**: Use an existing form ID; mock the analysis service.
- **Example (Python)**:

  ```python
  resp = client.post('/form/api/v1/ai/analysis', json={"form_id": form_id})
  assert resp.status_code == 200
  report = resp.get_json()
  assert 'average_completion_time' in report
  ```

---

### `tests/test_ai_anomalies.py`

- **Description**: Tests AI anomaly detection on response batches.
- **Inputs**: Payload with a list of responses, e.g. `{"responses": [{"id": "...", "answers": {...}}]}`.
- **Outputs**: **200** with `{"anomalies": [{"response_id": "...", "reason": "outlier"}]}`.
- **Error cases**: **400** if the batch structure is invalid.
- **Fixes**: Provide a correctly structured list; mock the anomaly detection service.
- **Example (Python)**:

  ```python
  batch = {"responses": [response_payload]}
  resp = client.post('/form/api/v1/ai/anomalies', json=batch)
  assert resp.status_code == 200
  anomalies = resp.get_json()['anomalies']
  assert isinstance(anomalies, list)
  ```

---

### `tests/test_form_versioning.py`

- **Description**: Tests versioning of forms.
- **Inputs**: Payload with `changes` dict, e.g. `{"changes": {"title": "Updated Title"}}`.
- **Outputs**: **201** with `{"new_version_id": "<uuid>"}`; original form remains unchanged.
- **Error cases**: **404** if the original form is missing.
- **Fixes**: Create the original form first; send only allowed fields in `changes`.
- **Example (Python)**:

  ```python
  resp = client.post(f'/form/api/v1/forms/{form_id}/version', json={"changes": {"title": "Version 2"}})
  assert resp.status_code == 201
  new_id = resp.get_json()['new_version_id']
  # Verify original unchanged
  orig = client.get(f'/form/api/v1/forms/{form_id}').get_json()
  assert orig['title'] != 'Version 2'
  # Verify new version has updated title
  new = client.get(f'/form/api/v1/forms/{new_id}').get_json()
  assert new['title'] == 'Version 2'
  ```

---

### `tests/test_integration_flow.py`

- **Description**: End‑to‑end flow: login → create form → submit response → view → export.
- **Inputs**: Sequence of payloads as described in the individual test sections.
- **Outputs**: Each step returns its expected success code; final export returns the correct data format.
- **Error handling**: If any step fails, the test aborts and reports the failing response for debugging.
- **Example (Python)**:

  ```python
  # 1. Login
  login_resp = client.post('/form/api/v1/auth/login', json={"email": "alice@example.com", "password": "Secret123!"})
  token = login_resp.get_json()['access_token']

  # 2. Create a form
  form_resp = client.post('/form/api/v1/forms', json=form_payload, headers={"Authorization": f"Bearer {token}"})
  form_id = form_resp.get_json()['id']

  # 3. Submit a response
  resp_payload = {"answers": {"rating": 5, "comment": "Great!"}}
  sub_resp = client.post(f'/form/api/v1/forms/{form_id}/responses', json=resp_payload, headers={"Authorization": f"Bearer {token}"})
  response_id = sub_resp.get_json()['response_id']

  # 4. Retrieve the response
  get_resp = client.get(f'/form/api/v1/responses/{response_id}', headers={"Authorization": f"Bearer {token}"})
  assert get_resp.status_code == 200

  # 5. Export responses as CSV
  export_resp = client.get(f'/form/api/v1/forms/{form_id}/export/csv', headers={"Authorization": f"Bearer {token}"})
  assert export_resp.status_code == 200
  assert export_resp.headers['Content-Type'] == 'text/csv'
  ```

---

### `tests/test_misc.py`

- **Description**: Miscellaneous utilities – archiving, restoring, public toggle, slug checks, etc.
- **Inputs**: Vary per endpoint; examples include `{}` for archive, `{"is_public": true}` for toggle.
- **Outputs**: Standard success codes (**200**, **204**) with minimal JSON messages.
- **Error cases**: **404** if form not found; **400** for invalid payload.
- **Fixes**: Ensure the target form exists; send the correct fields.
- **Example (Python)**:

  ```python
  # Archive a form
  resp = client.post(f'/form/api/v1/forms/{form_id}/archive')
  assert resp.status_code == 200

  # Restore the archived form
  resp = client.post(f'/form/api/v1/forms/{form_id}/restore')
  assert resp.status_code == 200

  # Toggle public access
  resp = client.post(f'/form/api/v1/forms/{form_id}/toggle-public', json={"is_public": true})
  assert resp.status_code == 200
  ```

---

### `tests/test_multi_language.py`

- **Description**: Tests multi‑language support for forms and responses.
- **Inputs**: Form definition with `languages` dict, e.g.:

  ```json
  {
    "title": {"en": "Survey", "es": "Encuesta"},
    "fields": [{"name": "rating", "type": "number", "label": {"en": "Rating", "es": "Calificación"}}]
  }
  ```

  - `title` and field `label` are objects keyed by language code.
  - Response payload includes a `lang` field, e.g. `{"answers": {"rating": 4}, "lang": "es"}`.
- **Outputs**: Form creation **201**; response submission **201**; retrieval respects the requested language.
- **Error cases**: **400** if an unsupported language code is used.
- **Fixes**: Include all required language keys in the form definition; validate `lang` against the supported list.
- **Example (Python)**:

  ```python
  # Create a bilingual form
  bilingual_form = {
      "title": {"en": "Feedback", "es": "Retroalimentación"},
      "fields": [{"name": "rating", "type": "number", "label": {"en": "Rating", "es": "Calificación"}}],
      "languages": ["en", "es"]
  }
  resp = client.post('/form/api/v1/forms', json=bilingual_form)
  form_id = resp.get_json()['id']

  # Submit a Spanish response
  spanish_resp = {"answers": {"rating": 5}, "lang": "es"}
  resp = client.post(f'/form/api/v1/forms/{form_id}/responses', json=spanish_resp)
  assert resp.status_code == 201

  # Retrieve the form in Spanish
  resp = client.get(f'/form/api/v1/forms/{form_id}?lang=es')
  data = resp.get_json()
  assert data['title']['es'] == 'Retroalimentación'
  ```

---

### `tests/test_preview_mode.py`

- **Description**: Tests preview mode allowing admins to view a form before publishing.
- **Inputs**: No body; simply a `GET` request with optional `preview=true` query flag.
- **Outputs**: **200** with full form JSON even if `is_published` is false.
- **Error cases**: **404** if the form does not exist.
- **Fixes**: Use a valid form ID; ensure the endpoint is enabled in the configuration (`ENABLE_PREVIEW=true`).
- **Example (Python)**:

  ```python
  resp = client.get(f'/form/api/v1/forms/{form_id}/preview')
  assert resp.status_code == 200
  form = resp.get_json()
  assert form['is_published'] is False
  ```

---

### `tests/test_reordering.py`

- **Description**: Tests reordering of form fields.
- **Inputs**: Payload with a new `order` array of field IDs, e.g.:

  ```json
  {"order": ["field3", "field1", "field2"]}
  ```

  - The array must contain **all** existing field IDs exactly once.
- **Outputs**: **200** with the updated form schema reflecting the new order.
- **Error cases**: **400** if the `order` list is missing fields or contains duplicates.
- **Fixes**: Retrieve the current field IDs (`GET /forms/{id}`), then construct a permutation that includes each ID once.
- **Example (Python)**:

  ```python
  # Get current field IDs
  form = client.get(f'/form/api/v1/forms/{form_id}').get_json()
  field_ids = [f['id'] for f in form['fields']]
  new_order = field_ids[::-1]  # simple reversal
  resp = client.post(f'/form/api/v1/forms/{form_id}/reorder', json={"order": new_order})
  assert resp.status_code == 200
  updated = client.get(f'/form/api/v1/forms/{form_id}').get_json()
  assert [f['id'] for f in updated['fields']] == new_order
  ```

---

### `tests/test_response_drafts.py`

- **Description**: Tests automatic saving of response drafts.
- **Inputs**: Partial response payload (any subset of required fields) and optionally a `draft_id` to update an existing draft.
- **Outputs**: **200** with `{"draft_id": "<uuid>"}`; subsequent calls with the same `draft_id` update the stored draft.
- **Error cases**: **400** if payload invalid; **404** if `draft_id` does not exist.
- **Fixes**: Start with a fresh draft (no `draft_id`), then reuse the returned `draft_id` for incremental saves.
- **Example (Python)**:

  ```python
  # First save – creates a draft
  partial = {"answers": {"rating": 3}}
  resp = client.post('/form/api/v1/responses/draft', json=partial)
  assert resp.status_code == 200
  draft_id = resp.get_json()['draft_id']

  # Second save – updates the same draft
  more = {"draft_id": draft_id, "answers": {"comment": "Will improve"}}
  resp = client.post('/form/api/v1/responses/draft', json=more)
  assert resp.status_code == 200
  ```

---

### `tests/test_response_management.py`

- **Description**: Tests bulk operations on responses (batch delete, status update).
- **Inputs**:
  - **Batch delete** payload:

    ```json
    {"ids": ["uuid1", "uuid2"]}
    ```

  - **Batch status update** payload:

    ```json
    {"ids": ["uuid1"], "status": "archived"}
    ```

- **Outputs**:
  - Delete: **200** with `{"deleted": 2}`.
  - Status update: **200** with `{"updated": 1}`.
- **Error cases**: **400** for malformed list; **404** for non‑existent IDs.
- **Fixes**: Verify IDs exist before the bulk call; handle partial successes by checking the returned counts.
- **Example (Python)**:

  ```python
  # Assume we have two response IDs
  ids = [resp1_id, resp2_id]
  resp = client.post('/form/api/v1/responses/batch-delete', json={"ids": ids})
  assert resp.status_code == 200
  assert resp.get_json()['deleted'] == 2

  # Change status of a response batch
  resp = client.post('/form/api/v1/responses/batch-status', json={"ids": [resp3_id], "status": "archived"})
  assert resp.status_code == 200
  assert resp.get_json()['updated'] == 1
  ```

---

### `tests/test_response_merge.py`

- **Description**: Tests merging of duplicate responses.
- **Inputs**: Payload with `source_ids` array, e.g.:

  ```json
  {"source_ids": ["uuid1", "uuid2"]}
  ```

- **Outputs**: **200** with `{"merged_id": "<new_uuid>", "merged_from": ["uuid1", "uuid2"]}`.
- **Error cases**: **400** if the responses are not duplicates; **404** if any ID is missing.
- **Fixes**: Ensure the responses have identical answers before merging; create them in the test with the same payload.
- **Example (Python)**:

  ```python
  # Create two identical responses
  payload = {"answers": {"rating": 5, "comment": "Great"}}
  r1 = client.post(f'/form/api/v1/forms/{form_id}/responses', json=payload).get_json()['response_id']
  r2 = client.post(f'/form/api/v1/forms/{form_id}/responses', json=payload).get_json()['response_id']

  # Merge them
  resp = client.post('/form/api/v1/responses/merge', json={"source_ids": [r1, r2]})
  assert resp.status_code == 200
  merged = resp.get_json()
  assert merged['merged_id'] is not None
  assert set(merged['merged_from']) == {r1, r2}
  ```

---

*All test files now contain exhaustive field‑by‑field explanations, concrete examples in both natural language and Python code, and detailed guidance on expected results, error handling, and how to fix common failures. This deep documentation should make writing, extending, and debugging the test suite straightforward.*

---
