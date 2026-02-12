# Workflow Module Quick Reference

## API Endpoints

### Workflow Management
```
POST   /api/v1/workflows/              Create workflow
GET    /api/v1/workflows/              List all workflows
GET    /api/v1/workflows/?trigger_form_id={id}  Filter by form
GET    /api/v1/workflows/{id}          Get workflow details
PUT    /api/v1/workflows/{id}          Update workflow
DELETE /api/v1/workflows/{id}          Delete workflow
```

### Form Workflow
```
GET    /api/v1/forms/{id}/next-action                List workflows for form
GET    /api/v1/forms/{id}/next-action?response_id={rid}  Check triggered workflow
```

## Workflow Object

```json
{
  "name": "Workflow Name",
  "description": "Description",
  "trigger_form_id": "form-uuid",
  "trigger_condition": "answers.get('field') == 'value'",
  "is_active": true,
  "actions": [
    {
      "type": "redirect_to_form | create_draft | notify_user",
      "target_form_id": "target-form-uuid",
      "data_mapping": {
        "target_field": "source_field"
      },
      "assign_to_user_field": "user_field_or_id"
    }
  ]
}
```

## Action Types

### 1. redirect_to_form (Client-Side)
Redirects user to another form with pre-filled data.

```json
{
  "type": "redirect_to_form",
  "target_form_id": "form-uuid",
  "data_mapping": {
    "new_field": "old_field",
    "ref_id": "id"
  }
}
```

### 2. create_draft (Server-Side)
Automatically creates a draft in target form.

```json
{
  "type": "create_draft",
  "target_form_id": "form-uuid",
  "data_mapping": {
    "field1": "source_field1"
  },
  "assign_to_user_field": "approver_id"
}
```

### 3. notify_user (Server-Side)
Sends email notification to user.

```json
{
  "type": "notify_user",
  "assign_to_user_field": "supervisor_id"
}
```

## Condition Syntax

### Simple Conditions
```python
answers.get('priority') == 'high'
answers.get('status') == 'approved'
```

### Numeric Comparisons
```python
int(answers.get('age', 0)) >= 18
int(answers.get('score', 0)) > 80
```

### Boolean Logic
```python
answers.get('consent') == 'yes' and int(answers.get('age', 0)) >= 18
answers.get('priority') == 'high' or answers.get('urgent') == 'true'
```

### String Operations
```python
'urgent' in answers.get('description', '').lower()
answers.get('email', '').endswith('@company.com')
```

### List Membership
```python
'emergency' in answers.get('incident_type', [])
'option1' in answers.get('checkbox_field', [])
```

### Always Trigger
```python
True
```

## Data Mapping

### Special Fields
```json
{
  "ref_id": "id",                    // Response UUID
  "timestamp": "submitted_at",       // ISO timestamp
  "user": "submitted_by",            // User ID
  "form_version": "version"          // Form version
}
```

### Direct Field Mapping
```json
{
  "new_name": "old_name",
  "priority": "priority"
}
```

### Nested Field Access
```json
{
  "detail": "data.section1.description",
  "value": "data.responses.amount"
}
```

## Form Submission with Workflow

### Request
```bash
POST /api/v1/forms/{form_id}/responses
```

### Response (Workflow Triggered)
```json
{
  "message": "Response submitted",
  "response_id": "uuid",
  "workflow_action": {
    "workflow_id": "uuid",
    "workflow_name": "Workflow Name",
    "actions": [...]
  }
}
```

### Response (No Workflow)
```json
{
  "message": "Response submitted",
  "response_id": "uuid"
}
```

## Frontend Integration

### Check for Workflow After Submission
```javascript
const response = await submitForm(formData);

if (response.workflow_action) {
  const action = response.workflow_action.actions[0];

  if (action.type === 'redirect_to_form') {
    // Map data and navigate
    const mappedData = mapData(formData, action.data_mapping);
    router.push({
      path: `/forms/${action.target_form_id}`,
      query: { prefill: JSON.stringify(mappedData) }
    });
  }
}
```

### List Available Workflows
```javascript
const response = await fetch(
  `/api/v1/forms/${formId}/next-action`,
  { headers: { Authorization: `Bearer ${token}` } }
);

const { workflows } = await response.json();
console.log(`${workflows.length} workflows configured`);
```

## Common Patterns

### Multi-Step Registration
```json
{
  "name": "Step 2 Redirect",
  "trigger_form_id": "step-1-form",
  "trigger_condition": "True",
  "actions": [{
    "type": "redirect_to_form",
    "target_form_id": "step-2-form",
    "data_mapping": {
      "name": "name",
      "email": "email",
      "step1_id": "id"
    }
  }]
}
```

### Conditional Escalation
```json
{
  "name": "High Priority Escalation",
  "trigger_form_id": "incident-form",
  "trigger_condition": "answers.get('priority') == 'high'",
  "actions": [{
    "type": "create_draft",
    "target_form_id": "escalation-form",
    "data_mapping": {
      "incident_id": "id",
      "description": "description"
    },
    "assign_to_user_field": "supervisor_id"
  }]
}
```

### Automatic Notification
```json
{
  "name": "Manager Notification",
  "trigger_form_id": "request-form",
  "trigger_condition": "int(answers.get('amount', 0)) > 1000",
  "actions": [{
    "type": "notify_user",
    "assign_to_user_field": "manager_id"
  }]
}
```

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Invalid condition syntax | Check Python syntax |
| 403 | Unauthorized | Requires admin role |
| 404 | Workflow/Form not found | Verify IDs |
| 409 | Duplicate workflow | Change name/trigger |

## Testing Commands

### Create Workflow
```bash
curl -X POST http://localhost:5000/form/api/v1/workflows/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

### List Workflows
```bash
curl -X GET http://localhost:5000/form/api/v1/workflows/ \
  -H "Authorization: Bearer $TOKEN"
```

### Check Next Action
```bash
curl -X GET "http://localhost:5000/form/api/v1/forms/$FORM_ID/next-action?response_id=$RESPONSE_ID" \
  -H "Authorization: Bearer $TOKEN"
```

## Debug Checklist

- [ ] Workflow is active (`is_active: true`)
- [ ] trigger_form_id matches form ID exactly
- [ ] Condition syntax is valid Python
- [ ] Field names in condition exist in form
- [ ] User has admin/superadmin role
- [ ] Target form exists (for redirect/create_draft)
- [ ] Check server logs for errors

## Logs

Check: `/path/to/backend/logs/app.log`

Look for:
- `--- Create Workflow branch started ---`
- `Workflow created successfully`
- `Workflow {id} triggered for response {rid}`
- `Error evaluating workflow`

## Performance Tips

1. Use simple conditions when possible
2. Index frequently-queried fields
3. Limit number of workflows per form
4. Use `is_active: false` instead of delete for audit
5. Monitor workflow execution frequency

## Security Notes

- Conditions are sandboxed (AST parse only)
- No file system access
- No network requests from conditions
- Admin-only workflow management
- All actions logged for audit

---

**Last Updated:** February 11, 2026
**Version:** 1.0
