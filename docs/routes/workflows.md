# Workflows API

## Overview

The Workflows API enables the automation of complex business logic and data processing tasks within the AIOS platform. It allows administrators to define **Automated Workflows** that are triggered by events (e.g., a form submission) and execute conditional actions based on the payload data. Using a powerful **Python-based condition engine**, users can specify precise rules for when a workflow should run (e.g., "only if age > 18"). Upon triggering, the system can perform actions such as creating subsequent follow-up forms, mapping data between documents, or assigning tasks to specific users. This module is critical for implementing multi-stage approval processes, operational escalations, and cross-departmental data synchronization.

## Base URL

`/form/api/v1/workflows`

## Endpoints

### POST /

**Description**: Creates a new automated workflow triggered by a specific form submission.
**Auth Required**: Yes (Admin/Superadmin only)
**Request Body**:

```json
{
  "name": "High Priority Follow-up",
  "description": "Triggered when a critical issue is reported",
  "trigger_form_id": "60d5f...",
  "trigger_condition": "response['priority'] == 'High'",
  "is_active": true,
  "actions": [
    {
      "type": "create_sub_form",
      "target_form_id": "60d5f_sub...",
      "data_mapping": {
        "source_id": "id",
        "detail": "data.description"
      },
      "assign_to_user_field": "assigned_staff"
    }
  ]
}
```

**Examples**:

1. **Simple Automation**: Auto-create a ticket when a form is submitted.
2. **Conditional Trigger**: Only run if a certain field value matches.
3. **Complex Mapping**: Pass data from the primary form to a follow-up form.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/workflows/ \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Audit Trigger",
           "trigger_form_id": "607d...",
           "trigger_condition": "True",
           "actions": [{"type": "notify", "target_form_id": "607e..."}]
         }'
```

**Expected Output**:

```json
{
  "message": "Workflow created",
  "id": "60d..."
}
```

---

### GET /

**Description**: Retrieves a list of all defined workflows. Can be filtered by `trigger_form_id`.
**Auth Required**: Yes (Admin/Superadmin only)
**Query Parameters**:

- `trigger_form_id` (Optional): Filter workflows triggered by a specific form.
**Examples**:

1. **Audit Workflows**: List all active automations for the "Audit" form.
2. **System Sync**: View all workflows across the platform.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/workflows/?trigger_form_id=607d... \
     -H "Authorization: Bearer <admin_token>"
```

**Expected Output**:

```json
[
  {
    "id": "60d...",
    "name": "High Priority Follow-up",
    "trigger_form_title": "Incident Report Form",
    "is_active": true,
    "action_count": 1
  }
]
```

---

### PUT /<id>

**Description**: Updates an existing workflow configuration, including its status, conditions, and actions.
**Auth Required**: Yes (Admin/Superadmin only)
**Examples**:

1. **Deactivation**: Disabling a workflow temporarily for maintenance.
2. **Condition Update**: Changing the threshold for triggering (e.g., from 'High' to 'Critical').
3. **Action Modification**: Adding an extra notification step.

**Curl Command**:

```bash
curl -X PUT http://localhost:5000/form/api/v1/workflows/60d... \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{"is_active": false}'
```

**Expected Output**:

```json
{
  "message": "Workflow updated"
}
```

---
*Security Note: Workflow conditions are parsed using `ast.parse` in 'eval' mode to prevent arbitrary code execution, ensuring safe processing of user-defined logic.*
