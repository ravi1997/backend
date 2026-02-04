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

## 9. User Dashboard Settings Service

**Base path:** `/api/v1/dashboard`

User-specific dashboard customization settings. Allows users to customize their dashboard layout, widgets, theme, language, and timezone preferences.

### 9.1 Get Dashboard Settings

Retrieve the authenticated user's dashboard customization settings. If no settings exist, default settings are created and returned.

* **Endpoint:** `/settings`
* **Method:** `GET`
* **Auth Required:** Yes (JWT)

**Response Example:**

```json
{
  "success": true,
  "settings": {
    "id": "...",
    "user_id": "...",
    "layout": {
      "columns": 3,
      "rowHeight": 100,
      "margin": [10, 10],
      "compactType": "vertical",
      "positions": {}
    },
    "widgets": [...],
    "theme": "system",
    "language": "en",
    "timezone": "UTC",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### 9.2 Update Dashboard Settings

Update the authenticated user's dashboard customization settings. All fields are optional.

* **Endpoint:** `/settings`
* **Method:** `PUT`
* **Auth Required:** Yes (JWT)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `layout` | object | No | Layout configuration (columns, rowHeight, margin, compactType, positions) |
| `widgets` | array | No | Array of widget objects with id, type, position, size, config |
| `theme` | string | No | Theme preference: `light`, `dark`, or `system` |
| `language` | string | No | Language preference (e.g., `en`, `es`) |
| `timezone` | string | No | Timezone preference (e.g., `UTC`, `America/New_York`) |

**Request Example:**

```bash
curl -X PUT http://localhost:5000/api/v1/dashboard/settings \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark",
    "language": "en",
    "layout": {
      "columns": 4,
      "rowHeight": 120
    }
  }'
```

---

### 9.3 Reset Dashboard Settings

Reset the authenticated user's dashboard settings to default values.

* **Endpoint:** `/reset`
* **Method:** `POST`
* **Auth Required:** Yes (JWT)

**Response:** Returns the reset default settings.

---

### 9.4 Get Available Widgets

Get list of available widget types that can be added to the dashboard.

* **Endpoint:** `/widgets`
* **Method:** `GET`
* **Auth Required:** Yes (JWT)

**Response Example:**

```json
{
  "success": true,
  "widgets": [
    {
      "id": "form_statistics",
      "name": "Form Statistics",
      "description": "Display statistics about your forms",
      "icon": "📊",
      "default_size": {"w": 2, "h": 2},
      "config_schema": {
        "forms_to_show": {"type": "number", "default": 5},
        "show_submission_count": {"type": "boolean", "default": true}
      }
    },
    {
      "id": "recent_responses",
      "name": "Recent Responses",
      "description": "Show recent form responses",
      "icon": "📋",
      "default_size": {"w": 2, "h": 3}
    },
    {
      "id": "quick_actions",
      "name": "Quick Actions",
      "description": "Quick access to common actions",
      "icon": "⚡",
      "default_size": {"w": 1, "h": 2}
    },
    {
      "id": "notifications",
      "name": "Notifications",
      "description": "Show recent notifications",
      "icon": "🔔",
      "default_size": {"w": 1, "h": 2}
    },
    {
      "id": "charts",
      "name": "Charts",
      "description": "Display charts and analytics",
      "icon": "📈",
      "default_size": {"w": 2, "h": 2}
    }
  ]
}
```

---

### 9.5 Add Widget

Add a widget to the user's dashboard.

* **Endpoint:** `/widgets`
* **Method:** `POST`
* **Auth Required:** Yes (JWT)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `type` | string | Yes | Widget type ID (e.g., `form_statistics`, `recent_responses`) |
| `position` | object | No | Position `{x, y}` |
| `size` | object | No | Size `{w, h}` |
| `config` | object | No | Widget-specific configuration |

**Request Example:**

```bash
curl -X POST http://localhost:5000/api/v1/dashboard/widgets \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "charts",
    "position": {"x": 0, "y": 6},
    "size": {"w": 2, "h": 2}
  }'
```

---

### 9.6 Update Widget

Update a widget's configuration.

* **Endpoint:** `/widgets/<widget_id>`
* **Method:** `PUT`
* **Auth Required:** Yes (JWT)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `position` | object | No | New position `{x, y}` |
| `size` | object | No | New size `{w, h}` |
| `config` | object | No | Configuration updates |
| `is_visible` | boolean | No | Visibility status |

---

### 9.7 Remove Widget

Remove a widget from the user's dashboard.

* **Endpoint:** `/widgets/<widget_id>`
* **Method:** `DELETE`
* **Auth Required:** Yes (JWT)

**Response:** `200 OK` on success, `404 Not Found` if widget doesn't exist.

---

### 9.8 Update Widget Positions

Update positions for multiple widgets (used for drag-and-drop reordering).

* **Endpoint:** `/widgets/positions`
* **Method:** `PUT`
* **Auth Required:** Yes (JWT)

**Input Schema:**

```json
{
  "positions": {
    "widget_id_1": {"x": 0, "y": 0},
    "widget_id_2": {"x": 2, "y": 0}
  }
}
```

---

### 9.9 Update Layout

Update only the layout configuration.

* **Endpoint:** `/layout`
* **Method:** `PUT`
* **Auth Required:** Yes (JWT)

**Input Schema:**

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `columns` | number | Number of grid columns |
| `rowHeight` | number | Height of each row in pixels |
| `margin` | array | Margin `[x, y]` between widgets |
| `compactType` | string | Layout compaction type: `vertical`, `horizontal`, or `null` |
| `positions` | object | Widget positions mapping |

---

### 9.10 Widget Types Reference

| Widget Type | Description | Default Size |
| :--- | :--- | :--- |
| `form_statistics` | Display statistics about forms | 2x2 |
| `recent_responses` | Show recent form responses | 2x3 |
| `quick_actions` | Quick access to common actions | 1x2 |
| `notifications` | Show recent notifications | 1x2 |
| `charts` | Display charts and analytics | 2x2 |
| `analytics_overview` | Overview of key analytics metrics | 2x1 |
| `workflow_status` | Show status of active workflows | 1x2 |
| `calendar` | Calendar view for scheduled forms | 2x3 |

---

## 10. Workflow Service

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

* Requires Ollama service running for semantic search and LLM features
* Fallback to keyword-based search if Ollama unavailable

---

#### 18.0.1 Ollama Fallback Model Support (M2-EXT-01b)

**Overview:**

The OllamaService now supports automatic fallback to backup models when the primary model fails. This improves reliability by ensuring AI operations continue even when the default model is unavailable or experiencing issues.

**Fallback Behavior:**

1. **Primary Model First:** The service attempts to use the configured primary model (default: `llama3.2`)
2. **Automatic Fallback:** If the primary model fails, the service automatically tries each fallback model in sequence
3. **Response Metadata:** All responses include metadata indicating which model was used and whether fallback was activated
4. **Logging:** Detailed logging tracks which model succeeded and any failures encountered

**Configuration:**

The `OllamaService` class includes a default fallback model list:

```python
FALLBACK_MODELS = ["llama3.1", "mistral:7b", "gemma:2b"]
```

**Service Methods:**

* `OllamaService.chat_with_fallback()` - Primary method for chat with automatic fallback
* `OllamaService.chat()` - Standard chat method (supports optional fallback_models parameter)

**Request Parameters:**

All AI endpoints now support an optional `fallback_models` parameter in the request body:

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `fallback_models` | array | No | List of model names to try if primary fails (overrides default) |

**Example Request with Custom Fallbacks:**

```json
{
  "query": "Analyze customer feedback",
  "options": {
    "fallback_models": ["llama3.1", "mistral:7b", "gemma:2b"]
  }
}
```

**Response Metadata:**

When fallback is used, the response includes:

```json
{
  "response": "...",
  "model": "llama3.1",
  "timing_ms": 1250,
  "fallback_used": true,
  "fallback_model": "llama3.1"
}
```

**Endpoints Supporting Fallback:**

* `/form/api/v1/ai/forms/<form_id>/nlp-search` - Natural language search
* `/form/api/v1/ai/forms/<form_id>/semantic-search` - Semantic search
* `/form/api/v1/ai/forms/<form_id>/summarize` - Response summarization
* `/form/api/v1/ai/forms/<form_id>/summarize/stream` - Streaming response summarization
* `/form/api/v1/ai/forms/<form_id>/executive-summary` - Executive summary
* `/form/api/v1/ai/forms/<form_id>/theme-summary` - Theme-based summary
* `/form/api/v1/ai/forms/<form_id>/summary-comparison` - Summary comparison across periods
* `/form/api/v1/ai/forms/<form_id>/summary-trends` - Trend analysis over time
* `/form/api/v1/ai/forms/<form_id>/summary-snapshots` - List summary snapshots

**Error Handling:**

If all models (primary + fallbacks) fail, the service raises a `ConnectionError` with details about which models were attempted.

**Logging:**

The service logs:

* Success: `"Ollama chat: Successfully used primary model 'llama3.2'"`
* Fallback success: `"Ollama chat: Successfully used fallback model 'llama3.1' after primary failure"`
* Failure: `"Ollama chat: Primary model 'llama3.2' failed: <error>"`

**Service Layer:** `app/services/ollama_service.py` - `OllamaService.chat_with_fallback()`, `OllamaService.FALLBACK_MODELS`

---

#### 18.0.2 Streaming Response Support (M2-EXT-01c)

**Overview:**

The AI services now support streaming responses for large LLM outputs. This improves user experience by showing responses as they're generated rather than waiting for the complete response.

**Streaming Format:**

Streaming endpoints use Server-Sent Events (SSE) format with `text/event-stream` content type. Each chunk is sent as a separate event with the following structure:

**Chunk Format (In Progress):**

```
data: { "content": "partial text", "done": false }
```

**Final Chunk Format:**

```
data: { "content": "", "done": true, "model_used": "llama3.2", "results_count": 8 }
```

**Response Headers:**

Streaming endpoints include the following headers:

| Header | Value | Description |
| :--- | :--- | :--- |
| `Content-Type` | `text/event-stream` | SSE content type |
| `Cache-Control` | `no-cache` | Disable caching for streaming |
| `X-Accel-Buffering` | `no` | Disable nginx buffering |
| `Connection` | `keep-alive` | Keep connection open |

**Service Methods:**

The `OllamaService` class provides the following streaming methods:

* `OllamaService.chat_stream()` - Stream chat responses from a single model
* `OllamaService.chat_stream_with_fallback()` - Stream with automatic fallback to backup models
* `OllamaService.chat()` - Enhanced to support `stream=True` parameter (returns generator)

**Streaming with Fallback:**

The `chat_stream_with_fallback()` method provides automatic fallback support for streaming:

1. **Primary Model First:** Attempts to stream from the primary model
2. **Automatic Fallback:** If the primary model fails, tries each fallback model in sequence
3. **Metadata Tracking:** Final chunk includes `fallback_used` and `fallback_model` keys
4. **Error Handling:** Raises `ConnectionError` if all models fail

**Example Client Usage (JavaScript):**

```javascript
const eventSource = new EventSource(
  'http://localhost:5000/form/api/v1/ai/forms/123/semantic-search/stream',
  {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer <token>',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: "What are the main complaints?",
      max_results: 20
    })
  }
);

