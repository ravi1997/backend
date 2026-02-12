# Workflow Module Testing Guide

This guide provides step-by-step instructions for manually testing the workflow module functionality.

## Prerequisites

1. Backend server running on `http://localhost:5000`
2. Admin user credentials
3. REST client (Postman, curl, or similar)

## Test Scenarios

### Scenario 1: Create and Test a Simple Workflow

#### Step 1: Create Primary Form

**Endpoint:** `POST /form/api/v1/forms/`

**Request:**
```json
{
  "title": "Incident Report",
  "description": "Primary incident reporting form",
  "slug": "incident-report",
  "status": "published",
  "ui": "flex",
  "versions": [{
    "version": "1.0",
    "sections": [{
      "id": "incident-details",
      "title": "Incident Details",
      "ui": "flex",
      "order": 1,
      "questions": [
        {
          "id": "priority",
          "label": "Priority Level",
          "field_type": "select",
          "is_required": true,
          "order": 1,
          "options": [
            {"option_label": "High", "option_value": "high", "order": 1},
            {"option_label": "Medium", "option_value": "medium", "order": 2},
            {"option_label": "Low", "option_value": "low", "order": 3}
          ]
        },
        {
          "id": "description",
          "label": "Incident Description",
          "field_type": "textarea",
          "is_required": true,
          "order": 2
        },
        {
          "id": "reporter_name",
          "label": "Reporter Name",
          "field_type": "input",
          "is_required": true,
          "order": 3
        }
      ]
    }]
  }]
}
```

**Expected Response:** Form ID (save this as `PRIMARY_FORM_ID`)

#### Step 2: Create Follow-up Form

**Endpoint:** `POST /form/api/v1/forms/`

**Request:**
```json
{
  "title": "High Priority Follow-up",
  "description": "Follow-up form for high priority incidents",
  "slug": "high-priority-followup",
  "status": "published",
  "ui": "flex",
  "versions": [{
    "version": "1.0",
    "sections": [{
      "id": "followup-details",
      "title": "Follow-up Details",
      "ui": "flex",
      "order": 1,
      "questions": [
        {
          "id": "original_incident_id",
          "label": "Original Incident ID",
          "field_type": "input",
          "is_required": true,
          "order": 1
        },
        {
          "id": "original_priority",
          "label": "Original Priority",
          "field_type": "input",
          "is_required": true,
          "order": 2
        },
        {
          "id": "action_taken",
          "label": "Action Taken",
          "field_type": "textarea",
          "is_required": true,
          "order": 3
        }
      ]
    }]
  }]
}
```

**Expected Response:** Form ID (save this as `TARGET_FORM_ID`)

#### Step 3: Create Workflow

**Endpoint:** `POST /form/api/v1/workflows/`

**Request:**
```json
{
  "name": "High Priority Escalation",
  "description": "Automatically redirect to follow-up form when priority is high",
  "trigger_form_id": "PRIMARY_FORM_ID",
  "trigger_condition": "answers.get('priority') == 'high'",
  "is_active": true,
  "actions": [
    {
      "type": "redirect_to_form",
      "target_form_id": "TARGET_FORM_ID",
      "data_mapping": {
        "original_incident_id": "id",
        "original_priority": "priority"
      },
      "assign_to_user_field": null
    }
  ]
}
```

**Expected Response:**
```json
{
  "message": "Workflow created",
  "id": "WORKFLOW_ID"
}
```

Save the `WORKFLOW_ID` for later tests.

#### Step 4: Test Workflow Trigger (High Priority)

**Endpoint:** `POST /form/api/v1/forms/{PRIMARY_FORM_ID}/responses`

**Request:**
```json
{
  "data": {
    "incident-details": {
      "priority": "high",
      "description": "Critical system outage detected",
      "reporter_name": "John Doe"
    }
  }
}
```

**Expected Response:**
```json
{
  "message": "Response submitted",
  "response_id": "RESPONSE_ID",
  "workflow_action": {
    "workflow_id": "WORKFLOW_ID",
    "workflow_name": "High Priority Escalation",
    "actions": [
      {
        "type": "redirect_to_form",
        "target_form_id": "TARGET_FORM_ID",
        "data_mapping": {
          "original_incident_id": "id",
          "original_priority": "priority"
        },
        "assign_to_user_field": null
      }
    ]
  }
}
```

