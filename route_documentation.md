# Backend API Route Documentation

This document provides a comprehensive reference for all available API routes in the `app/routes` directory.

## Base URL

All API routes are prefixed. The common patterns are:

* **API Routes:** `/form/api/v1/{service}`
* **View Routes:** `/form/`

---

## 2. Authentication & Authorization

The API uses **JWT (JSON Web Tokens)** for authentication.

### How to Authenticate

1. **Login:** Send a `POST` request to `/form/api/v1/auth/login` with credentials (`email`/`password` or `mobile`/`otp`).
2. **Receive Token:** The response will contain an `access_token`.
3. **Use Token:** Include the token in the `Authorization` header of all subsequent requests:

```http
Authorization: Bearer <your_access_token>
```

*Alternatively, the API also supports cookies (`access_token_cookie`) for browser-based clients.*

### Roles & Permissions

Endpoints are protected by Role-Based Access Control (RBAC). Common roles:

* `admin` / `superadmin`: Full access to all resources.
* `creator`: Can create and manage their own forms.
* `employee` / `general`: Can submit forms and view their own data.

---

## 3. Error Handling

All API errors return a standardized JSON format.

**Standard Error Response:**

```json
{
  "error": "Short error description",
  "message": "Detailed error message (optional)",
  "details": { ... } // Optional validation structure
}
```

**Common HTTP Status Codes:**

* `200 OK` - Success.
* `201 Created` - Resource created successfully.
* `400 Bad Request` - Invalid input or validation failure.
* `401 Unauthorized` - Missing or invalid authentication token.
* `403 Forbidden` - Insufficient permissions (Role mismatch).
* `404 Not Found` - Resource (Form, User, Response) not found.
* `500 Internal Server Error` - Unexpected server-side error.

---

## 4. Pagination & Filtering

List endpoints support standard pagination parameters via query strings.

**Parameters:**

* `page`: Page number (default: `1`)
* `limit`: Number of items per page (default: `10`)
* `sort_by`: Field to sort by (e.g., `created_at`)
* `sort_order`: `asc` or `desc` (default: `desc`)

**Example:**
`GET /form/api/v1/form/123/responses/paginated?page=2&limit=25`

**Response Format:**

```json
{
  "total": 100,
  "page": 2,
  "responses": [ ... ]
}
```

---

## 5. Rate Limiting

*Currently, explicit rate limiting is not enforced at the application level, but clients should avoid excessive polling. Webhooks are recommended for real-time updates.*

---

## 6. Authentication Service

**Base path:** `/form/api/v1/auth`

### 6.1 Register User

Register a new user in the system.

* **Endpoint:** `/register`
* **Method:** `POST`
* **Auth Required:** No

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `username` | string | Yes | Unique username for the user. |
| `email` | string | Yes | Valid email address (must be unique). |
| `password` | string | Yes | Strong password. |
| `user_type` | string | Yes | `employee` or `general`. |
| `employee_id` | string | No | Required if `user_type` is `employee`. |
| `mobile` | string | No | Mobile number for OTP login. |

**Output:** `201 Created`, `409 Conflict`, `400 Bad Request`.

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jdoe",
    "email": "jdoe@example.com",
    "password": "SecurePassword123!",
    "user_type": "employee",
    "employee_id": "E1001"
  }'
```

**Response:**

```json
{
  "message": "User registered"
}
```

---

### 6.2 Login

Authenticate a user and retrieve a JWT access token. Supports password or OTP.

* **Endpoint:** `/login`
* **Method:** `POST`
* **Auth Required:** No

**Input Schema (Password Flow):**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `identifier` | string | Yes | Email, Username, or Employee ID. |
| `password` | string | Yes | User's password. |

**Input Schema (OTP Flow):**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `mobile` | string | Yes | Registered mobile number. |
| `otp` | string | Yes | 6-digit OTP received via SMS. |

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "jdoe@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
  "success": true
}
```

---

### 6.3 Generate OTP

Generate and send an OTP to the user's mobile number for login.

* **Endpoint:** `/generate-otp`
* **Method:** `POST`
* **Auth Required:** No

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `mobile` | string | Yes | Registered mobile number. |

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/auth/generate-otp \
  -H "Content-Type: application/json" \
  -d '{"mobile": "9876543210"}'
```

---

### 6.4 Logout

Invalidate the current session/token.

* **Endpoint:** `/logout`
* **Method:** `POST`
* **Auth Required:** Yes (JWT)

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/auth/logout \
  -H "Authorization: Bearer <token>"
```

---

## 7. User Service

**Base path:** `/form/api/v1/user`

### 7.1 Get Current User Status

Retrieve profile information for the currently logged-in user.