let fullContent = '';
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (!data.done) {
    fullContent += data.content;
    // Update UI with partial content
    console.log('Partial:', data.content);
  } else {
    // Streaming complete
    console.log('Final:', data.model_used);
    console.log('Results:', data.results_count);
    eventSource.close();
  }
};

eventSource.onerror = (error) => {
  console.error('Stream error:', error);
  eventSource.close();
};
```

**Example Client Usage (Python with requests):**

```python
import requests
import json

response = requests.post(
    'http://localhost:5000/form/api/v1/ai/forms/123/summarize/stream',
    headers={
        'Authorization': 'Bearer <token>',
        'Content-Type': 'application/json'
    },
    json={
        'strategy': 'hybrid',
        'format': 'bullet_points'
    },
    stream=True
)

full_content = ''
for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8').replace('data: ', ''))
        if not data.get('done'):
            full_content += data.get('content', '')
            print(f"Partial: {data.get('content', '')}")
        else:
            print(f"Complete! Model: {data.get('model_used')}")
            print(f"Responses analyzed: {data.get('responses_analyzed')}")
```

**Streaming Endpoints:**

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/semantic-search/stream` | POST | Stream semantic search results |
| `/summarize/stream` | POST | Stream response summarization |

**Request Parameters (Same as non-streaming):**

All streaming endpoints accept the same parameters as their non-streaming counterparts:

* **Semantic Search Stream:** Same as `/semantic-search`
* **Summarize Stream:** Same as `/summarize`

**Response Metadata (Final Chunk):**

The final chunk includes additional metadata:

| Field | Type | Description |
| :--- | :--- | :--- |
| `done` | boolean | Always `true` for final chunk |
| `model_used` | string | Model that generated the response |
| `fallback_used` | boolean | Whether fallback was activated (summarization only) |
| `fallback_model` | string | Fallback model used (if applicable) |
| `results_count` | integer | Number of results (semantic search) |
| `responses_analyzed` | integer | Number of responses processed (summarization) |
| `processing_time_ms` | integer | Total processing time (summarization) |

**Error Handling in Streams:**

If an error occurs during streaming, the final chunk will include error information:

```json
{
  "content": "",
  "done": true,
  "error": "Ollama service is not available",
  "message": "Ensure Ollama is running with embedding support"
}
```

**Service Layer:** `app/services/ollama_service.py` - `OllamaService.chat_stream()`, `OllamaService.chat_stream_with_fallback()`

---

### 18.1 NLP Search Enhancement (T-M2-02)

**Base path:** `/form/api/v1/ai/forms/<form_id>`

#### 18.1.1 Natural Language Search

Search form responses using natural language queries. Supports sentiment filtering, topic extraction, semantic search, and advanced filtering (date range, field-specific).

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
| `options.nocache` | boolean | No | Bypass cache and invalidate for this query (default: false) |
| `options.fallback_models` | array | No | List of model names to try if primary fails (default: ["llama3.1", "mistral:7b", "gemma:2b"]) |
| `filters.date_range.start_date` | string | No | ISO format start date (e.g., "2025-01-01T00:00:00Z") |
| `filters.date_range.end_date` | string | No | ISO format end date (e.g., "2025-03-31T23:59:59Z") |
| `filters.field_filters` | array | No | List of field filter objects |
| `filters.field_filters[].field` | string | Yes | Field name to filter on |
| `filters.field_filters[].operator` | string | Yes | Operator: ">", ">=", "<", "<=", "=", "contains" |
| `filters.field_filters[].value` | string | Yes | Value to filter by |
| `filters.submitted_by` | array | No | List of user IDs to filter by |
| `filters.source` | array | No | List of sources to filter by (e.g., ["web", "mobile"]) |
| `filter_mode` | string | No | Filter combination mode: "and" (all must match) or "or" (any can match) (default: "and") |

**Natural Language Date Parsing:**

The query parser automatically extracts date ranges from natural language:

| Expression | Meaning |
| :--- | :--- |
| "last 7 days" | Responses from the past 7 days |
| "past 2 weeks" | Responses from the past 2 weeks |
| "last month" | Responses from the previous month |
| "today" | Responses submitted today |
| "yesterday" | Responses submitted yesterday |
| "this week" | Responses from this week |
| "2025-01 to 2025-03" | Responses between January and March 2025 |
| "from 2025-01-01 to 2025-03-31" | Responses between specified dates |
| "after 2025-01-01" | Responses after specified date |
| "before 2025-03-31" | Responses before specified date |

**Natural Language Field Filtering:**

The query parser automatically extracts field filters from natural language:

| Expression | Meaning |
| :--- | :--- |
| "q_satisfaction: positive" | Contains "positive" in q_satisfaction field |
| "q_rating > 3" | q_rating greater than 3 |
| "q_rating >= 4" | q_rating greater than or equal to 4 |
| "q_rating < 5" | q_rating less than 5 |
| "q_rating <= 3" | q_rating less than or equal to 3 |
| "q_status = approved" | q_status equals "approved" |
| "q_name contains John" | q_name contains "John" |

**Response Schema (Success):**

```json
{
  "query": "Show me all users who were unhappy with delivery last 7 days",
  "parsed_intent": {
    "original_query": "Show me all users who were unhappy with delivery last 7 days",
    "search_query": "users delivery",
    "sentiment_filter": "negative",
    "topic": "delivery",
    "entities": ["delivery", "users"],
    "date_range": {
      "start_date": "2025-01-28T00:00:00Z",
      "end_date": "2025-02-04T00:00:00Z",
      "expression": "last 7 days"
    },
    "field_filters": [],
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
  "cached": false,
  "filters_applied": {
    "date_range": {
      "start_date": "2025-01-28T00:00:00Z",
      "end_date": "2025-02-04T00:00:00Z"
    }
  },
  "filter_mode": "and"
}
```

**Example Request with Filters:**

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
    },
    "filters": {
      "date_range": {
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-03-31T23:59:59Z"
      },
      "field_filters": [
        {"field": "q_rating", "operator": "<", "value": "3"},
        {"field": "q_satisfaction", "operator": "contains", "value": "positive"}
      ],
      "submitted_by": ["user1", "user2"],
      "source": ["web", "mobile"]
    },
    "filter_mode": "and"
  }'
```

**Example Request with Natural Language Filters:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/nlp-search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all users who were unhappy with delivery last 7 days q_rating > 3",
    "options": {
      "max_results": 50,
      "semantic_search": true
    }
  }'
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.parse_query()`, `NLPSearchService.semantic_search()`, `NLPSearchService.filter_by_criteria()`

---

#### 18.1.2 Semantic Search

Pure semantic search using Ollama embeddings for similarity matching with advanced filtering capabilities.

* **Endpoint:** `/semantic-search`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | string | Yes | Search query text |
| `options.nocache` | boolean | No | Bypass cache and invalidate for this query (default: false) |
| `options.fallback_models` | array | No | List of model names to try if primary fails (default: ["llama3.1", "mistral:7b", "gemma:2b"]) |
| `query` | string | Yes | Search query for semantic matching |
| `similarity_threshold` | float | No | Minimum similarity score 0-1 (default: 0.7) |
| `max_results` | integer | No | Maximum results to return (default: 20) |
| `fallback_models` | array | No | List of model names to try if primary fails (default: ["llama3.1", "mistral:7b", "gemma:2b"]) |
| `date_range.start_date` | string | No | ISO format start date (e.g., "2025-01-01T00:00:00Z") |
| `date_range.end_date` | string | No | ISO format end date (e.g., "2025-03-31T23:59:59Z") |
| `field_filters` | array | No | List of field filter objects |
| `field_filters[].field` | string | Yes | Field name to filter on |
| `field_filters[].operator` | string | Yes | Operator: ">", ">=", "<", "<=", "=", "contains" |
| `field_filters[].value` | string | Yes | Value to filter by |
| `submitted_by` | array | No | List of user IDs to filter by |
| `source` | array | No | List of sources to filter by (e.g., ["web", "mobile"]) |
| `filter_mode` | string | No | Filter combination mode: "and" (all must match) or "or" (any can match) (default: "and") |

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
  ],
  "filters_applied": {
    "date_range": {
      "start_date": "2025-01-01T00:00:00Z",
      "end_date": "2025-03-31T23:59:59Z"
    },
    "field_filters": [
      {"field": "q_rating", "operator": "<", "value": "3"}
    ]
  },
  "filter_mode": "and"
}
```

**Example Request with Date Range Filter:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/semantic-search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main complaints about product quality?",
    "similarity_threshold": 0.7,
    "max_results": 20,
    "date_range": {
      "start_date": "2025-01-01T00:00:00Z",
      "end_date": "2025-03-31T23:59:59Z"
    }
  }'
```