**Verification:**
- `workflow_action` should be present
- `workflow_name` should be "High Priority Escalation"
- Actions array should contain the redirect action

#### Step 5: Test Workflow NOT Triggered (Low Priority)

**Endpoint:** `POST /form/api/v1/forms/{PRIMARY_FORM_ID}/responses`

**Request:**
```json
{
  "data": {
    "incident-details": {
      "priority": "low",
      "description": "Minor UI glitch",
      "reporter_name": "Jane Smith"
    }
  }
}
```

**Expected Response:**
```json
{
  "message": "Response submitted",
  "response_id": "RESPONSE_ID_2"
}
```

**Verification:**
- `workflow_action` should NOT be present (or be null)
- This confirms the condition is being evaluated correctly

#### Step 6: Test Next-Action Endpoint (List Workflows)

**Endpoint:** `GET /form/api/v1/forms/{PRIMARY_FORM_ID}/next-action`

**Expected Response:**
```json
{
  "form_id": "PRIMARY_FORM_ID",
  "workflows": [
    {
      "id": "WORKFLOW_ID",
      "name": "High Priority Escalation",
      "description": "Automatically redirect to follow-up form when priority is high",
      "condition": "answers.get('priority') == 'high'"
    }
  ],
  "count": 1
}
```

**Verification:**
- Should return list of all active workflows for the form

#### Step 7: Test Next-Action Endpoint (Evaluate Response)

**Endpoint:** `GET /form/api/v1/forms/{PRIMARY_FORM_ID}/next-action?response_id={RESPONSE_ID}`

(Use RESPONSE_ID from Step 4 - the high priority submission)

**Expected Response:**
```json
{
  "form_id": "PRIMARY_FORM_ID",
  "response_id": "RESPONSE_ID",
  "workflow_action": {
    "workflow_id": "WORKFLOW_ID",
    "workflow_name": "High Priority Escalation",
    "matched_condition": "answers.get('priority') == 'high'",
    "actions": [
      {
        "type": "redirect_to_form",
        "target_form_id": "TARGET_FORM_ID",
        "data_mapping": {
          "original_incident_id": "id",
          "original_priority": "priority"
        },
        "assign_to_user_field": null
      }
    ]
  }
}
```

**Verification:**
- Should return the matched workflow action
- `matched_condition` should show which condition matched

#### Step 8: Test Workflow Update

**Endpoint:** `PUT /form/api/v1/workflows/{WORKFLOW_ID}`

**Request:**
```json
{
  "description": "Updated: Escalate high priority incidents immediately",
  "trigger_condition": "answers.get('priority') == 'high' or answers.get('priority') == 'medium'"
}
```

**Expected Response:**
```json
{
  "message": "Workflow updated"
}
```

**Verification:**
- Workflow should now trigger for both high AND medium priority
- Test by submitting a medium priority incident

#### Step 9: Test Workflow Deactivation

**Endpoint:** `PUT /form/api/v1/workflows/{WORKFLOW_ID}`

**Request:**
```json
{
  "is_active": false
}
```

**Expected Response:**
```json
{
  "message": "Workflow updated"
}
```

**Verification:**
- Submit a high priority incident
- Workflow should NOT trigger (no `workflow_action` in response)

### Scenario 2: Complex Workflow with Data Mapping

#### Step 1: Create Workflow with Complex Mapping

**Request:**
```json
{
  "name": "Patient Registration Workflow",
  "trigger_form_id": "PATIENT_REG_FORM_ID",
  "trigger_condition": "int(answers.get('age', 0)) >= 65",
  "is_active": true,
  "actions": [
    {
      "type": "create_draft",
      "target_form_id": "SENIOR_CARE_FORM_ID",
      "data_mapping": {
        "patient_name": "patient_name",
        "patient_age": "age",
        "registration_date": "submitted_at",
        "registration_id": "id",
        "emergency_contact": "emergency_phone"
      },
      "assign_to_user_field": "assigned_doctor"
    }
  ]
}
```

**Condition Explanation:**
- `int(answers.get('age', 0)) >= 65` - Triggers only for patients 65 or older
- Uses type conversion and default value for safety

**Data Mapping:**
- Maps multiple fields from source to target form
- Can map special fields like `id`, `submitted_at`, `submitted_by`
- Can map nested fields using dot notation

### Scenario 3: Testing Multiple Workflows

#### Create Multiple Workflows for Same Form