* **Endpoint:** `/status`
* **Method:** `GET`
* **Auth Required:** Yes

**Example Request:**

```bash
curl -X GET http://localhost:5000/form/api/v1/user/status \
  -H "Authorization: Bearer <token>"
```

**Response:**

```json
{
  "user": {
    "id": "65af...",
    "username": "jdoe",
    "email": "jdoe@example.com",
    "roles": ["employee"],
    "user_type": "employee"
  }
}
```

---

### 7.2 Change Password

Allow a logged-in user to change their own password.

* **Endpoint:** `/change-password`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `current_password` | string | Yes | The user's old password. |
| `new_password` | string | Yes | The new password to set. |

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/user/change-password \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"current_password": "Old", "new_password": "New"}'
```

---

### 7.3 List Users (Admin)

List all users in the system.

* **Endpoint:** `/users`
* **Method:** `GET`
* **Auth Required:** Yes (Admin/Superadmin)

---

### 7.4 Get Specific User (Admin)

Retrieve details of a specific user.

* **Endpoint:** `/users/<user_id>`
* **Method:** `GET`
* **Auth Required:** Yes (Admin/Superadmin)

---

### 7.5 Create User (Admin)

Create a new user manually.

* **Endpoint:** `/users`
* **Method:** `POST`
* **Auth Required:** Yes (Admin/Superadmin)

---

### 7.6 Update User (Admin)

Update user details.

* **Endpoint:** `/users/<user_id>`
* **Method:** `PUT`
* **Auth Required:** Yes (Admin/Superadmin)

---

### 7.7 Delete User (Admin)

Remove a user from the system.

* **Endpoint:** `/users/<user_id>`
* **Method:** `DELETE`
* **Auth Required:** Yes (Admin/Superadmin)

---

### 7.8 Lock/Unlock User (Admin)

* **Endpoints:**
  * `/<user_id>/lock` (POST)
  * `/<user_id>/unlock` (POST)
* **Auth Required:** Yes (Admin/Superadmin)

---

### 7.9 Security Utilities

* **Endpoints:**
  * `/security/extend-password-expiry` (POST) - Extend password validity.
  * `/security/lock-status/<user_id>` (GET) - Check if account is locked.
  * `/security/resend-otp` (POST) - Resend OTP to mobile.
  * `/<user_id>/reset-otp-count` (POST) - Reset OTP resend attempts.

---

## 8. Dashboard Service

**Base path:** `/form/api/v1/dashboards`

### 8.1 List Dashboards

List dashboards accessible to the current user.

* **Endpoint:** `/`
* **Method:** `GET`
* **Auth Required:** Yes

---

### 8.2 Create Dashboard

Create a new dashboard configuration.

* **Endpoint:** `/`
* **Method:** `POST`
* **Auth Required:** Yes (Admin)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | string | Yes | Dashboard Title. |
| `slug` | string | Yes | Unique URL Identifier. |
| `widgets` | array | No | List of widget objects. |

---

### 8.3 Get Dashboard

Fetch a dashboard by slug, including widget data.

* **Endpoint:** `/<slug>`
* **Method:** `GET`
* **Auth Required:** Yes

---

### 8.4 Update Dashboard

Update an existing dashboard configuration.

* **Endpoint:** `/<id>`
* **Method:** `PUT`
* **Auth Required:** Yes (Admin)

---

## 9. Workflow Service

**Base path:** `/form/api/v1/workflows`

### 9.1 List Workflows

List available workflows.

* **Endpoint:** `/`
* **Method:** `GET`
* **Auth Required:** Yes (Admin)
* **Params:** `trigger_form_id` (optional).

---

### 9.2 Create Workflow

* **Endpoint:** `/`
* **Method:** `POST`
* **Auth Required:** Yes (Admin)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | Yes | Workflow Name. |
| `trigger_form_id` | string | Yes | Which form triggers this. |
| `trigger_condition` | string | No | Python expression for triggering. |
| `actions` | array | No | List of actions (target_form, mapping). |

---

### 9.3 Get Workflow

* **Endpoint:** `/<id>`
* **Method:** `GET`
* **Auth Required:** Yes (Admin)

---

### 9.4 Update Workflow

* **Endpoint:** `/<id>`
* **Method:** `PUT`
* **Auth Required:** Yes (Admin)

---

### 9.5 Delete Workflow

* **Endpoint:** `/<id>`
* **Method:** `DELETE`
* **Auth Required:** Yes (Admin)

---

## 10. Form Service

**Base path:** `/form/api/v1/form`

### 10.1 Create Form

Create a new form definition structure.

* **Endpoint:** `/`
* **Method:** `POST`
* **Auth Required:** Yes (Creator/Admin)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | string | Yes | Form title. |
| `slug` | string | Yes | Unique URL identifier. |
| `description` | string | No | Form description. |
| `is_public` | boolean | No | Allow anonymous submissions. |

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/form/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Customer Feedback",
    "slug": "customer-feedback-v1",
    "is_public": true
  }'
```

