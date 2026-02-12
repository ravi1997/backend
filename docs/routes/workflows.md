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

### GET /<id>

**Description**: Retrieves detailed information about a specific workflow configuration.
**Auth Required**: Yes (Admin/Superadmin only)
**Path Parameters**:

- `id` (Required): Workflow UUID
**Examples**:

1. **View Configuration**: Inspect workflow rules and actions.
2. **Debugging**: Verify condition syntax and data mappings.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/workflows/60d... \
     -H "Authorization: Bearer <admin_token>"
```

**Expected Output**:

```json
{
  "id": "60d...",
  "name": "High Priority Follow-up",
  "description": "Triggered when a critical issue is reported",
  "trigger_form_id": "60d5f...",
  "trigger_condition": "response['priority'] == 'High'",
  "is_active": true,
  "actions": [
    {
      "type": "create_draft",
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

---

### DELETE /<id>

**Description**: Permanently deletes a workflow configuration.
**Auth Required**: Yes (Admin/Superadmin only)
**Path Parameters**:

- `id` (Required): Workflow UUID
**Examples**:

1. **Cleanup**: Remove outdated or unused workflows.
2. **Decommission**: Delete workflows after process changes.

**Curl Command**:

```bash
curl -X DELETE http://localhost:5000/form/api/v1/workflows/60d... \
     -H "Authorization: Bearer <admin_token>"
```

**Expected Output**:

```json
{
  "message": "Workflow deleted"
}
```

---

## Form Workflow Endpoints

### GET /form/api/v1/forms/<form_id>/next-action

**Description**: Checks if any active workflows should be triggered for a specific form or form submission. This endpoint is primarily used by the frontend to determine the next action after form submission.
**Auth Required**: Yes (Authenticated user)
**Path Parameters**:

- `form_id` (Required): Form UUID
**Query Parameters**:

- `response_id` (Optional): Specific response UUID to check workflows against

**Behavior**:
1. **Without response_id**: Returns a list of all active workflows configured for the form
2. **With response_id**: Evaluates all active workflows against the response data and returns the first matching workflow action

**Examples**:

1. **List Available Workflows**: Check which workflows are configured for a form
   ```bash
   curl -X GET http://localhost:5000/form/api/v1/forms/607d.../next-action \
        -H "Authorization: Bearer <token>"
   ```

2. **Check Triggered Workflow**: After form submission, check which workflow was triggered
   ```bash
   curl -X GET "http://localhost:5000/form/api/v1/forms/607d.../next-action?response_id=608e..." \
        -H "Authorization: Bearer <token>"
   ```

**Expected Output (No response_id)**:

```json
{
  "form_id": "607d...",
  "workflows": [
    {
      "id": "60d...",
      "name": "High Priority Follow-up",
      "description": "Triggered when a critical issue is reported",
      "condition": "response['priority'] == 'High'"
    },
    {
      "id": "60e...",
      "name": "Standard Processing",
      "description": "Default workflow for all submissions",
      "condition": "True"
    }
  ],
  "count": 2
}
```

**Expected Output (With response_id - Workflow Triggered)**:

```json
{
  "form_id": "607d...",
  "response_id": "608e...",
  "workflow_action": {
    "workflow_id": "60d...",
    "workflow_name": "High Priority Follow-up",
    "matched_condition": "response['priority'] == 'High'",
    "actions": [
      {
        "type": "redirect_to_form",
        "target_form_id": "609f...",
        "data_mapping": {
          "incident_id": "id",
          "description": "data.issue_description",
          "reporter": "submitted_by"
        },
        "assign_to_user_field": null
      }
    ]
  }
}
```

**Expected Output (With response_id - No Workflow Triggered)**:

```json
{
  "form_id": "607d...",
  "response_id": "608e...",
  "workflow_action": null
}
```

---

## Workflow Action Types

### 1. redirect_to_form

Redirects the user to another form after successful submission. Data from the original submission can be mapped to pre-fill fields in the target form.

**Use Cases**:
- Multi-step registration processes
- Sequential data collection
- Follow-up questionnaires

**Configuration**:
```json
{
  "type": "redirect_to_form",
  "target_form_id": "target-form-uuid",
  "data_mapping": {
    "target_field_1": "source_field_1",
    "target_field_2": "data.section1.field2",
    "target_field_3": "submitted_by"
  }
}
```

**Data Mapping Sources**:
- `"field_uuid"` - Direct field value from flattened response data
- `"data.section.field"` - Nested field access
- `"id"` - Response ID
- `"submitted_by"` - User who submitted
- `"submitted_at"` - Submission timestamp

---

### 2. create_draft

Automatically creates a draft response in another form with data pre-filled from the original submission.

**Use Cases**:
- Approval workflows
- Task creation from reports
- Follow-up form generation

**Configuration**:
```json
{
  "type": "create_draft",
  "target_form_id": "target-form-uuid",
  "data_mapping": {
    "reference_id": "id",
    "original_data": "data.key_info"
  },
  "assign_to_user_field": "approver_id"
}
```

**assign_to_user_field**: Can reference a field in the source form that contains the user ID who should receive the draft.

---

### 3. notify_user

Sends a notification to specified users when the workflow is triggered.

**Use Cases**:
- Escalation alerts
- Assignment notifications
- Status updates

**Configuration**:
```json
{
  "type": "notify_user",
  "target_form_id": null,
  "data_mapping": {},
  "assign_to_user_field": "supervisor_id"
}
```

---

## Workflow Trigger Conditions

Workflow conditions are Python expressions evaluated against the submitted response data. The expression must return a boolean value.

### Available Context Variables

- `answers` - Dictionary of flattened response data (all fields from all sections)
- `data` - Alias for `answers`

### Condition Examples

**Simple equality check**:
```python
answers['priority'] == 'High'
```

**Multiple conditions**:
```python
answers['age'] >= 18 and answers['consent'] == 'yes'
```

**Numeric comparisons**:
```python
int(answers['score']) > 80
```

**String operations**:
```python
'urgent' in answers['description'].lower()
```

**List membership**:
```python
'option1' in answers['checkbox_field']
```

**Always trigger**:
```python
True
```

### Safety Features

- Conditions are parsed using `ast.parse` in 'eval' mode to prevent arbitrary code execution
- Only safe mathematical and logical operations are allowed
- Access to built-in dangerous functions is restricted
- Execution is sandboxed through the `execute_safe_script` utility

---

## Integration with Form Submission

When a form is submitted through the `/api/v1/forms/<form_id>/responses` endpoint, the workflow evaluation happens automatically:

1. **Response is validated and saved**
2. **Active workflows are queried** for the form
3. **Conditions are evaluated** against the response data
4. **First matching workflow is executed** (workflows are evaluated in order)
5. **Workflow action is returned** in the response payload

### Response Payload with Workflow

```json
{
  "message": "Response submitted",
  "response_id": "608e...",
  "workflow_action": {
    "workflow_id": "60d...",
    "workflow_name": "High Priority Follow-up",
    "actions": [...]
  }
}
```

### Frontend Integration

The frontend should:

1. **Check response for workflow_action** after submission
2. **Execute the appropriate action**:
   - `redirect_to_form`: Navigate to the target form with pre-filled data
   - `create_draft`: Show success message indicating draft was created
   - `notify_user`: Show notification confirmation
3. **Handle data mapping** by extracting values from the original submission

**Example Frontend Code**:
```javascript
// After form submission
const response = await submitForm(formData);

if (response.workflow_action) {
  const action = response.workflow_action.actions[0];

  if (action.type === 'redirect_to_form') {
    // Build pre-fill data from data_mapping
    const prefillData = {};
    for (const [targetField, sourceField] of Object.entries(action.data_mapping)) {
      prefillData[targetField] = getValueFromPath(formData, sourceField);
    }

    // Navigate to target form
    router.push({
      path: `/forms/${action.target_form_id}`,
      query: { prefill: JSON.stringify(prefillData) }
    });
  }
}
```

---

## Example: Multi-Step Patient Registration Workflow

### Step 1: Create Primary Registration Form
Form ID: `patient-reg-001`
Fields:
- `patient_name` (text)
- `age` (number)
- `emergency_case` (checkbox)

### Step 2: Create Follow-up Forms
- Emergency Form ID: `emergency-protocol-001`
- Standard Form ID: `standard-admission-001`

### Step 3: Create Workflows

**Emergency Workflow**:
```json
{
  "name": "Emergency Protocol",
  "trigger_form_id": "patient-reg-001",
  "trigger_condition": "'emergency' in answers.get('emergency_case', [])",
  "actions": [{
    "type": "redirect_to_form",
    "target_form_id": "emergency-protocol-001",
    "data_mapping": {
      "patient_name": "patient_name",
      "patient_age": "age",
      "registration_id": "id"
    }
  }]
}
```

**Standard Workflow**:
```json
{
  "name": "Standard Admission",
  "trigger_form_id": "patient-reg-001",
  "trigger_condition": "'emergency' not in answers.get('emergency_case', [])",
  "actions": [{
    "type": "redirect_to_form",
    "target_form_id": "standard-admission-001",
    "data_mapping": {
      "patient_name": "patient_name",
      "patient_age": "age",
      "registration_id": "id"
    }
  }]
}
```

### Result

When a user submits the patient registration form:
- If "emergency" checkbox is checked → Redirected to emergency protocol form with pre-filled data
- If not checked → Redirected to standard admission form with pre-filled data

---

*Security Note: Workflow conditions are parsed using `ast.parse` in 'eval' mode to prevent arbitrary code execution, ensuring safe processing of user-defined logic.*