**Example Request with Field Filters:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/semantic-search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main complaints about product quality?",
    "similarity_threshold": 0.7,
    "max_results": 20,
    "field_filters": [
      {"field": "q_rating", "operator": "<", "value": "3"},
      {"field": "q_satisfaction", "operator": "contains", "value": "poor"}
    ],
    "filter_mode": "and"
  }'
```

**Example Request with Multiple Filters:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/semantic-search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main complaints about product quality?",
    "similarity_threshold": 0.7,
    "max_results": 20,
    "date_range": {
      "start_date": "2025-01-01T00:00:00Z",
      "end_date": "2025-03-31T23:59:59Z"
    },
    "field_filters": [
      {"field": "q_rating", "operator": "<", "value": "3"}
    ],
    "submitted_by": ["user1", "user2"],
    "source": ["web"],
    "filter_mode": "and"
  }'
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.semantic_search()`, `NLPSearchService.filter_by_criteria()`, `app/services/ollama_service.py` - `OllamaService.generate_embedding()`

---

#### 18.1.5 Advanced Filtering (M2-EXT-02c)

Advanced filtering capabilities for NLP search, supporting date ranges, field-specific filters, and metadata filtering.

**Features:**

* **Date Range Filtering**: Filter responses by submission date using natural language or ISO format dates
* **Field-Specific Filtering**: Filter by form fields with operators (>, <, =, contains)
* **Metadata Filtering**: Filter by submitted_by user IDs and source
* **Filter Combination**: Combine filters using "and" or "or" logic
* **Natural Language Parsing**: Extract filters directly from query text

**Date Range Expressions:**

| Expression | Description | Example |
| :--- | :--- | :--- |
| `last N days` | Responses from past N days | "last 7 days" |
| `past N days` | Same as last N days | "past 30 days" |
| `previous N days` | Same as last N days | "previous 14 days" |
| `today` | Responses submitted today | "today" |
| `yesterday` | Responses submitted yesterday | "yesterday" |
| `this week` | Responses from this week | "this week" |
| `last week` | Responses from last week | "last week" |
| `this month` | Responses from this month | "this month" |
| `last month` | Responses from last month | "last month" |
| `this year` | Responses from this year | "this year" |
| `last year` | Responses from last year | "last year" |
| `YYYY-MM to YYYY-MM` | Responses between months | "2025-01 to 2025-03" |
| `YYYY-MM-DD to YYYY-MM-DD` | Responses between dates | "2025-01-01 to 2025-03-31" |
| `from YYYY-MM-DD to YYYY-MM-DD` | Responses between dates | "from 2025-01-01 to 2025-03-31" |
| `between YYYY-MM-DD and YYYY-MM-DD` | Responses between dates | "between 2025-01-01 and 2025-03-31" |
| `after YYYY-MM-DD` | Responses after date | "after 2025-01-01" |
| `before YYYY-MM-DD` | Responses before date | "before 2025-03-31" |
| `since YYYY-MM-DD` | Responses since date | "since 2025-01-01" |
| `until YYYY-MM-DD` | Responses until date | "until 2025-03-31" |

**Field Filter Operators:**

| Operator | Description | Example |
| :--- | :--- | :--- |
| `:` | Contains (case-insensitive) | "q_satisfaction: positive" |
| `>` | Greater than (numeric) | "q_rating > 3" |
| `>=` | Greater than or equal (numeric) | "q_rating >= 4" |
| `<` | Less than (numeric) | "q_rating < 5" |
| `<=` | Less than or equal (numeric) | "q_rating <= 3" |
| `=` | Equals (exact match) | "q_status = approved" |
| `contains` | Contains (explicit) | "q_name contains John" |

**Filter Mode:**

| Mode | Description |
| :--- | :--- |
| `and` | All filters must match (default) |
| `or` | Any filter can match |

**Service Methods:**

| Method | Description |
| :--- | :--- |
| `NLPSearchService._parse_date_range(query)` | Parse date range from natural language query |
| `NLPSearchService._extract_field_filters(query)` | Extract field filters from natural language query |
| `NLPSearchService.filter_by_criteria(docs, filters, mode)` | Apply filters to documents |
| `NLPSearchService.validate_date_range(date_range)` | Validate date range format |
| `NLPSearchService.validate_field_names(filters, schema)` | Validate field names against form schema |

**Example: Combined Natural Language Query**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/nlp-search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me unhappy users with delivery issues last 7 days q_rating > 3",
    "options": {
      "max_results": 50,
      "semantic_search": true
    }
  }'
```

This query will:

1. Parse sentiment filter: "negative" (from "unhappy")
2. Parse topic: "delivery"
3. Parse date range: last 7 days
4. Parse field filter: q_rating > 3
5. Combine all filters with "and" mode
6. Perform semantic search on filtered results

**Example: Explicit Filters**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/nlp-search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "delivery issues",
    "filters": {
      "date_range": {
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-03-31T23:59:59Z"
      },
      "field_filters": [
        {"field": "q_rating", "operator": "<", "value": "3"},
        {"field": "q_satisfaction", "operator": "contains", "value": "poor"}
      ],
      "submitted_by": ["user1", "user2"],
      "source": ["web"]
    },
    "filter_mode": "and"
  }'
```

**Task Reference:** M2-EXT-02c - Add advanced filters (date range, field-specific)

---

#### 18.1.2b Semantic Search (Streaming)

Pure semantic search using Ollama embeddings with streaming response for real-time feedback and advanced filtering capabilities.

* **Endpoint:** `/semantic-search/stream`
* **Method:** `POST`
* **Auth Required:** Yes
* **Content-Type:** `text/event-stream`

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | string | Yes | Search query for semantic matching |
| `similarity_threshold` | float | No | Minimum similarity score 0-1 (default: 0.7) |
| `max_results` | integer | No | Maximum results to return (default: 20) |
| `fallback_models` | array | No | List of model names to try if primary fails (default: ["llama3.1", "mistral:7b", "gemma:2b"]) |
| `date_range.start_date` | string | No | ISO format start date (e.g., "2025-01-01T00:00:00Z") |
| `date_range.end_date` | string | No | ISO format end date (e.g., "2025-03-31T23:59:59Z") |
| `field_filters` | array | No | List of field filter objects |
| `field_filters[].field` | string | Yes | Field name to filter on |
| `field_filters[].operator` | string | Yes | Operator: ">", ">=", "<", "<=", "=", "contains" |
| `field_filters[].value` | string | Yes | Value to filter by |
| `submitted_by` | array | No | List of user IDs to filter by |
| `source` | array | No | List of sources to filter by (e.g., ["web", "mobile"]) |
| `filter_mode` | string | No | Filter combination mode: "and" (all must match) or "or" (any can match) (default: "and") |

**Stream Format:**

The endpoint sends Server-Sent Events (SSE) with the following structure:

**Status Updates:**

```
data: { "content": "Fetching documents...", "done": false, "stage": "fetching" }
data: { "content": "Found 500 documents. Performing semantic search...", "done": false, "stage": "searching" }
```

**Results (Final Chunk):**

```
data: { "content": "{\"query\": \"...\", \"embedding_model\": \"...\", \"results_count\": 8, \"results\": [...], \"filters_applied\": {...}, \"filter_mode\": \"and\"}", "done": true, "model_used": "nomic-embed-text", "results_count": 8 }
```

**Example Request with Filters:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/semantic-search/stream \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main complaints about product quality?",
    "similarity_threshold": 0.7,
    "max_results": 20,
    "date_range": {
      "start_date": "2025-01-01T00:00:00Z",
      "end_date": "2025-03-31T23:59:59Z"
    },
    "field_filters": [
      {"field": "q_rating", "operator": "<", "value": "3"}
    ],
    "filter_mode": "and"
  }'
```

**Example Response Stream:**

```
data: {"content": "Fetching documents...", "done": false, "stage": "fetching"}

data: {"content": "Found 500 documents. Performing semantic search...", "done": false, "stage": "searching"}

data: {"content": "{\"query\": \"What are the main complaints about product quality?\", \"embedding_model\": \"nomic-embed-text\", \"results_count\": 8, \"results\": [{\"response_id\": \"resp_456\", \"data\": {...}, \"similarity_score\": 0.85}], \"filters_applied\": {\"date_range\": {...}, \"field_filters\": [...]}, \"filter_mode\": \"and\"}", "done": true, "model_used": "nomic-embed-text", "results_count": 8}
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.semantic_search()`, `NLPSearchService.filter_by_criteria()`, `app/services/ollama_service.py` - `OllamaService.generate_embedding()`

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

#### 18.1.4 Query Suggestions / Autocomplete

Get intelligent query suggestions based on partial input. Helps users discover what they can search for by suggesting relevant terms from existing responses and form structure.

* **Endpoint:** `/query-suggestions`
* **Method:** `GET`
* **Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `q` | string | Yes | Partial query string to match against |
| `limit` | integer | No | Maximum number of suggestions (default: 10, max: 50) |

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "query": "del",
  "suggestions": [
    {
      "text": "delivery",
      "count": 98,
      "match_score": 0.92,
      "is_form_term": false
    },
    {
      "text": "delivered",
      "count": 45,
      "match_score": 0.88,
      "is_form_term": false
    },
    {
      "text": "delay",
      "count": 23,
      "match_score": 0.75,
      "is_form_term": true
    }
  ],
  "total_suggestions": 3
}
```