**Response:**

```json
{
  "message": "Form created",
  "form_id": "65af..."
}
```

---

### 10.2 List Forms

List forms created by or shared with the user.

* **Endpoint:** `/`
* **Method:** `GET`
* **Auth Required:** Yes

**Example Request:**

```bash
curl -X GET http://localhost:5000/form/api/v1/form/ \
  -H "Authorization: Bearer <token>"
```

---

### 10.3 Get Form Definition

Retrieve the structure (questions, logic) of a form.

* **Endpoint:** `/<form_id>`
* **Method:** `GET`
* **Auth Required:** Yes

---

### 10.4 Update Form

Update basic form settings.

* **Endpoint:** `/<form_id>`
* **Method:** `PUT`
* **Auth Required:** Yes (Editor/Admin)

---

### 10.5 Delete Form

Permanently delete a form and all its responses.

* **Endpoint:** `/<form_id>`
* **Method:** `DELETE`
* **Auth Required:** Yes (Admin/Superadmin)

---

### 10.6 Clone Form

Duplicate an existing form structure.

* **Endpoint:** `/<form_id>/clone`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `title` | string | No | New title. |
| `slug` | string | No | New slug. |

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/form/65af.../clone \
  -H "Authorization: Bearer <token>" \
  -d '{"title": "Feedback Copy", "slug": "feedback-v2"}'
```

---

### 10.7 Create Form Version

Snapshot the current form structure as a numbered version.

* **Endpoint:** `/<form_id>/versions`
* **Method:** `POST`
* **Auth Required:** Yes (Editor)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `version` | string | Yes | Version string (e.g., "1.1"). |
| `sections` | array | Yes | Current sections with questions. |
| `activate` | boolean | No | Set as active version immediately. |

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/form/65af.../versions \
  -H "Authorization: Bearer <token>" \
  -d '{"version": "2.0", "sections": [], "activate": true}'
```

---

### 10.8 Submit Response

Submit a filled form entry.

* **Endpoint:** `/<form_id>/responses`
* **Method:** `POST`
* **Auth Required:** Yes (For private forms)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `data` | object | Yes | Key-value mapping of IDs to answers. |
| `is_draft` | boolean | No | Save as draft. |

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/form/65af.../responses \
  -H "Authorization: Bearer <token>" \
  -d '{"data": {"q_123": "Answer"}}'
```

---

---

### 10.9 List Form Versions

Retrieve all versions available for a specific form.

* **Endpoint:** `/<form_id>/versions`
* **Method:** `GET`
* **Auth Required:** Yes

---

### 10.10 Activate Version

Set a specific version as the active version for submissions.

* **Endpoint:** `/<form_id>/versions/<v_str>/activate`
* **Method:** `PATCH`
* **Auth Required:** Yes (Editor)

---

### 10.11 Get Form Version

Retrieve a specific version of a form.

* **Endpoint:** `/<form_id>/versions/<v_str>`
* **Method:** `GET`
* **Auth Required:** Yes

**Example Request:**

```bash
curl -X GET http://localhost:5000/form/api/v1/form/65af.../versions/1.1 \
  -H "Authorization: Bearer <token>"
```

---

### 10.12 Update Form Version

Update structure and settings for a specific form version.

* **Endpoint:** `/<form_id>/versions/<v_str>`
* **Method:** `PUT`
* **Auth Required:** Yes (Editor)

---

### 10.13 Update Translations

Add or update translations for a specific language.

* **Endpoint:** `/<form_id>/translations`
* **Method:** `POST`
* **Auth Required:** Yes (Editor)
* **Input:** `{"lang_code": "es", "translations": {...}}`

---

### 10.14 Reorder Sections

Change the order of sections in a form version.

* **Endpoint:** `/<form_id>/reorder-sections`
* **Method:** `PATCH`
* **Params:** `v` (optional version string, defaults to latest).
* **Auth Required:** Yes (Editor)

**Input:** `{"order": ["section_id_1", "section_id_2"]}`

---

### 10.15 Reorder Questions

Change the order of questions within a section.

* **Endpoint:** `/<form_id>/section/<section_id>/reorder-questions`
* **Method:** `PATCH`
* **Params:** `v` (optional version string, defaults to latest).
* **Auth Required:** Yes (Editor)

**Input:** `{"order": ["q_id_1", "q_id_2"]}`

---

### 10.16 Bulk Import Options

Import choices for a question from a CSV file.

* **Endpoint:** `/<form_id>/section/<section_id>/question/<question_id>/options/import`
* **Method:** `POST`
* **Params:**
  * `replace` (boolean, default false)
  * `v` (optional version string, defaults to latest)
* **Auth Required:** Yes (Editor)

**Input:** Multipart form-data with `file` field.

---

### 10.17 List Responses

Retrieve submissions for a form.

* **Endpoint:** `/<form_id>/responses`
* **Method:** `GET`
* **Auth Required:** Yes
* **Params:** `status` (optional).

**Example Request:**

```bash
curl -X GET http://localhost:5000/form/api/v1/form/65af.../responses?status=pending \
  -H "Authorization: Bearer <token>"
