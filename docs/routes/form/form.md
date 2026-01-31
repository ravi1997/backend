# Form Management API

## Overview

The Form Management module is the core of the AIOS engine, providing the foundation for creating, versioning, and controlling complex data collection instruments. It supports a **hierarchical structure** of sections and questions, allowing for nested data models and sophisticated UI layouts. Key features include **multi-versioning**, which enables creators to iterate on form designs without breaking existing submissions, and **state-based lifecycle management** (Draft, Published, Expired). The module also handles advanced features like **translations** (multi-language support), **cloning** of existing forms, and **bulk importing** of question options via CSV. Designed for flexibility, this API serves both the administrative "Builder" interface and the end-user "Survey" view.

## Base URL

`/form/api/v1/form`

## Endpoints

### POST /

**Description**: Creates a new form shell. Sets initial permissions, status, and metadata.
**Auth Required**: Yes (Creator/Admin)
**Request Body**:

```json
{
  "title": "Quarterly Health Audit",
  "slug": "health-audit-q1",
  "description": "Comprehensive audit for regional clinics",
  "is_template": false,
  "status": "draft",
  "tags": ["healthcare", "internal"],
  "publish_at": "2024-03-01T09:00:00Z",
  "expires_at": "2024-06-30T17:00:00Z"
}
```

**Examples**:

1. **Standard Form**: Create a new audit form from scratch.
2. **Template Creation**: Mark a form as a template for others to clone.
3. **Scheduled Form**: Set future publish and expiry dates.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/form/ \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"title": "Feedback Form", "slug": "feedback-v1"}'
```

**Expected Output**:

```json
{
  "message": "Form created",
  "form_id": "60d5f..."
}
```

---

### GET /<form_id>

**Description**: Retrieves the full schema of a form, including sections, questions, and translations.
**Auth Required**: Yes
**Query Parameters**:

- `v` (Optional): Request a specific version string.
- `lang` (Optional): Request translations for a specific language code.
**Examples**:

1. **Latest View**: Fetch the current active version for display.
2. **Multilingual Fetch**: Fetch the form with 'Hindi' translations applied.
3. **Historical Audit**: View version '1.0' of a modified form.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/form/60d5f...?lang=hi \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
{
  "id": "60d5f...",
  "title": "...",
  "sections": [...],
  "active_version": "1.0"
}
```

---

### POST /<form_id>/versions

**Description**: Creates a new version for an existing form. Each version contains the full structure of sections and questions.
**Auth Required**: Yes (Creator/Admin)
**Request Body**:

```json
{
  "version": "2.0",
  "description": "Added logic for vaccination status",
  "activate": true,
  "sections": [
    {
      "title": "Patient History",
      "questions": [
        {
          "question_text": "Have you been vaccinated?",
          "type": "radio",
          "options": [{"option_label": "Yes", "option_value": "yes"}, {"option_label": "No", "option_value": "no"}]
        }
      ]
    }
  ]
}
```

**Examples**:

1. **Major Update**: Push a new version with structural changes.
2. **Minor Patch**: Update helper text or validation messages in a new version.
3. **Experimental Version**: Create a version without activating it.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/form/60d5f.../versions \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"version": "1.1", "sections": [{"title": "Basics", "questions": []}]}'
```

**Expected Output**:

```json
{
  "message": "Version 1.1 created"
}
```

---

### POST /<form_id>/clone

**Description**: Duplicates an existing form, creating a new document with a unique slug and resetting it to 'Draft' status.
**Auth Required**: Yes
**Request Body**:

```json
{
  "title": "New Survey Name",
  "slug": "custom-slug-123"
}
```

**Examples**:

1. **Template Usage**: Create a new form based on a corporate template.
2. **Branching**: Clone a successful form to modify it for a different department.
3. **Archival Copy**: Keep a snapshot of a form by cloning it before major edits.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/form/60d5f.../clone \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"title": "Cloned Audit"}'
```

**Expected Output**:

```json
{
  "message": "Form cloned",
  "form_id": "60d...",
  "slug": "health-audit-q1-copy-..."
}
```

---
*Note: Only the latest version is carried over during a clone operation to keep the new form clean.*
