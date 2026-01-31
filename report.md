# Backend Documentation & Implementation Gap Analysis

## 1. Overview

This report analyzes the discrepancies between the existing **AIOS Backend** (Python/MongoDB) and the **Frontend Builder** (Flutter) after the recent addition of advanced field types and the Custom Field Library.

---

## 2. Model & Enum Discrepancies

### A. Missing Field Types

The current `FIELD_TYPE_CHOICES` in `app/models/enumerations.py` is missing several types implemented in the frontend.

- **Action**: Add the following to `FIELD_TYPE_CHOICES`:
  - `signature`
  - `slider`
  - `image`
  - `divider`
  - `spacer`
  - `matrix_choice` (Note: Frontend uses `matrixChoice`, backend should probably use snake_case for consistency).

### B. Question Metadata Schema

The `Question` model has a `meta_data` (DictField), which is excellent. However, there is no documentation on what keys are expected for the new fields.

- **Requirement**: Update documentation to include:
  - **Rating**: `{ "max_stars": int, "icon": string }`
  - **Slider**: `{ "min": num, "max": num, "step": num }`
  - **Matrix Choice**: `{ "rows": string[], "columns": string[] }`
  - **Image**: `{ "image_url": string, "alt_text": string }`

---

## 3. Missing Infrastructure: Custom Field Library

### The Problem

The frontend now has a "Custom Field Library" where users can save and reuse pre-configured questions. The backend currently has `ResponseTemplate` and `Form.is_template`, but no mechanism to store individual **Question Templates**.

### The Proposal

Add a new Document model `CustomFieldTemplate`:

```python
class CustomFieldTemplate(Document):
    user_id = StringField(required=True)
    name = StringField(required=True)
    category = StringField()
    question_data = EmbeddedDocumentField(Question) # Reuses existing Question model
```

**API Endpoints required**:

- `GET /field-library/`: List user's saved question templates.
- `POST /field-library/`: Save a `Question` object as a template.

---

## 4. Documentation Improvements (`backend/docs`)

### A. API Endpoint Gaps

- **Workflows**: The `Form` model has a `webhooks` list and `notification_emails`, but `ENDPOINTS.md` does not explain how to update these.
- **Field Library**: Needs a new section for the proposed library mentioned above.

### B. Data Model Docs (`docs/models/Form.md`)

- Update the examples to show a **Matrix Choice** or **Slider** to help backend developers understand the nested `meta_data` structure.

---

## 5. Security & Validation Updates

- **Validation Logic**: The backend should use the `meta_data` to validate submissions.
  - *Example*: If a `slider` submission comes in, the backend should check `value >= meta_data['min']` and `value <= meta_data['max']`.
- **RBAC**: The `editors` and `viewers` lists in the `Form` model are documented but need explicit endpoint details on how to manage these permissions.

---

## Summary of Urgent Tasks

1. **Update Enums**: Sync `FIELD_TYPE_CHOICES` with the new Flutter field types.
2. **Implement Library Model**: Create the `CustomFieldTemplate` collection and API.
3. **Draft Metadata Specs**: Create a developer guide for the `meta_data` JSON structure to ensure frontend/backend parity.