```

---

---

### 10.18 Preview Submission

Validate submission data against the form schema without saving it. Useful for testing.

* **Endpoint:** `/<form_id>/preview`
* **Method:** `POST`
* **Auth Required:** Yes
* **Input Schema:** Same as **Submit Response**.

---

## 11. AI Service

**Base path:** `/form/api/v1/ai`

### 11.1 Generate Form Structure

Generate a form schema from a text description.

* **Endpoint:** `/generate`
* **Method:** `POST`
* **Auth Required:** Yes

**Input:** `{"prompt": "Job application form"}`

---

### 11.2 Analyze Response

Perform sentiment analysis and PII scanning on a response.

* **Endpoint:** `/<form_id>/responses/<id>/analyze`
* **Method:** `POST`
* **Auth Required:** Yes

---

### 11.3 Content Moderation

Perform deep moderation (Profanity, Injection, PHI detection).

* **Endpoint:** `/<form_id>/responses/<id>/moderate`
* **Method:** `POST`
* **Auth Required:** Yes

---

### 11.4 Field Suggestions

Get AI-powered field suggestions based on a theme.

* **Endpoint:** `/suggestions`
* **Method:** `POST`
* **Auth Required:** Yes
* **Input:** `{"theme": "feedback"}`

---

### 11.5 AI Templates

* **Endpoints:**
  * `GET /templates` - List AI form templates.
  * `GET /templates/<template_id>` - Get specific template structure.
* **Auth Required:** Yes

---

### 11.6 Sentiment Trends

Get aggregate sentiment distribution for a form.

* **Endpoint:** `/<form_id>/sentiment`
* **Method:** `GET`
* **Auth Required:** Yes

---

### 11.7 AI Powered Search

Natural language search that translates to filters.

* **Endpoint:** `/<form_id>/search`
* **Method:** `POST`
* **Auth Required:** Yes
* **Input:** `{"query": "patients over 60"}`

---

### 11.8 Anomaly Detection

Scan for duplicates, outliers, and low-quality responses.

* **Endpoint:** `/<form_id>/anomalies`
* **Method:** `POST`
* **Auth Required:** Yes

---

### 11.9 Security Scan

Analyze form definition for vulnerabilities.

* **Endpoint:** `/<form_id>/security-scan`
* **Method:** `POST`
* **Auth Required:** Yes

---

## 12. View Service (Frontend)

**Base path:** `/form/`

### 12.1 View Login Page

Renders the HTML login page.

* **Endpoint:** `/`
* **Method:** `GET`
* **Auth Required:** No

**Example Request:**
Open in Browser: `http://localhost:5000/form/`

**Output:** HTML Content.

---

### 12.2 View Form

Renders the HTML for a specific public or private form.

* **Endpoint:** `/<form_id>`
* **Method:** `GET`
* **Auth Required:** No (if Public), Yes (Token cookie needed if Private)
* **Params:** `lang` (optional language code).

**Example Request:**
Open in Browser: `http://localhost:5000/form/65af...?lang=es`

**Output:** HTML Content with `window.Context` populated.

---

## 13. Advanced Form Actions

**Base path:** `/form/api/v1/form`

### 13.1 Publish Form

Change form status to `published`.

* **Endpoint:** `/<form_id>/publish`
* **Method:** `PATCH`
* **Auth Required:** Yes (Editor/Admin)

---

### 13.2 Archive Form

Change form status to `archived`.

* **Endpoint:** `/<form_id>/archive`
* **Method:** `PATCH`
* **Auth Required:** Yes (Admin)

---

### 13.3 Restore Form

Restore an `archived` form to `draft`.

* **Endpoint:** `/<form_id>/restore`
* **Method:** `PATCH`
* **Auth Required:** Yes (Admin)

---

### 13.4 Share Form

Add editors, viewers, or submitters to a form.

* **Endpoint:** `/<form_id>/share`
* **Method:** `POST`
* **Auth Required:** Yes (Admin)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `editors` | array | No | List of user IDs. |
| `viewers` | array | No | List of user IDs. |
| `submitters` | array | No | List of user IDs. |