**Example Request:**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/form_123/query-suggestions?q=del&limit=5" \
  -H "Authorization: Bearer <token>"
```

**Suggestion Sources:**

1. **Existing Response Data:** Extracts most common terms from up to 500 recent responses
2. **Form Structure:** Extracts terms from question labels, field names, and option labels

**Fuzzy Matching Logic:**

* **Prefix Match:** High priority for terms starting with the query
* **Contains Match:** Medium priority for terms containing the query
* **Character Overlap:** Calculates similarity based on common character sequences
* **Scoring Factors:**
  * Match score (50% weight)
  * Term frequency (30% weight)
  * Recency (10% weight)
  * Form term bonus (10% weight)

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.get_query_suggestions()`, `NLPSearchService._fuzzy_match_score()`

---

#### 18.1.5 Search History (M2-EXT-02b)

Persist user search queries for analytics and personalization. Enables showing recent searches and tracking popular queries.

**Base path:** `/form/api/v1/ai/forms/<form_id>/search-history`

##### 18.1.5.1 Get Search History

Retrieve recent searches for a user for a specific form.

* **Endpoint:** `/search-history`
* **Method:** `GET`
* **Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `limit` | integer | No | Maximum number of results (default: 50, max: 100) |
| `offset` | integer | No | Number of results to skip (default: 0) |

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "user_id": "user_456",
  "history": [
    {
      "id": "search_789",
      "query": "delivery issues",
      "timestamp": "2024-01-15T10:30:00Z",
      "results_count": 15,
      "form_id": "form_123",
      "search_type": "nlp",
      "cached": false,
      "parsed_intent": {
        "sentiment_filter": "negative",
        "topic": "delivery"
      }
    }
  ],
  "total": 50,
  "limit": 50,
  "offset": 0
}
```

**Example Request:**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/form_123/search-history?limit=20&offset=0" \
  -H "Authorization: Bearer <token>"
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.get_user_search_history()`

---

##### 18.1.5.2 Save Search History

Explicitly save a search query to user's search history. (Note: Searches are automatically saved when using the NLP search endpoints)

* **Endpoint:** `/search-history`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | string | Yes | Search query text |
| `results_count` | integer | No | Number of results returned (default: 0) |
| `parsed_intent` | object | No | Parsed query details (optional) |
| `search_type` | string | No | Type of search: 'nlp', 'semantic', 'keyword' (default: 'nlp') |
| `cached` | boolean | No | Whether result was from cache (default: false) |

**Response Schema (Success):**

```json
{
  "id": "search_789",
  "query": "delivery issues",
  "timestamp": "2024-01-15T10:30:00Z",
  "message": "Search saved successfully"
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/form_123/search-history \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "delivery issues",
    "results_count": 15,
    "search_type": "nlp",
    "cached": false
  }'
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.save_search()`

---

##### 18.1.5.3 Clear Search History

Clear user's search history for a form or all forms.

* **Endpoint:** `/search-history`
* **Method:** `DELETE`
* **Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `all` | string | No | If "true", clears all search history (not just for this form) |

**Response Schema (Success):**

```json
{
  "deleted_count": 15,
  "message": "15 search record(s) cleared successfully"
}
```

**Example Request (Clear form-specific history):**

```bash
curl -X DELETE http://localhost:5000/form/api/v1/ai/forms/form_123/search-history \
  -H "Authorization: Bearer <token>"
```

**Example Request (Clear all history):**

```bash
curl -X DELETE "http://localhost:5000/form/api/v1/ai/forms/form_123/search-history?all=true" \
  -H "Authorization: Bearer <token>"
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.clear_user_search_history()`

---

##### 18.1.5.4 Delete Specific Search History Item

Delete a specific search history item by ID.

* **Endpoint:** `/search-history/<search_id>`
* **Method:** `DELETE`
* **Auth Required:** Yes

**Response Schema (Success):**

```json
{
  "deleted_count": 1,
  "message": "Search record deleted successfully"
}
```

**Example Request:**

```bash
curl -X DELETE http://localhost:5000/form/api/v1/ai/forms/form_123/search-history/search_789 \
  -H "Authorization: Bearer <token>"
```

---

##### 18.1.5.5 Get Popular Queries

Get popular search queries for a form. Uses caching (1 hour TTL) for performance.

* **Endpoint:** `/popular-queries`
* **Method:** `GET`
* **Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `limit` | integer | No | Maximum number of results (default: 10, max: 50) |
| `nocache` | string | No | If "true", bypasses cache and fetches fresh data |

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "popular_queries": [
    {
      "query": "delivery issues",
      "count": 45
    },
    {
      "query": "product quality",
      "count": 32
    },
    {
      "query": "customer support",
      "count": 28
    }
  ],
  "cached": true
}
```

**Example Request:**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/form_123/popular-queries?limit=10" \
  -H "Authorization: Bearer <token>"
```

**Example Request (Bypass Cache):**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/form_123/popular-queries?limit=10&nocache=true" \
  -H "Authorization: Bearer <token>"
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.get_popular_queries_cached()`

**Cache TTL:** 1 hour (3600 seconds)

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
| `max_points` | integer | No | Override default max bullet points (3-10, default: 5) |
| `detail_level` | string | No | Detail level: "brief" (3 points, no examples), "standard" (5 points, 2 examples), "detailed" (10 points, 5 examples) |
| `include_examples` | boolean | No | Whether to include example quotes (default: true) |
| `nocache` | boolean | No | Bypass cache and invalidate for this form (default: false) |
| `config.max_points` | integer | No | Maximum bullet points (default: 5) - DEPRECATED, use `max_points` instead |
| `config.focus_area` | string | No | Focus area filter: "all", "sentiment", "topics" |
| `config.include_sentiment` | boolean | No | Include sentiment analysis (default: true) |
| `config.include_quotes` | boolean | No | Include supporting quotes (default: true) |
| `fallback_models` | array | No | List of model names to try if primary fails (default: ["llama3.1", "mistral:7b", "gemma:2b"]) |

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

#### 18.2.1b Generate Summary (Streaming)

Automatically summarize form responses with streaming response for real-time feedback.

* **Endpoint:** `/summarize/stream`
* **Method:** `POST`
* **Auth Required:** Yes
* **Content-Type:** `text/event-stream`

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
| `fallback_models` | array | No | List of model names to try if primary fails (default: ["llama3.1", "mistral:7b", "gemma:2b"]) |

**Stream Format:**

The endpoint sends Server-Sent Events (SSE) with the following structure:

**Status Updates:**

```
data: { "content": "Fetching responses...", "done": false, "stage": "fetching" }
data: { "content": "Analyzing 150 responses...", "done": false, "stage": "analyzing" }
```

**Partial Content (Abstractive/Hybrid):**

```
data: { "content": "Based on the form responses, the following key insights emerged:", "done": false }
data: { "content": " - Majority of customers (65%) mentioned slow delivery times", "done": false }
data: { "content": " - Product quality received positive feedback (40 mentions)", "done": false }
```

**Final Chunk:**

```
data: { "content": "", "done": true, "model_used": "llama3.2", "fallback_used": false, "fallback_model": null, "responses_analyzed": 150, "processing_time_ms": 1250 }
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/summarize/stream \
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

**Example Response Stream (Abstractive/Hybrid):**

```
data: {"content": "Fetching responses...", "done": false, "stage": "fetching"}

data: {"content": "Analyzing 150 responses...", "done": false, "stage": "analyzing"}

data: {"content": "Based on the form responses, the following key insights emerged:", "done": false}

data: {"content": "\n\n- Majority of customers (65%) mentioned slow delivery times as a primary concern", "done": false}

data: {"content": "\n- Product quality received positive feedback with 40 mentions", "done": false}

data: {"content": "", "done": true, "model_used": "llama3.2", "fallback_used": false, "fallback_model": null, "responses_analyzed": 150, "processing_time_ms": 1250}
```

**Example Response Stream (Extractive):**

```
data: {"content": "Fetching responses...", "done": false, "stage": "fetching"}

data: {"content": "Analyzing 150 responses...", "done": false, "stage": "analyzing"}

data: {"content": "{\"format\": \"bullet_points\", \"bullet_points\": [{\"point\": \"Majority of customers (65%) mentioned slow delivery times\", \"sentiment\": \"negative\", \"supporting_count\": 98, \"confidence\": 0.85}]}", "done": true, "model_used": "tfidf", "responses_analyzed": 150, "processing_time_ms": 450}
```

**Service Layer:** `app/services/summarization_service.py` - `SummarizationService.hybrid_summarize()`, `app/services/ollama_service.py` - `OllamaService.chat_stream_with_fallback()`

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
| `nocache` | boolean | No | Bypass cache and invalidate for this form (default: false) |
| `fallback_models` | array | No | List of model names to try if primary fails (default: ["llama3.1", "mistral:7b", "gemma:2b"]) |

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
| `fallback_models` | array | No | List of model names to try if primary fails (default: ["llama3.1", "mistral:7b", "gemma:2b"]) |

