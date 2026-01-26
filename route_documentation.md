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