---

### 13.5 Toggle Public Access

Enable or disable anonymous submissions.

* **Endpoint:** `/<form_id>/toggle-public`
* **Method:** `PATCH`
* **Auth Required:** Yes (Admin)

---

### 13.6 Public Submission

Submit a response anonymously (if form is public).

* **Endpoint:** `/<form_id>/public-submit`
* **Method:** `POST`
* **Auth Required:** No

**Input Schema:**
Same as **Submit Response**.

---

---

### 13.7 Expire Form

Set a date/time after which the form will no longer accept submissions.

* **Endpoint:** `/<form_id>/expire`
* **Method:** `PATCH`
* **Auth Required:** Yes (Admin/Superadmin)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `expires_at` | string | Yes | ISO 8601 Datetime (e.g., "2023-12-31T23:59:59Z") |

---

### 13.8 List Expired Forms

List all forms that have passed their expiration date.

* **Endpoint:** `/expired`
* **Method:** `GET`
* **Auth Required:** Yes (Admin/Superadmin)

---

## 14. Response Management (Detailed)

**Base path:** `/form/api/v1/form`

### 14.1 Update Response

Modify an existing submission.

* **Endpoint:** `/<form_id>/responses/<response_id>`
* **Method:** `PUT`
* **Auth Required:** Yes

---

### 14.2 Delete Response

Soft-delete a response.

* **Endpoint:** `/<form_id>/responses/<response_id>`
* **Method:** `DELETE`
* **Auth Required:** Yes

---

### 14.3 Delete All Responses

Delete **ALL** responses for a form (Admin only).

* **Endpoint:** `/<form_id>/responses`
* **Method:** `DELETE`
* **Auth Required:** Yes (Admin)

---

### 14.4 Archive/Restore Response

Archive or restore a specific submission.

* **Endpoints:**
  * `/<form_id>/responses/<response_id>/archive` (PATCH)
  * `/<form_id>/responses/<response_id>/restore` (PATCH)
* **Auth Required:** Yes

---

### 14.5 Response Status

Update status (e.g., `approved`, `pending`, `rejected`).

* **Endpoint:** `/<form_id>/responses/<response_id>/status`
* **Method:** `PATCH`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `status` | string | New status value. |

---

### 14.6 Approval Workflow

Approve or Reject a response workflow step.

* **Endpoints:**
  * `/<form_id>/responses/<response_id>/approve` (POST)
  * `/<form_id>/responses/<response_id>/reject` (POST)
* **Auth Required:** Yes (Approver Role)
* **Input:** `{"comment": "Optional comment"}`

---

### 14.7 Comments

Manage comments on a response.

* **Endpoints:**
  * `GET /<form_id>/responses/<response_id>/comments`
  * `POST /<form_id>/responses/<response_id>/comments`
* **Auth Required:** Yes

---

### 14.8 Saved Searches

Save complex filters for reuse.

* **Endpoints:**
  * `POST /<form_id>/saved-search` (Create)
  * `GET /<form_id>/saved-search` (List)
  * `DELETE /<form_id>/saved-search/<id>` (Delete)
* **Auth Required:** Yes

---

### 14.9 Advanced Search

Search responses with complex JSON structure.

* **Endpoint:** `/<form_id>/responses/search`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `data` | object | Filter criteria by question ID. |
| `limit` | integer | Max results. |
| `sort_by` | string | `submitted_at`, etc. |

---

### 14.10 Response History

View audit log of a response.

* **Endpoint:** `/<form_id>/responses/<response_id>/history`
* **Method:** `GET`
* **Auth Required:** Yes

---

---

### 14.11 List Responses (Paginated)

Retrieve responses with server-side pagination.

* **Endpoint:** `/<form_id>/responses/paginated`
* **Method:** `GET`
* **Auth Required:** Yes
* **Params:**
  * `page` (default: 1)
  * `limit` (default: 10)
  * `is_draft` (boolean, default: false)

**Response:**

```json
{
  "total": 50,
  "page": 1,
  "responses": [...]
}
```

---

## 15. Form Analytics

**Base path:** `/form/api/v1/form`

### 15.1 Get Analytics Summary

Get total counts and status breakdown.

* **Endpoint:** `/<form_id>/analytics/summary`
* **Method:** `GET`
* **Auth Required:** Yes

---

### 15.2 Get Timeline

Get submission counts over time.

* **Endpoint:** `/<form_id>/analytics/timeline`
* **Method:** `GET`
* **Auth Required:** Yes
* **Params:** `days` (default 30).

---

### 15.3 Get Distribution