---

#### 18.2.4 Summary Comparison Across Time Periods (M2-EXT-03c)

**Overview:**

The summary comparison feature enables trend analysis by comparing summaries across multiple time periods. This allows users to track changes in sentiment, themes, and response counts over time, answering questions like "How has sentiment changed over the last month?"

**Automatic Snapshot Creation:**

When a summary is generated via the `/summarize` endpoint, a snapshot is automatically saved (unless `save_snapshot` is set to `false`). Each snapshot includes:

* Complete summary data
* Period range (start and end dates)
* Response count
* Strategy used
* Creation timestamp

**Database Schema:**

Collection: `summary_snapshots`

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Primary key |
| `form_id` | UUID | Form identifier |
| `timestamp` | DateTime | When the snapshot was created |
| `period_start` | DateTime | Start of the analysis period |
| `period_end` | DateTime | End of the analysis period |
| `period_label` | String | Human-readable period label |
| `summary_data` | Dict | Complete summary data |
| `created_by` | String | User ID who created the snapshot |
| `response_count` | Integer | Number of responses analyzed |
| `strategy_used` | String | Summarization strategy used |

---

##### 18.2.4a Compare Summaries

Compare summaries across multiple time periods to identify trends.

* **Endpoint:** `/summary-comparison`
* **Method:** `GET`
* **Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `period_ranges` | JSON array | Yes* | Array of period ranges (see format below) |
| `preset` | string | Yes* | Preset period comparison (see options below) |

*Either `period_ranges` or `preset` must be provided.

**Period Ranges Format:**

```json
[
  {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-01-31T23:59:59Z",
    "label": "January 2025"
  },
  {
    "start": "2025-02-01T00:00:00Z",
    "end": "2025-02-28T23:59:59Z",
    "label": "February 2025"
  }
]
```

**Available Presets:**

| Preset | Description |
| :--- | :--- |
| `last_7_days` | Compare last 7 days with previous 7 days |
| `last_30_days` | Compare last 30 days with previous 30 days |
| `last_90_days` | Compare last 90 days with previous 90 days |
| `month_over_month` | Compare current month with last month |

**Response Schema:**

```json
{
  "form_id": "form_123",
  "snapshots_count": 2,
  "snapshots": [
    {
      "period": "January 2025",
      "snapshot_id": "snapshot_001",
      "data": { ... },
      "response_count": 150,
      "timestamp": "2025-02-01T10:00:00Z"
    },
    {
      "period": "February 2025",
      "snapshot_id": "snapshot_002",
      "data": { ... },
      "response_count": 200,
      "timestamp": "2025-03-01T10:00:00Z"
    }
  ],
  "trend_analysis": {
    "sentiment": [
      {
        "period": "January 2025",
        "positive_pct": 30.0,
        "negative_pct": 55.0,
        "neutral_pct": 15.0,
        "total_responses": 150
      },
      {
        "period": "February 2025",
        "positive_pct": 45.0,
        "negative_pct": 35.0,
        "neutral_pct": 20.0,
        "total_responses": 200
      }
    ],
    "sentiment_change": {
      "positive_change": 15.0,
      "negative_change": -20.0,
      "neutral_change": 5.0
    },
    "themes": {
      "delivery": [
        {"period": "January 2025", "mentions": 98},
        {"period": "February 2025", "mentions": 75}
      ],
      "product_quality": [
        {"period": "January 2025", "mentions": 40},
        {"period": "February 2025", "mentions": 55}
      ]
    },
    "response_counts": [
      {"period": "January 2025", "count": 150},
      {"period": "February 2025", "count": 200}
    ],
    "response_change": {
      "absolute": 50,
      "percentage": 33.33
    },
    "insights": [
      "Positive sentiment has improved significantly.",
      "Response volume increased by 33.33%."
    ]
  }
}
```

**Example Request (Preset):**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/123/summary-comparison?preset=last_30_days" \
  -H "Authorization: Bearer <token>"
```

**Example Request (Custom Periods):**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/123/summary-comparison?period_ranges=%5B%7B%22start%22%3A%222025-01-01T00%3A00%3A00Z%22%2C%22end%22%3A%222025-01-31T23%3A59%3A59Z%22%2C%22label%22%3A%22January%202025%22%7D%2C%7B%22start%22%3A%222025-02-01T00%3A00%3A00Z%22%2C%22end%22%3A%222025-02-28T23%3A59%3A59Z%22%2C%22label%22%3A%22February%202025%22%7D%5D" \
  -H "Authorization: Bearer <token>"
```

**Service Layer:** `app/services/summarization_service.py` - `SummarizationService.compare_summaries()`

---

##### 18.2.4b Get Summary Trends

Get trend data for a specific metric over time.

* **Endpoint:** `/summary-trends`
* **Method:** `GET`
* **Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `metric` | string | No | Metric to track: "sentiment", "theme", or "response_count" (default: "sentiment") |
| `limit` | integer | No | Maximum number of snapshots to include (default: 10, max: 100) |

**Response Schema (Sentiment Metric):**

```json
{
  "form_id": "form_123",
  "metric": "sentiment",
  "snapshots_count": 5,
  "data": [
    {
      "snapshot_id": "snapshot_001",
      "timestamp": "2025-01-01T10:00:00Z",
      "period_label": "2024-12-01 to 2024-12-31",
      "period_start": "2024-12-01T00:00:00Z",
      "period_end": "2024-12-31T23:59:59Z",
      "response_count": 150,
      "positive_pct": 30.0,
      "negative_pct": 55.0,
      "neutral_pct": 15.0
    },
    {
      "snapshot_id": "snapshot_002",
      "timestamp": "2025-02-01T10:00:00Z",
      "period_label": "2025-01-01 to 2025-01-31",
      "period_start": "2025-01-01T00:00:00Z",
      "period_end": "2025-01-31T23:59:59Z",
      "response_count": 200,
      "positive_pct": 45.0,
      "negative_pct": 35.0,
      "neutral_pct": 20.0
    }
  ],
  "trend_direction": "increasing",
  "trend_percentage": 15.0
}
```

**Response Schema (Theme Metric):**

```json
{
  "form_id": "form_123",
  "metric": "theme",
  "snapshots_count": 3,
  "data": [
    {
      "snapshot_id": "snapshot_001",
      "timestamp": "2025-01-01T10:00:00Z",
      "period_label": "2024-12-01 to 2024-12-31",
      "response_count": 150,
      "themes": [
        {"name": "delivery", "mentions": 98},
        {"name": "product_quality", "mentions": 40}
      ]
    }
  ]
}
```

**Response Schema (Response Count Metric):**

```json
{
  "form_id": "form_123",
  "metric": "response_count",
  "snapshots_count": 5,
  "data": [
    {
      "snapshot_id": "snapshot_001",
      "timestamp": "2025-01-01T10:00:00Z",
      "period_label": "2024-12-01 to 2024-12-31",
      "response_count": 150
    },
    {
      "snapshot_id": "snapshot_002",
      "timestamp": "2025-02-01T10:00:00Z",
      "period_label": "2025-01-01 to 2025-01-31",
      "response_count": 200
    }
  ],
  "trend_direction": "increasing",
  "trend_percentage": 33.33
}
```

**Example Request:**

```bash
# Get sentiment trends
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/123/summary-trends?metric=sentiment&limit=10" \
  -H "Authorization: Bearer <token>"

# Get theme trends
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/123/summary-trends?metric=theme&limit=20" \
  -H "Authorization: Bearer <token>"

# Get response count trends
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/123/summary-trends?metric=response_count&limit=10" \
  -H "Authorization: Bearer <token>"
```

**Service Layer:** `app/services/summarization_service.py` - `SummarizationService.get_summary_trends()`

---

##### 18.2.4c List Summary Snapshots

List all summary snapshots for a form.

* **Endpoint:** `/summary-snapshots`
* **Method:** `GET`
* **Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `limit` | integer | No | Maximum number of snapshots (default: 20, max: 100) |
| `offset` | integer | No | Number of snapshots to skip (default: 0) |

**Response Schema:**

```json
{
  "form_id": "form_123",
  "total": 45,
  "offset": 0,
  "limit": 20,
  "snapshots": [
    {
      "id": "snapshot_045",
      "form_id": "form_123",
      "timestamp": "2025-03-01T10:00:00Z",
      "period_start": "2025-02-01T00:00:00Z",
      "period_end": "2025-02-28T23:59:59Z",
      "period_label": "2025-02-01 to 2025-02-28",
      "response_count": 200,
      "strategy_used": "hybrid",
      "created_by": "user_123",
      "created_at": "2025-03-01T10:00:00Z"
    }
  ]
}
```

**Example Request:**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/123/summary-snapshots?limit=20&offset=0" \
  -H "Authorization: Bearer <token>"
```

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
| `sensitivity` | string | No | "auto", "low", "medium", or "high" (default: "medium") |
| `use_dynamic_thresholds` | boolean | No | Use thresholds from database (default: false) |
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
  "thresholds_used": {
    "z_score_threshold": 3.0,
    "z_score_2sigma": 2.0,
    "z_score_3sigma": 3.0,
    "z_score_4sigma": 4.0,
    "active_threshold": 3.0,
    "sensitivity": "medium",
    "calculated_at": "2026-02-04T07:00:00.000Z",
    "length_thresholds": {
      "mean": 150,
      "std": 45,
      "lower_2sigma": 60,
      "upper_2sigma": 240,
      "lower_3sigma": 15,
      "upper_3sigma": 285,
      "lower_4sigma": -30,
      "upper_4sigma": 330
    },
    "sentiment_thresholds": {
      "mean": 0.3,
      "std": 1.2,
      "lower_2sigma": -2.1,
      "upper_2sigma": 2.7,
      "lower_3sigma": -3.3,
      "upper_3sigma": 3.9,
      "lower_4sigma": -4.5,
      "upper_4sigma": 5.1
    }
  },
  "use_dynamic_thresholds": false,
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
    "sensitivity": "medium",
    "use_dynamic_thresholds": false
  }'
```

