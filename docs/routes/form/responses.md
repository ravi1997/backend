# Form Responses API

## Overview

The Form Responses module is the operational engine for data collection, handling the entire lifecycle of a submission from initial **Draft** to **Final Approval**. It provides high-performance endpoints for submitting structured data (including **file uploads** and repeatable sections), managing response versions, and tracking a complete **audit history** of every change. The API includes a sophisticated **Search & Filter engine** capable of executing complex logical queries (AND/OR/NOT), date-range filtering, and cursor-based pagination for large datasets. Additionally, it integrates with the **Workflow Engine** to trigger automated actions (like state transitions or notifications) immediately upon submission, ensuring seamless business process integration.

## Base URL

`/form/api/v1/form`

## Endpoints

### POST /<form_id>/responses

**Description**: Submits a new response for a specific form. Supports saving as a draft and handles multipart/form-data for file uploads.
**Auth Required**: Yes
**Query Parameters**:

- `draft` (Optional): If `true`, saves the response as a draft (bypasses full validation).
**Request Body (JSON)**:

```json
{
  "data": {
    "section_id_1": {
      "question_id_1": "Answer text",
      "question_id_2": 42
    }
  }
}
```

**Examples**:

1. **Full Submission**: Finalize and submit all answers for validation.
2. **Partial Draft**: Save progress without completing mandatory fields.
3. **File Upload**: Submit images or documents using `multipart/form-data`.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/form/60d5f.../responses?draft=false \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"data": {"sec1": {"q1": "Blue"}}}'
```

**Expected Output**:

```json
{
  "message": "Response submitted",
  "response_id": "60d..."
}
```

---

### GET /<form_id>/responses/paginated

**Description**: Retrieves a paginated list of responses for a form.
**Auth Required**: Yes
**Query Parameters**:

- `page` (Default: 1): The page number.
- `limit` (Default: 10): Number of responses per page.
- `is_draft` (Default: false): Filter for drafts or final submissions.
**Examples**:

1. **Dashboard List**: Display a table of the first 10 submissions.
2. **Draft Recovery**: Fetch a user's saved drafts to resume data entry.
3. **Export Preview**: View a larger batch (e.g., 100) of final responses.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/form/60d5f.../responses/paginated?page=1&limit=5 \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
{
  "total": 54,
  "page": 1,
  "responses": [...]
}
```

---

### POST /<form_id>/responses/search

**Description**: Executes a deep search across form responses using complex filters, sorting, and cursor-based pagination.
**Auth Required**: Yes
**Request Body**:

```json
{
  "data": {
    "question_id_1": {"op": "icontains", "value": "test", "type": "string", "fuzzy": true}
  },
  "date_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-12-31T23:59:59Z"
  },
  "sort_by": "submitted_at",
  "sort_order": "desc",
  "limit": 20
}
```

**Examples**:

1. **Fuzzy Search**: Find responses where 'Name' contains 'John'.
2. **Range Filter**: Get all submissions between January and March.
3. **Saved Search**: Execute a pre-defined filter using `saved_search_id`.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/form/60d5f.../responses/search \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"data": {"q1": {"op": "gte", "value": 18, "type": "number"}}}'
```

**Expected Output**:

```json
{
  "next_cursor": "2024-02-01...",
  "prev_cursor": "2024-01-20...",
  "limit": 10,
  "responses": [...]
}
```

---

### PATCH /<form_id>/responses/<response_id>/status

**Description**: Updates the administrative status of a response (e.g., Approved, Rejected).
**Auth Required**: Yes (Editor/Admin)
**Request Body**:

```json
{
  "status": "approved",
  "comment": "Data verified by supervisor"
}
```

**Examples**:

1. **Approval**: Mark a submission as reviewed and valid.
2. **Rejection**: Kick back a submission for corrections with a comment.
3. **Notification**: Triggers email/webhooks to notify the submitter of status change.

**Curl Command**:

```bash
curl -X PATCH http://localhost:5000/form/api/v1/form/60d5f.../responses/60d.../status \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"status": "approved"}'
```

**Expected Output**:

```json
{
  "message": "Response status updated to approved"
}
```

---
*Audit Note: Every update or status change is recorded in the `ResponseHistory` collection for full traceability.*