Get answer choices distribution (charts data).

* **Endpoint:** `/<form_id>/analytics/distribution`
* **Method:** `GET`
* **Auth Required:** Yes

---

## 16. Data Export

**Base path:** `/form/api/v1/form`

### 16.1 Export CSV

Download responses as CSV file.

* **Endpoint:** `/<form_id>/export/csv`
* **Method:** `GET`
* **Auth Required:** Yes

---

### 16.2 Export JSON

Download full form definition and responses as JSON.

* **Endpoint:** `/<form_id>/export/json`
* **Method:** `GET`
* **Auth Required:** Yes

---

### 16.3 Bulk Export

Download ZIP of multiple forms' CSVs.

* **Endpoint:** `/export/bulk`
* **Method:** `POST`
* **Auth Required:** Yes

**Input:** `{"form_ids": ["id1", "id2"]}`

---

## 17. Helper Utilities

**Base path:** `/form/api/v1/form`

### 17.1 Check Slug Availability

Check if a URL slug is taken.

* **Endpoint:** `/slug-available`
* **Method:** `GET`
* **Params:** `slug`

### 17.2 Serve File

Download an uploaded file.

* **Endpoint:** `/<form_id>/files/<question_id>/<filename>`
* **Method:** `GET`
* **Auth Required:** Yes (or Public if form is public).

### 17.3 Check Duplicate

Check if user has already submitted specific data.

* **Endpoint:** `/<form_id>/check-duplicate`
* **Method:** `POST`
* **Auth Required:** Yes

### 17.4 Global Submission History

Search for submissions by specific question value across form history.

* **Endpoint:** `/<form_id>/history`
* **Method:** `GET`
* **Params:** `question_id`, `primary_value`.

---

## 18. AI Services (M2 - AI-Driven Intelligence)

**Base path:** `/form/api/v1/ai/forms/<form_id>`

**Authentication:** JWT Required for all endpoints

**Dependencies:**
- Requires Ollama service running for semantic search and LLM features
- Fallback to keyword-based search if Ollama unavailable

---

### 18.1 NLP Search Enhancement (T-M2-02)

**Base path:** `/form/api/v1/ai/forms/<form_id>`

#### 18.1.1 Natural Language Search

Search form responses using natural language queries. Supports sentiment filtering, topic extraction, and semantic search.

* **Endpoint:** `/nlp-search`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | string | Yes | Natural language search query (e.g., "Show me all users who were unhappy with delivery") |
| `options.max_results` | integer | No | Maximum results to return (default: 50) |
| `options.include_sentiment` | boolean | No | Include sentiment analysis in results (default: true) |
| `options.semantic_search` | boolean | No | Use Ollama embeddings for semantic matching (default: true) |
| `options.cache_results` | boolean | No | Cache results for 1 hour (default: true) |

**Response Schema (Success):**

```json
{
  "query": "Show me all users who were unhappy with delivery",
  "parsed_intent": {
    "original_query": "Show me all users who were unhappy with delivery",
    "search_query": "users delivery",
    "sentiment_filter": "negative",
    "topic": "delivery",
    "entities": ["delivery", "users"],
    "requires_semantic": false
  },
  "results_count": 15,
  "results": [
    {
      "response_id": "resp_123",
      "data": {
        "section_main": {
          "q_satisfaction": "The delivery was terrible and arrived late"
        }
      },
      "sentiment": {
        "label": "negative",
        "score": -3
      },
      "similarity_score": 0.92,
      "highlighted_text": "The <mark>delivery</mark> was terrible and arrived late"
    }
  ],
  "processing_time_ms": 245,
  "cached": false
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/nlp-search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all users who were unhappy with delivery",
    "options": {
      "max_results": 50,
      "include_sentiment": true,
      "semantic_search": true,
      "cache_results": true
    }
  }'
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.parse_query()`, `NLPSearchService.semantic_search()`

---

#### 18.1.2 Semantic Search

Pure semantic search using Ollama embeddings for similarity matching.

* **Endpoint:** `/semantic-search`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | string | Yes | Search query for semantic matching |
| `similarity_threshold` | float | No | Minimum similarity score 0-1 (default: 0.7) |
| `max_results` | integer | No | Maximum results to return (default: 20) |

**Response Schema (Success):**

```json
{
  "query": "What are the main complaints about product quality?",
  "embedding_model": "nomic-embed-text",
  "results_count": 8,
  "results": [
    {
      "response_id": "resp_456",
      "data": {...},
      "similarity_score": 0.85,
      "highlighted_text": "...product <mark>quality</mark> was poor and items were damaged..."
    }
  ]
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/semantic-search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main complaints about product quality?",
    "similarity_threshold": 0.7,
    "max_results": 20
  }'
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.semantic_search()`, `app/services/ollama_service.py` - `OllamaService.generate_embedding()`