**Example Request with Dynamic Thresholds:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/detect-anomalies \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_type": "full",
    "detection_types": ["spam", "outlier", "duplicate"],
    "sensitivity": "auto",
    "use_dynamic_thresholds": true
  }'
```

**Service Layer:** `app/services/anomaly_detection_service.py` - `AnomalyDetectionService.run_full_detection()`, `AnomalyDetectionService.detect_spam()`, `AnomalyDetectionService.detect_outliers()`

---

#### 18.3.5 Auto-Thresholding for Anomaly Detection (M2-EXT-04b)

The anomaly detection system now supports dynamic threshold calculation based on data distribution. This feature enables adaptive thresholds that automatically adjust based on the statistical characteristics of form responses.

**Key Features:**

* **Dynamic Z-score thresholds**: Automatically calculates thresholds based on mean and standard deviation
* **Sensitivity levels**: "auto", "low", "medium", "high" - each adjusts the detection threshold
* **Baseline statistics**: Stores baseline metrics (avg/std for response length, sentiment score)
* **Threshold history**: Tracks threshold changes over time for audit and analysis
* **Manual adjustment**: Allows manual threshold overrides when needed

**Sensitivity Levels:**

| Sensitivity | Z-Score Threshold | Description |
| :--- | :--- | :--- |
| `auto` | Adaptive (2.0-4.0) | Automatically adjusts based on data variance |
| `low` | 4.0σ | High threshold, fewer false positives |
| `medium` | 3.0σ | Standard threshold, balanced approach |
| `high` | 2.0σ | Low threshold, catches more anomalies |

**Auto Threshold Logic:**

When sensitivity is set to "auto", the system analyzes the data distribution:

* Low variance (std < 0.5): Uses 4.0σ to avoid false positives
* Normal variance (0.5 ≤ std < 1.5): Uses 3.0σ standard threshold
* High variance (std ≥ 1.5): Uses 2.5σ to catch more outliers

---

##### 18.3.5.1 Update Baseline

Update baseline statistics and calculate dynamic thresholds for a form.

* **Endpoint:** `/thresholds/update-baseline`
* **Method:** `POST`
* **Auth Required:** Yes

**Response Schema (Success):**

```json
{
  "message": "Baseline updated successfully",
  "baseline_stats": {
    "avg_response_length": 150,
    "std_response_length": 45,
    "avg_sentiment_score": 0.3,
    "std_sentiment_score": 1.2
  },
  "thresholds": {
    "z_score_threshold": 3.0,
    "z_score_2sigma": 2.0,
    "z_score_3sigma": 3.0,
    "z_score_4sigma": 4.0,
    "active_threshold": 3.0,
    "sensitivity": "auto",
    "calculated_at": "2026-02-04T07:00:00.000Z"
  },
  "response_count": 150,
  "threshold_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/thresholds/update-baseline \
  -H "Authorization: Bearer <token>"
```

**Service Layer:** `app/services/anomaly_detection_service.py` - `AnomalyDetectionService.update_baseline()`

---

##### 18.3.5.2 Get Threshold History

Retrieve threshold changes over time for a form.

* **Endpoint:** `/thresholds/history`
* **Method:** `GET`
* **Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `limit` | integer | No | Maximum number of records (default: 50) |

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "threshold_history": [
    {
      "threshold_id": "550e8400-e29b-41d4-a716-446655440000",
      "form_id": "form_123",
      "timestamp": "2026-02-04T07:00:00.000Z",
      "created_at": "2026-02-04T07:00:00.000Z",
      "thresholds": {
        "z_score_threshold": 3.0,
        "sensitivity": "auto",
        "calculated_at": "2026-02-04T07:00:00.000Z"
      },
      "sensitivity": "auto",
      "baseline_stats": {
        "avg_response_length": 150,
        "std_response_length": 45
      },
      "response_count": 150,
      "created_by": "user_123",
      "is_manual": false
    }
  ]
}
```

**Example Request:**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/123/thresholds/history?limit=20" \
  -H "Authorization: Bearer <token>"
```

**Service Layer:** `app/services/anomaly_detection_service.py` - `AnomalyDetectionService.get_threshold_history()`

---

##### 18.3.5.3 Get Latest Threshold

Get the latest threshold configuration for a form.

* **Endpoint:** `/thresholds/latest`
* **Method:** `GET`
* **Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `sensitivity` | string | No | Filter by sensitivity (auto, low, medium, high) |

**Response Schema (Success):**

```json
{
  "threshold_id": "550e8400-e29b-41d4-a716-446655440000",
  "form_id": "form_123",
  "timestamp": "2026-02-04T07:00:00.000Z",
  "thresholds": {
    "z_score_threshold": 3.0,
    "z_score_2sigma": 2.0,
    "z_score_3sigma": 3.0,
    "z_score_4sigma": 4.0,
    "active_threshold": 3.0,
    "sensitivity": "auto",
    "calculated_at": "2026-02-04T07:00:00.000Z"
  },
  "sensitivity": "auto",
  "baseline_stats": {
    "avg_response_length": 150,
    "std_response_length": 45,
    "avg_sentiment_score": 0.3,
    "std_sentiment_score": 1.2
  },
  "response_count": 150,
  "created_by": "user_123",
  "is_manual": false
}
```

**Example Request:**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/123/threshold/latest?sensitivity=auto" \
  -H "Authorization: Bearer <token>"
```

**Service Layer:** `app/services/anomaly_detection_service.py` - `AnomalyDetectionService.get_latest_threshold()`

---

##### 18.3.5.4 Set Manual Threshold

Manually set a threshold configuration for a form.

* **Endpoint:** `/thresholds/manual`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `thresholds` | object | Yes | Custom threshold configuration |
| `reason` | string | No | Reason for manual adjustment |

**Response Schema (Success):**

```json
{
  "message": "Manual threshold set successfully",
  "threshold_id": "550e8400-e29b-41d4-a716-446655440000",
  "thresholds": {
    "z_score_threshold": 2.5,
    "sensitivity": "high",
    "calculated_at": "2026-02-04T07:00:00.000Z"
  },
  "baseline_stats": {
    "avg_response_length": 150,
    "std_response_length": 45
  },
  "created_at": "2026-02-04T07:00:00.000Z"
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/thresholds/manual \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "thresholds": {
      "z_score_threshold": 2.5,
      "sensitivity": "high"
    },
    "reason": "Too many false positives with auto threshold"
  }'
```

**Service Layer:** `app/services/anomaly_detection_service.py` - `AnomalyDetectionService.set_manual_threshold()`

---

##### 18.3.5.5 Database Schema

**Collection:** `anomaly_thresholds`

**Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Primary key |
| `form_id` | UUID | Form identifier |
| `timestamp` | DateTime | When threshold was calculated |
| `thresholds` | Object | Threshold configuration |
| `sensitivity` | String | Sensitivity level (auto, low, medium, high) |
| `baseline_stats` | Object | Baseline statistics used |
| `created_by` | String | User/system identifier |
| `response_count` | Integer | Number of responses in baseline |
| `is_manual` | Boolean | Whether manually adjusted |
| `manual_adjustment_reason` | String | Reason for manual override |
| `created_at` | DateTime | Record creation timestamp |

**Indexes:**

* `form_id`
* `timestamp`
* `sensitivity`
* `created_by`
* `('form_id', 'timestamp')`
* `('form_id', 'sensitivity')`
* `('form_id', 'created_at')`

**Model:** `app/models/Form.py` - `AnomalyThreshold`

---

#### 18.3.6 Batch Scanning for Anomaly Detection (M2-EXT-04c)

The anomaly detection system now supports batch scanning for large form response sets. This feature enables scheduled scans with progress tracking for long-running operations.

**Key Features:**

* **Batch processing**: Scan specific response IDs (not all responses)
* **Progress tracking**: Monitor scan progress in real-time
* **Async processing**: Support for large batches without blocking
* **Status polling**: Check scan status and estimated completion time
* **Result caching**: Cached results with TTL for performance
* **Error handling**: Graceful error reporting and recovery

**Batch Scan Status Values:**

| Status | Description |
| :--- | :--- |
| `pending` | Batch scan is queued but not started |
| `in_progress` | Batch scan is currently running |
| `completed` | Batch scan finished successfully |
| `failed` | Batch scan encountered an error |

**Caching:**

* In-progress batches: Cached for 5 minutes
* Completed batches: Cached for 1 hour
* Use `nocache=true` query parameter to bypass cache

---

##### 18.3.6.1 Detect Anomalies (Batch)

Run anomaly detection on a batch of form responses.

* **Endpoint:** `/detect-anomalies/batch`
* **Method:** `POST`
* **Auth Required:** Yes

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `response_ids` | array | Yes | List of response IDs to scan |
| `scan_config` | object | No | Scan configuration |
| `scan_config.detection_types` | array | No | Types: ["spam", "outlier", "impossible_value", "duplicate"] |
| `scan_config.sensitivity` | string | No | "auto", "low", "medium", or "high" (default: "medium") |
| `scan_config.use_dynamic_thresholds` | boolean | No | Use thresholds from database (default: false) |
| `batch_id` | string | No | Custom batch ID (auto-generated if not provided) |

**Response Schema (Success - Completed):**

```json
{
  "batch_id": "batch_abc123_1234567890",
  "status": "completed",
  "form_id": "form_123",
  "total_responses": 100,
  "scanned_count": 100,
  "anomalies_detected": 12,
  "summary": {
    "total_responses": 100,
    "anomalies_detected": 12,
    "summary_by_type": {
      "spam": 5,
      "outlier": 3,
      "duplicate": 2,
      "impossible_value": 1,
      "pattern": 1
    }
  },
  "results": {
    "total_responses": 100,
    "anomalies_detected": 12,
    "baseline": {
      "avg_response_length": 150,
      "std_response_length": 45,
      "avg_sentiment_score": 0.3,
      "std_sentiment_score": 1.2
    },
    "anomalies": [...],
    "summary_by_type": {
      "spam": 5,
      "outlier": 3,
      "duplicate": 2,
      "impossible_value": 1,
      "pattern": 1
    },
    "thresholds_used": {
      "z_score_threshold": 3.0,
      "sensitivity": "medium"
    },
    "use_dynamic_thresholds": false
  },
  "started_at": "2026-02-04T10:00:00Z",
  "completed_at": "2026-02-04T10:01:30Z"
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/detect-anomalies/batch \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "response_ids": ["resp_1", "resp_2", "resp_3"],
    "scan_config": {
      "detection_types": ["spam", "outlier"],
      "sensitivity": "medium",
      "use_dynamic_thresholds": false
    }
  }'
```

**Service Layer:** `app/services/anomaly_detection_service.py` - `AnomalyDetectionService.scan_batch()`

---

##### 18.3.6.2 Get Batch Scan Status

Get status of a batch anomaly detection scan.

* **Endpoint:** `/detect-anomalies/batch/<batch_id>/status`
* **Method:** `GET`
* **Auth Required:** Yes

**Query Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `nocache` | string | No | Set to "true" to bypass cache |

**Response Schema (Success - In Progress):**

```json
{
  "batch_id": "batch_abc123_1234567890",
  "form_id": "form_123",
  "status": "in_progress",
  "progress": 45.5,
  "total_responses": 100,
  "scanned_count": 45,
  "results_count": 5,
  "estimated_completion": "2026-02-04T10:02:00Z",
  "started_at": "2026-02-04T10:00:00Z",
  "completed_at": null,
  "error_message": null
}
```

**Response Schema (Success - Completed):**

```json
{
  "batch_id": "batch_abc123_1234567890",
  "form_id": "form_123",
  "status": "completed",
  "progress": 100.0,
  "total_responses": 100,
  "scanned_count": 100,
  "results_count": 12,
  "estimated_completion": null,
  "started_at": "2026-02-04T10:00:00Z",
  "completed_at": "2026-02-04T10:01:30Z",
  "error_message": null,
  "results": {
    "total_responses": 100,
    "anomalies_detected": 12,
    "anomalies": [...],
    "summary_by_type": {...}
  },
  "summary": {
    "total_responses": 100,
    "anomalies_detected": 12,
    "summary_by_type": {...}
  }
}
```

**Example Request:**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/123/detect-anomalies/batch/batch_abc123_1234567890/status" \
  -H "Authorization: Bearer <token>"
```

**Example Request (Bypass Cache):**

```bash
curl -X GET "http://localhost:5000/form/api/v1/ai/forms/123/detect-anomalies/batch/batch_abc123_1234567890/status?nocache=true" \
  -H "Authorization: Bearer <token>"
```

**Service Layer:** `app/services/anomaly_detection_service.py` - `AnomalyDetectionService.get_batch_status()`

---

##### 18.3.6.3 Database Schema

**Collection:** `anomaly_batch_scans`

**Fields:**

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Primary key |
| `form_id` | UUID | Form identifier |
| `batch_id` | String | Unique batch identifier |
| `response_ids` | Array | List of response IDs to scan |
| `scan_config` | Object | Scan configuration |
| `status` | String | Scan status (pending, in_progress, completed, failed) |
| `total_responses` | Integer | Total responses to scan |
| `scanned_count` | Integer | Number of responses scanned |
| `results_count` | Integer | Number of anomalies detected |
| `results` | Object | Complete scan results |
| `summary` | Object | Summary statistics |
| `created_by` | String | User/system identifier |
| `started_at` | DateTime | Scan start time |
| `completed_at` | DateTime | Scan completion time |
| `error_message` | String | Error message if failed |
| `created_at` | DateTime | Record creation timestamp |

**Indexes:**

* `form_id`
* `batch_id`
* `status`
* `created_by`
* `started_at`
* `completed_at`
* `('form_id', 'batch_id')`
* `('form_id', 'status')`
* `('batch_id', 'status')`

**Model:** `app/models/Form.py` - `AnomalyBatchScan`

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

Check the health status of AI services including Ollama availability, model loading status, and response latency.

* **Endpoint:** `/health`
* **Method:** `GET`
* **Auth Required:** No
* **Base Path:** `/form/api/v1/ai`

**Description:**

This endpoint provides comprehensive health monitoring for AI services, including:

* Overall AI service status (healthy/degraded/unavailable)
* Ollama server connection status
* Available models list
* Default and embedding model loading status
* Response latency measurement

**Response Schema (Success - Healthy):**

```json
{
  "status": "healthy",
  "ollama": {
    "status": "healthy",
    "available": true,
    "models": ["llama3.2", "nomic-embed-text"],
    "default_model": "llama3.2",
    "embedding_model": "nomic-embed-text",
    "latency_ms": 45
  },
  "timestamp": "2026-02-04T10:00:00Z"
}
```

**Response Schema (Degraded):**

```json
{
  "status": "degraded",
  "ollama": {
    "status": "degraded",
    "available": true,
    "models": ["llama3.2"],
    "default_model": "llama3.2",
    "embedding_model": "nomic-embed-text",
    "latency_ms": 6500,
    "error": "Latency exceeds threshold"
  },
  "timestamp": "2026-02-04T10:00:00Z"
}
```

**Response Schema (Unavailable):**

```json
{
  "status": "unavailable",
  "error": "Ollama service is not reachable",
  "timestamp": "2026-02-04T10:00:00Z"
}
```

**Status Values:**

| Status | Description |
| :--- | :--- |
| `healthy` | All AI services are functioning normally |
| `degraded` | AI services are available but with issues (e.g., high latency, missing models) |
| `unavailable` | AI services are not reachable |

**Caching:**

Health check results are cached for 1 minute to avoid excessive Ollama pings. Use the endpoint for monitoring and alerting purposes.

**Periodic Monitoring:**

The system automatically performs health checks every 5 minutes and logs warnings for:

* Ollama server unreachable
* Default model not loaded
* Latency exceeding 5 seconds

**Example Request:**

```bash
curl -X GET http://localhost:5000/form/api/v1/ai/health
```

**Example Response:**

```json
{
  "status": "healthy",
  "ollama": {
    "status": "healthy",
    "available": true,
    "models": ["llama3.2", "nomic-embed-text"],
    "default_model": "llama3.2",
    "embedding_model": "nomic-embed-text",
    "latency_ms": 45
  },
  "timestamp": "2026-02-04T10:00:00Z"
}
```

---

#### 18.2.5 Cache Invalidation (M2-INT-01b)

**Overview:**

The cache invalidation feature allows manual control over cached NLP search and summarization results. This improves data freshness and reduces stale cache hits by providing endpoints to invalidate cache entries selectively.

**Cache Invalidation Patterns:**

| Pattern | Description | Scope |
| :--- | :--- | :--- |
| `all` | Invalidate all cache entries for the service | Global |
| `by_form` | Invalidate all cache for a specific form | Form-scoped |
| `by_query` | Invalidate cache for a specific search query | Query-scoped |
| `by_user` | Invalidate all cache for a specific user | User-scoped |
| `by_responses` | Invalidate cache for specific response IDs | Response-scoped |

---

##### 18.2.5a Manual Cache Invalidation

Manually invalidate cache entries for a specific form.

* **Endpoint:** `/cache/invalidate`
* **Method:** `POST`
* **Auth Required:** Yes (Edit permission required)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `pattern` | string | No | Invalidation pattern: "all", "nlp_search", "summarization", "by_query" (default: "all") |
| `query` | string | No* | Specific query text (required for "by_query" pattern) |

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "pattern": "all",
  "keys_invalidated": 5,
  "invalidated_at": "2026-02-04T10:00:00Z"
}
```

**Example Request (Invalidate All Cache):**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/cache/invalidate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": "all"
  }'
