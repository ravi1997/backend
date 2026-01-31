# Form & Response Data Models

## Overview

The data models in AIOS are designed to encapsulate the high complexity of dynamic form definitions while ensuring that response data remains queryable and structured. The **Form** model acts as the root container, holding administrative settings such as **editors/viewers**, **webhooks**, and **publication timelines**. The actual "questions" reside within the **FormVersion** and **Section** embedded models, creating a clean separation between "What is this form?" (metadata) and "What does this form ask?" (schema). **FormResponse** then captures the user's answers, storing them in a hierarchical `data` dictionary that mirrors the section/question structure of the schema version used at the time of entry.

## Models

### Form (Document)

**Role**: Global container for a single form entity.
**Key Fields**:

- `title` / `slug`: Human-readable name and URL identifier.
- `status`: Lifecycle state (Draft, Published, Expired).
- `editors` / `viewers`: RBAC lists for granular access.
- `versions`: List of `FormVersion` embedded documents.

### FormResponse (Document)

**Role**: Individual submission record.
**Key Fields**:

- `form`: Reference to the parent Form.
- `data`: Deeply nested dictionary of answers `{section_id: {question_id: value}}`.
- `status`: Review state (Pending, Approved, Rejected).
- `version`: String tracking exactly which schema version was matched.
- `ai_results`: Captured insights from automated analysis.

## Examples

### Example 1: Creating a Form Model via API

To initialize a form, the backend instantiates a `Form` document with default settings:

```python
form = Form(
    title="Safety Audit",
    slug="safety-audit-2024",
    created_by="admin_123",
    status="draft"
)
form.save()
```

**Expected Entity**: A MongoDB document in the `forms` collection with a unique UUID.

### Example 2: Structured Response Data

A response stored in the `data` field reflects the form's hierarchy:

```json
{
  "section_safety_checks": {
    "question_helmet_worn": "yes",
    "question_floor_clean": "no"
  },
  "section_comments": {
    "question_notes": "Heavy traffic in Zone B"
  }
}
```

**Expected Storage**: A `FormResponse` document with `version: "1.0"` and `submitted_by: "user_456"`.

### Example 3: Response with AI Insights

The `ai_results` field is populated after an AI analysis run:

```json
{
  "sentiment": {"label": "negative", "score": -2},
  "pii_scan": {"found_count": 0},
  "moderation": {"is_safe": true, "flags": []}
}
```

**Expected Use**: Dashboards use this data to flag low-quality or negative feedback for immediate review.

---
*Industry Standard: Our models implement indexes on 'submitted_at', 'form', and 'deleted' flags to ensure sub-second search performance even with millions of records.*