---

#### 18.1.3 Search Statistics

Get search-related statistics for a form.

* **Endpoint:** `/search-stats`
* **Method:** `GET`
* **Auth Required:** Yes

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "total_responses": 250,
  "indexed_responses": 250,
  "ollama_available": true,
  "ollama_models": ["llama3.2", "nomic-embed-text"],
  "supported_query_types": ["sentiment", "topic", "semantic", "keyword", "time_based"],
  "cache_ttl_seconds": 3600
}
```

---

### 18.2 Automated Summarization (T-M2-03)

**Base path:** `/form/api/v1/ai/forms/<form_id>`

#### 18.2.1 Generate Summary

Automatically summarize form responses using extractive or abstractive methods.

* **Endpoint:** `/summarize`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `response_ids` | array | No | Specific response IDs to summarize (defaults to all) |
| `strategy` | string | No | "extractive", "abstractive", or "hybrid" (default: "hybrid") |
| `format` | string | No | "bullet_points" or "themes" (default: "bullet_points") |
| `config.max_points` | integer | No | Maximum bullet points (default: 5) |
| `config.focus_area` | string | No | Focus area filter: "all", "sentiment", "topics" |
| `config.include_sentiment` | boolean | No | Include sentiment analysis (default: true) |
| `config.include_quotes` | boolean | No | Include supporting quotes (default: true) |

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "responses_analyzed": 150,
  "strategy_used": "hybrid",
  "summary": {
    "format": "bullet_points",
    "bullet_points": [
      {
        "point": "Majority of customers (65%) mentioned slow delivery times",
        "sentiment": "negative",
        "supporting_count": 98,
        "confidence": 0.85
      },
      {
        "point": "Product quality received positive feedback (40 mentions)",
        "sentiment": "positive",
        "supporting_count": 40,
        "confidence": 0.78
      }
    ],
    "theme_analysis": {
      "delivery": { "sentiment": "negative", "mentions": 98 },
      "product_quality": { "sentiment": "positive", "mentions": 40 },
      "customer_support": { "sentiment": "positive", "mentions": 25 }
    }
  },
  "metadata": {
    "processing_time_ms": 1250,
    "model_used": "llama3.2",
    "cached": false
  }
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/summarize \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "hybrid",
    "format": "bullet_points",
    "config": {
      "max_points": 5,
      "focus_area": "all",
      "include_sentiment": true
    }
  }'
```

**Service Layer:** `app/services/summarization_service.py` - `SummarizationService.hybrid_summarize()`, `SummarizationService.extractive_summarize()`

---

#### 18.2.2 Executive Summary

Generate executive-level summary for leadership reporting.

* **Endpoint:** `/executive-summary`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `response_ids` | array | No | Specific response IDs (defaults to all) |
| `audience` | string | No | "leadership", "operations", or "product" (default: "leadership") |
| `tone` | string | No | "formal" or "concise" (default: "formal") |
| `include_metrics` | boolean | No | Include metrics in summary (default: true) |

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "executive_summary": {
    "overview": "Based on 150 responses, customer sentiment is mixed with 55% negative, 30% positive, and 15% neutral feedback.",
    "key_findings": [
      "Delivery performance is the primary driver of negative sentiment",
      "Product quality consistently exceeds expectations",
      "Customer support interactions show high satisfaction"
    ],
    "recommendations": [
      "Prioritize delivery speed improvements",
      "Maintain current product quality standards",
      "Document support interaction best practices"
    ],
    "metrics": {
      "total_responses": 150,
      "avg_sentiment_score": -0.3,
      "response_rate": 78
    }
  },
  "generated_at": "2026-02-04T10:00:00Z"
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/executive-summary \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "audience": "leadership",
    "tone": "formal"
  }'