```

**Example Request (Invalidate Specific Query):**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/cache/invalidate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": "by_query",
    "query": "unhappy customers"
  }'
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.invalidate_cache()`, `app/services/summarization_service.py` - `SummarizationService.invalidate_cache()`

---

##### 18.2.5b Clear All Cache for Form

Clear all cached data for a specific form including NLP search, semantic search, and summarization.

* **Endpoint:** `/cache`
* **Method:** `DELETE`
* **Auth Required:** Yes (Edit permission required)

**Response Schema (Success):**

```json
{
  "form_id": "form_123",
  "keys_invalidated": 10,
  "cleared_at": "2026-02-04T10:00:00Z"
}
```

**Example Request:**

```bash
curl -X DELETE http://localhost:5000/form/api/v1/ai/forms/123/cache \
  -H "Authorization: Bearer <token>"
```

**Service Layer:** `app/services/nlp_service.py` - `NLPSearchService.invalidate_cache()`, `app/services/summarization_service.py` - `SummarizationService.invalidate_cache()`

---

##### 18.2.5c Cache Bypass Parameter

All AI endpoints now support a `nocache` parameter to bypass cache and force fresh computation:

| Endpoint | Parameter | Effect |
| :--- | :--- | :--- |
| `/nlp-search` | `options.nocache` | Invalidates cache for the specific query |
| `/semantic-search` | `options.nocache` | Invalidates cache for the specific query |
| `/summarize` | `nocache` | Invalidates all cache for the form |
| `/executive-summary` | `nocache` | Invalidates all cache for the form |

