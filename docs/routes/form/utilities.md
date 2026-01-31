# Form Utilities API

## Overview

The Form Utilities module provides essential support services for managing the auxiliary aspects of the form lifecycle, focusing on **File Management** and **Expiration Scheduling**. It handles the secure serving of user-uploaded files (identifying permissions for private vs. public forms) and provides administrative controls for setting and viewing form expiration dates. These utilities ensure that the platform can handle complex data types like images and documents while maintaining strict control over the availability of data collection windows. Together, they round out the administrative suite, providing the necessary "glue" for managing real-world operational constraints.

## Base URL

`/form/api/v1/form`

## Endpoints

### GET /<form_id>/files/<question_id>/<filename>

**Description**: Serves a previously uploaded file. Access is granted if the form is public or if the authenticated user has "View" permissions.
**Auth Required**: Optional (Required if form is private)
**Examples**:

1. **Direct View**: Open an uploaded ID proof image in the browser.
2. **Public Access**: Allow anonymous users to download attachments from a public survey.
3. **Security Check**: Deny access to files if the question ID does not match a `file_upload` field type.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/form/60d.../files/q_123/receipt.pdf \
     -H "Authorization: Bearer <token>" \
     --output download.pdf
```

**Expected Output**: The binary content of the requested file.

---

### PATCH /<form_id>/expire

**Description**: Schedules or updates the expiration date for a form. Once expired, the form will no longer accept submissions.
**Auth Required**: Yes (Admin/Superadmin only)
**Request Body**:

```json
{
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Examples**:

1. **Collection Deadline**: Set a hard cutoff for an end-of-year survey.
2. **Immediate Expiry**: Backdate the expiration to stop submissions instantly.
3. **Extension**: Move the deadline forward to allow more responses.

**Curl Command**:

```bash
curl -X PATCH http://localhost:5000/form/api/v1/form/60d.../expire \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{"expires_at": "2025-01-01T00:00:00Z"}'
```

**Expected Output**:

```json
{
  "message": "Form expiration updated"
}
```

---

### GET /expired

**Description**: Lists all forms that have passed their expiration date.
**Auth Required**: Yes (Admin/Superadmin only)
**Examples**:

1. **Archival Cleanup**: Identify forms that can now be archived or deleted.
2. **Operational Report**: See which collection streams are currently inactive.
3. **Audit**: Verify that closed campaigns are indeed no longer accepting data.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/form/expired \
     -H "Authorization: Bearer <admin_token>"
```

**Expected Output**:

```json
[
  {
    "id": "60d...",
    "title": "Old Marketing Survey",
    "expires_at": "2023-12-31T..."
  },
  ...
]
```

---
*Security Note: File serving logic prevents Path Traversal attacks by strictly constructing file paths from UUID-based identifiers.*