```

**Service Layer:** `app/services/summarization_service.py` - `SummarizationService.generate_executive_summary()`

---

#### 18.2.3 Theme Summary

Generate theme-based analysis of responses.

* **Endpoint:** `/theme-summary`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `themes` | array | No | Themes to analyze (default: ["delivery", "product", "support", "pricing"]) |
| `include_quote_examples` | boolean | No | Include example quotes (default: true) |
| `sentiment_per_theme` | boolean | No | Include sentiment per theme (default: true) |

---

### 18.3 Predictive Anomaly Detection (T-M2-04)

**Base path:** `/form/api/v1/ai/forms/<form_id>`

#### 18.3.1 Detect Anomalies

Run anomaly detection on form responses to identify spam, outliers, duplicates, and impossible values.

* **Endpoint:** `/detect-anomalies`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `scan_type` | string | No | "full" or "incremental" (default: "full") |
| `response_ids` | array | No | Specific response IDs to scan (defaults to all) |
| `detection_types` | array | No | Types: ["spam", "outlier", "impossible_value", "duplicate"] |
| `sensitivity` | string | No | "low", "medium", or "high" (default: "medium") |
| `save_results` | boolean | No | Save results to database (default: false) |

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "scan_type": "full",
  "responses_scanned": 250,
  "anomalies_detected": 12,
  "scan_duration_ms": 850,
  "baseline": {
    "avg_response_length": 150,
    "std_response_length": 45,
    "avg_sentiment_score": 0.3,
    "std_sentiment_score": 1.2
  },
  "anomalies": [
    {
      "response_id": "resp_789",
      "overall_score": 75,
      "severity": "high",
      "flags": [
        {
          "type": "spam",
          "confidence": 0.85,
          "description": "Spam patterns detected",
          "details": {
            "spam_score": 75,
            "indicators": [
              {"name": "spam_keyword", "description": "Contains spam keywords", "weight": 30},
              {"name": "fast_submission", "description": "Submitted in under 2 seconds", "weight": 25}
            ]
          }
        }
      ]
    }
  ],
  "summary_by_type": {
    "spam": 5,
    "outlier": 3,
    "duplicate": 2,
    "impossible_value": 1,
    "pattern": 1
  }
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/detect-anomalies \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_type": "full",
    "detection_types": ["spam", "outlier", "duplicate"],
    "sensitivity": "medium"
  }'
```

**Service Layer:** `app/services/anomaly_detection_service.py` - `AnomalyDetectionService.run_full_detection()`, `AnomalyDetectionService.detect_spam()`, `AnomalyDetectionService.detect_outliers()`

---

#### 18.3.2 Get Anomaly Details

Get detailed anomaly information for a specific response.

* **Endpoint:** `/anomalies/<response_id>`
* **Method:** `GET`
* **Auth Required:** Yes

**Response Schema (Success):**

```json
{
  "response_id": "resp_789",
  "anomaly_flags": {
    "spam": {
      "score": 75,
      "indicators": [
        {
          "name": "spam_keyword",
          "description": "Contains spam keywords",
          "weight": 20
        },
        {
          "name": "fast_submission",
          "description": "Submitted in under 2 seconds",
          "weight": 25
        }
      ],
      "confidence": 0.85
    },
    "duplicate": null,
    "outlier": null
  },
  "response_data": {...},
  "review_status": "pending",
  "suggested_actions": ["review", "flag_response", "ignore"]
}
```

---

#### 18.3.3 Anomaly Statistics

Get anomaly detection statistics for a form.

* **Endpoint:** `/anomaly-stats`
* **Method:** `GET`
* **Auth Required:** Yes

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "total_responses": 250,
  "flagged_count": 12,
  "flagged_percentage": 4.8,
  "reviewed_count": 8,
  "false_positive_rate": 0.15,
  "detection_accuracy": 0.92,
  "recent_scans": [
    {
      "scan_date": "2026-02-04",
      "anomalies_found": 3,
      "false_positives": 0
    }
  ]
}
```

---

#### 18.3.4 Submit Anomaly Feedback

Submit feedback on anomaly detection results to improve accuracy.

* **Endpoint:** `/anomalies/<response_id>/feedback`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `feedback_type` | string | Yes | "false_positive" or "correct" |
| `comment` | string | No | Optional comment |

**Response Schema (Success):**

```json
{
  "message": "Feedback recorded successfully",
  "feedback_id": "fb_123",
  "model_improvement": "This feedback will help improve future detection accuracy"
}
```

---

### 18.4 AI Health Check

Check the health status of AI services including Ollama availability.

* **Endpoint:** `/health`
* **Method:** `GET`
* **Auth Required:** No

**Response Schema (Success):**

```json
{
  "status": "healthy",
  "ollama": {
    "status": "healthy",
    "available": true,
    "models": ["llama3.2", "nomic-embed-text"],
    "default_model": "llama3.2",
    "embedding_model": "nomic-embed-text"
  },
  "timestamp": "2026-02-04T10:00:00Z"
}
```

---

## 19. Ollama Integration

**Configuration:**

Add these to your environment or config:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OLLAMA_API_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Default chat model | `llama3.2` |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model for semantic search | `nomic-embed-text` |

**Requirements:**
- Ollama must be running with models pulled
- For semantic search: `ollama pull nomic-embed-text`
- For summarization: `ollama pull llama3.2`

**Rate Limiting:**
- No explicit rate limiting at application level
- Ollama server may have its own limits
- Semantic search results are cached for 1 hour