**Example Request with Cache Bypass:**

```bash
curl -X POST http://localhost:5000/form/api/v1/ai/forms/123/summarize \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "hybrid",
    "nocache": true
  }'
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
| `OLLAMA_POOL_SIZE` | Maximum number of pooled connections | `5` |
| `OLLAMA_POOL_TIMEOUT` | Timeout for getting connection from pool (seconds) | `30` |
| `OLLAMA_CONNECTION_TIMEOUT` | Timeout for individual HTTP requests (seconds) | `10` |

**Requirements:**

* Ollama must be running with models pulled
* For semantic search: `ollama pull nomic-embed-text`
* For summarization: `ollama pull llama3.2`

**Connection Pooling:**

The Ollama service implements HTTP connection pooling to improve performance by reusing connections across requests:

* **Pool Size:** Configurable via `OLLAMA_POOL_SIZE` (default: 5 connections)
* **Pool Timeout:** Maximum time to wait for available connection (default: 30 seconds)
* **Connection Timeout:** Timeout for individual HTTP requests (default: 10 seconds)
* **Automatic Management:** Connections are automatically returned to pool after use
* **Pool Exhaustion:** New connections created when pool is empty
* **Idle Connection Handling:** Connections closed when pool is full

**Connection Pool Features:**

* Thread-safe connection management using Queue
* Automatic connection reuse for chat and streaming requests
* Graceful handling of pool exhaustion
* Connection cleanup on pool overflow
* Supports both synchronous and streaming operations

**Health Monitoring:**

The Ollama service includes automatic health monitoring:

* **Health Check Endpoint:** `GET /form/api/v1/ai/health`
* **Cache TTL:** 1 minute (health results cached to avoid excessive pings)
* **Periodic Checks:** Every 5 minutes (automatic background monitoring)
* **Latency Threshold:** 5 seconds (warning logged if exceeded)

**Health Check Features:**

* Server connection status monitoring
* Available models listing
* Model loading status verification
* Response latency measurement
* Automatic warning logging for issues

**Rate Limiting:**

* No explicit rate limiting at application level
* Ollama server may have its own limits
* Semantic search results are cached for 1 hour
* Health check results are cached for 1 minute

---

## 20. Distributed Locking for Concurrent Cache Access

**Overview:**

The application implements distributed locking for concurrent cache access to prevent race conditions when multiple requests write to the same cache key. This prevents cache stampede and ensures data consistency.

**Locking Methods:**

The [`RedisClient`](app/utils/redis_client.py:26) class provides the following distributed locking methods:

| Method | Description |
| :--- | :--- |
| [`acquire_lock(key)`](app/utils/redis_client.py:127) | Acquire a lock with timeout |
| [`release_lock(key)`](app/utils/redis_client.py:156) | Release a lock |
| [`acquire_lock_with_retry(key, timeout, max_attempts)`](app/utils/redis_client.py:178) | Acquire lock with retry logic and exponential backoff |
| [`set_with_lock(key, value, ttl)`](app/utils/redis_client.py:199) | Set cache value with automatic locking |
| [`get_with_lock(key)`](app/utils/redis_client.py:218) | Get cache value with automatic locking |
| [`delete_lock(key)`](app/utils/redis_client.py:234) | Delete a lock (not the cache key) |
| [`get_lock_status()`](app/utils/redis_client.py:242) | Get lock health status for monitoring |

**Lock Configuration:**

| Configuration | Default | Description |
| :--- | :--- | :--- |
| `_lock_timeout` | 30 seconds | Lock timeout in seconds |
| `_lock_retry_max_attempts` | 3 | Maximum retry attempts for lock acquisition |
| `_lock_retry_backoff` | 0.1 seconds | Initial backoff in seconds |
| `_lock_retry_backoff_multiplier` | 2.0 | Backoff multiplier for exponential backoff |

**Usage in Services:**

**NLP Search Service:**

The [`nlp_search.py`](app/routes/v1/form/nlp_search.py) route uses distributed locking for cache operations:

```python
# Get cached result with lock
cached_result = redis_client.get_with_lock(cache_key)

# Set cache result with lock
redis_client.set_with_lock(cache_key, response, ttl=3600)
```

**NLP Service:**

The [`nlp_service.py`](app/services/nlp_service.py) uses distributed locking for popular queries caching:

```python
# Get from cache with lock
cached = redis_client.get_with_lock(cache_key)

# Set to cache with lock
redis_client.set_with_lock(cache_key, json.dumps(popular_queries), ttl=3600)
```

**Lock Health Monitoring:**

Use the [`get_lock_status()`](app/utils/redis_client.py:242) method to monitor lock health:

```python
from app.utils.redis_client import redis_client

lock_status = redis_client.get_lock_status()
print(f"Total locks: {lock_status['total_locks']}")
print(f"Active locks: {lock_status['active_locks']}")
print(f"Expired locks: {lock_status['expired_locks']}")
```

**Lock Cleanup:**

The [`cleanup_expired_locks()`](app/utils/redis_client.py:270) method can be used to clean up expired locks:

```python
from app.utils.redis_client import redis_client

cleaned_count = redis_client.cleanup_expired_locks()
print(f"Cleaned up {cleaned_count} expired locks")
```

**Benefits:**

* **Prevents Race Conditions:** Ensures only one thread can write to a cache key at a time
* **Prevents Cache Stampede:** Multiple concurrent requests don't overwhelm the cache
* **Automatic Lock Release:** Locks are automatically released when operations complete
* **Exponential Backoff:** Retry logic with exponential backoff reduces contention
* **Health Monitoring:** Built-in lock status monitoring for debugging

**Implementation Notes:**

* Locks are stored in-memory for the in-memory Redis client implementation
* Lock keys are automatically suffixed with `:lock` to avoid conflicts with cache keys
* Locks include thread ID for ownership verification
* Expired locks are automatically cleaned up during acquisition attempts

---

## 21. External SMS Gateway

**Base path:** `/api/v1/sms`

The SMS Gateway service provides a simple wrapper for sending SMS via the external AIIMS RPC API.

### Configuration

The following environment variables must be set:

| Variable | Description |
| :--- | :--- |
| `SMS_API_URL` | External SMS API endpoint URL |
| `SMS_API_TOKEN` | Authorization bearer token for the external API |

### 21.1 Send Single SMS

Send a single SMS message via the external API.

* **Endpoint:** `/single`
* **Method:** `POST`
* **Auth Required:** Yes (JWT)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `mobile` | string | Yes | Recipient phone number |
| `message` | string | Yes | SMS message content |

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/sms/single \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "9899378106",
    "message": "Hello from AIIMS"
  }'
```

**Python Example:**

```python
import requests
import json

url = "https://rpcapplication.aiims.edu/services/api/v1/sms/single"
Token = "9a6a4578-743a-4172-9e40-534c79d08eda"

payload = json.dumps({
  "mobile": "9899378106",
  "message": "Hello from AIIMS"
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': f'Bearer {Token}'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
```

**Response (Success):**

```json
{
  "success": true,
  "message_id": "...",
  "status_code": 200
}
```

**Response (Failure):**

```json
{
  "success": false,
  "error": "Error message",
  "status_code": 500
}
```

---

### 21.2 Send OTP

Send an OTP (One-Time Password) via SMS.

* **Endpoint:** `/otp`
* **Method:** `POST`
* **Auth Required:** Yes (JWT)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `mobile` | string | Yes | Recipient phone number |
| `otp` | string | Yes | OTP code to send |

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/sms/otp \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "9899378106",
    "otp": "123456"
  }'
```

**Response:**

```json
{
  "success": true,
  "message_id": "...",
  "status_code": 200
}
```

---

### 21.3 Send Notification

Send a notification via SMS.

* **Endpoint:** `/notify`
* **Method:** `POST`
* **Auth Required:** Yes (JWT)

**Input Schema:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `mobile` | string | Yes | Recipient phone number |
| `title` | string | No | Notification title |
| `body` | string | Yes | Notification body |

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/sms/notify \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "9899378106",
    "title": "Appointment Reminder",
    "body": "Your appointment is tomorrow at 10 AM"
  }'
```

---

### 21.4 Health Check

Check the health status of the SMS service.

* **Endpoint:** `/health`
* **Method:** `GET`
* **Auth Required:** No

**Example Request:**

```bash
curl -X GET http://localhost:5000/api/v1/sms/health
```

**Response (Healthy):**

```json
{
  "status": "healthy",
  "service": "external_sms",
  "api_url": "https://rpcapplication.aiims.edu/services/api/v1/sms/single"
}
```

**Response (Unhealthy):**

```json
{
  "status": "unhealthy",
  "service": "external_sms",
  "error": "SMS API not configured"
}
```

---

### 21.5 Service Layer

**Main Service:** [`app/services/external_sms_service.py`](app/services/external_sms_service.py) - `ExternalSMSService`

**Route:** [`app/routes/v1/sms_route.py`](app/routes/v1/sms_route.py)