1. **High Priority Workflow** (condition: `priority == 'high'`)
2. **Medium Priority Workflow** (condition: `priority == 'medium'`)
3. **Default Workflow** (condition: `True`)

**Expected Behavior:**
- Only the FIRST matching workflow is triggered
- Workflows are evaluated in the order they were created
- If high priority workflow matches, medium and default won't execute

## Testing Condition Syntax

### Valid Conditions

```python
# Simple equality
answers.get('status') == 'approved'

# Numeric comparison
int(answers.get('age', 0)) >= 18

# String operations
'urgent' in answers.get('description', '').lower()

# Boolean logic
answers.get('consent') == 'yes' and int(answers.get('age', 0)) >= 18

# List membership (for checkbox fields)
'emergency' in answers.get('incident_type', [])

# Always trigger
True
```

### Invalid Conditions (Should Fail Validation)

```python
# Import statements (not allowed)
import os; answers.get('status')

# Function calls beyond safe list
eval("malicious code")

# File operations
open('/etc/passwd')
```

## Common Issues and Solutions

### Issue 1: Workflow Not Triggering

**Symptoms:**
- Form submission succeeds but no `workflow_action` in response

**Troubleshooting:**
1. Check workflow is active: `is_active: true`
2. Verify trigger_form_id matches your form ID exactly
3. Test condition syntax is valid
4. Check condition evaluates to True for your test data
5. Verify field IDs in condition match actual question IDs

**Debug Steps:**
```bash
# Get workflow details
GET /form/api/v1/workflows/{WORKFLOW_ID}

# Check available workflows for form
GET /form/api/v1/forms/{FORM_ID}/next-action

# Check response data structure
GET /form/api/v1/forms/{FORM_ID}/responses/{RESPONSE_ID}
```

### Issue 2: Data Mapping Not Working

**Symptoms:**
- Workflow triggers but target form fields not pre-filled

**Troubleshooting:**
1. Verify field IDs in `data_mapping` match actual question IDs
2. Check source field exists in response data
3. Verify target form has fields with specified IDs
4. Check data types are compatible

**Correct Mapping:**
```json
{
  "data_mapping": {
    "target_field_id": "source_field_id",
    "another_target": "id",
    "timestamp_field": "submitted_at"
  }
}
```

### Issue 3: Condition Syntax Error

**Symptoms:**
- Workflow creation fails with "Invalid python syntax in trigger_condition"

**Solution:**
- Use Python expression syntax
- Always use `answers.get('field_id')` to safely access fields
- Provide default values: `answers.get('age', 0)`
- Test condition in Python REPL before using

## Performance Testing

### Test Large Number of Workflows

1. Create 20+ workflows with different conditions
2. Submit form and measure response time
3. Expected: Response time should remain under 500ms

### Test Complex Conditions

1. Create workflow with complex nested conditions
2. Test with various input data
3. Verify condition evaluation is correct

## Security Testing

### Test Malicious Conditions

Try to create workflows with dangerous code:

```json
{
  "trigger_condition": "import os; os.system('rm -rf /')"
}
```

**Expected:** Should fail validation with syntax error

### Test SQL Injection in Data Mapping

```json
{
  "data_mapping": {
    "field": "'; DROP TABLE users; --"
  }
}
```

**Expected:** Should be stored as literal string, not executed

## Cleanup

After testing, clean up test data:

```bash
# Delete workflows
DELETE /form/api/v1/workflows/{WORKFLOW_ID}

# Delete test forms
DELETE /form/api/v1/forms/{FORM_ID}
```

## Automated Testing

For automated testing, use the provided test script:

```bash
python test_workflow_integration.py
```

This will:
1. Create test forms
2. Create test workflows
3. Run all test scenarios
4. Verify expected behavior
5. Clean up test data
6. Generate test report

## Expected Success Criteria

All tests should pass with:
- ✓ Workflow CRUD operations working
- ✓ Trigger conditions evaluated correctly
- ✓ Actions returned in response payload
- ✓ Data mapping structure correct
- ✓ Next-action endpoint functional
- ✓ Security validations in place
- ✓ No errors in server logs

## Troubleshooting Server Logs

Check backend logs for detailed error messages:

```bash
tail -f /path/to/backend/logs/app.log
```

Look for:
- Workflow evaluation logs
- Condition syntax errors
- Action execution logs
- Error stack traces
