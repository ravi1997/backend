# detailed Implementation Plan: Advanced Dashboards & Workflows

## 1. Gap Analysis & Objectives

Based on the user's request and the current SRS/Status, the core Form Management and Data Collection features are **present** and **complete**. However, specifically requested features regarding **"Multiple Views/Dashboards"** and **"Structured Multi-Form Workflows"** are either missing or only partially supported via basic API lookups.

### Missing Features Identified:
1.  **Custom Views & Dashboards**: The current `SavedSearch` is strictly for filtering response lists. There is no concept of a "Dashboard" entity that aggregates multiple views, counts, or charts into a single page for specific user roles (e.g., "Data Entry Operator Dashboard" vs "Admin Dashboard").
2.  **Form Linking & Workflow Orchestration**: While `FR-API-003` allows *pulling* data from another form, there is no orchestrated *push* or *flow* (e.g., "After submitting Registration, immediately open Admission Form with data pre-filled").

---

## 2. Module 1: Dynamic Dashboards & Views Configuration

**Objective**: Allow the creation of role-specific dashboards that display tailored views of form data (e.g., "Today's Patients", "My Pending Entries").

### 2.1 New Data Models

#### `Dashboard`
Represents a configured view page assignable to roles.

```python
class Dashboard(Document):
    title = StringField(required=True)
    slug = StringField(required=True, unique=True)
    description = StringField()
    roles = ListField(StringField()) # Roles that can access this dashboard (e.g., ['deo', 'doctor'])
    layout = StringField(default="grid") # grid, list
    widgets = ListField(EmbeddedDocumentField('DashboardWidget'))
    created_by = ReferenceField('User')
    created_at = DateTimeField(default=datetime.utcnow)
```

#### `DashboardWidget`
A single component within a dashboard.

```python
class DashboardWidget(EmbeddedDocument):
    id = UUIDField(default=uuid.uuid4)
    title = StringField()
    type = StringField(choices=('counter', 'list_view', 'chart_bar', 'chart_pie', 'shortcut'))
    
    # Data Source Configuration
    form_ref = ReferenceField('Form')
    saved_search_ref = ReferenceField('SavedSearch') # Reuse existing SavedSearch logic
    
    # Display Configuration
    size = StringField(choices=('small', 'medium', 'large', 'full_width'))
    refresh_interval = IntField(default=300) # Seconds
    
    # For 'counter' type:
    aggregation_field = StringField() # e.g., "count(*)" or "sum(amount)"
    
    # For 'list_view' type:
    display_columns = ListField(StringField()) # Fields to show in table
    
    # For 'shortcut' type:
    target_link = StringField() # e.g., "/forms/registration/new"
```

### 2.2 New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/dashboards/` | Create a new Dashboard definition |
| `GET` | `/api/v1/dashboards/` | List dashboards available to current user's role |
| `GET` | `/api/v1/dashboards/{id}` | Get full dashboard config with widget data |
| `PUT` | `/api/v1/dashboards/{id}` | Update dashboard layout/widgets |
| `POST` | `/api/v1/dashboards/{id}/widgets` | Add widget to dashboard |

### 2.3 Implementation Details
1.  **Widget Data Resolution**: usage of the existing `Search Response` logic. When a dashboard is loaded, the backend or frontend iterates through widgets. For `list_view` widgets, it runs the associated `SavedSearch` query and returns the top N results.
2.  **Role Access**: Middleware check to ensure user has one of the `roles` allowed for the requested dashboard.

---

## 3. Module 2: Advanced Form Workflows (Primary/Secondary Forms)

**Objective**: Enable "Registration -> Admission" flows where submitting one form triggers actions for another, including data mapping.

### 3.1 New Data Model: `FormWorkflow`

This entity defines the relationship and transition between forms.

```python
class FormWorkflow(Document):
    name = StringField(required=True)
    trigger_form = ReferenceField('Form', required=True) # The "Primary" form
    trigger_condition = StringField() # Python-expression, e.g., "'admit' in answers.get('disposition')"
    
    actions = ListField(EmbeddedDocumentField('WorkflowAction'))
    is_active = BooleanField(default=True)

class WorkflowAction(EmbeddedDocument):
    type = StringField(choices=('redirect_to_form', 'create_draft', 'notify_user'))
    
    # For 'redirect_to_form' / 'create_draft':
    target_form = ReferenceField('Form')
    
    # Data Mapping: Target Field -> Source Field/Expression
    # Example: {"patient_name": "name", "uhid": "uhid", "reg_date": "submitted_at"}
    data_mapping = DictField() 
    
    # User Assignment (for 'create_draft')
    assign_to_user_field = StringField() # e.g., "treating_doctor_id"
```

### 3.2 Enhanced Form Submission Logic
Modify `FR-RESP-001 (Submit Response)` to evaluate workflows post-submission:

1.  **Post-Process Hook**: After a successful save of Form A response.
2.  **Evaluate Triggers**: Find all `FormWorkflow` docs where `trigger_form == Form A`.
3.  **Check Condition**: If `trigger_condition` evaluates to True (or is empty).
4.  **Execute Actions**:
    *   **Redirect**: Return a specific response payload to the frontend: `{ "status": "success", "next_action": "redirect", "target_url": "/forms/{B}/new?prefill_id={response_A_id}" }`.
    *   **Pre-fill API**: The "New Response" API for Form B must accept `?prefill_id={response_A_id}` and `?workflow_id={id}` to automatically execute the `data_mapping` and populate fields.

### 3.3 API Updates

*   **Update `POST /api/v1/form/{id}/responses`**: Return `workflow_actions` in response body.
*   **New `POST /api/v1/workflow/`**: Create workflows.
*   **Update `GET /api/v1/form/{id}/structure`**: Allow passing `prefill_source_response_id` to resolve creating a submission based on a previous form.

---

## 4. Execution Roadmap

### Phase 1: Dashboard Foundation (Week 1)
1.  Implement `Dashboard` and `DashboardWidget` models.
2.  Create CRUD endpoints for Dashboards.
3.  Implement "Widget Data Resolver" service to fetch filtered data from `FormResponse` collection based on widget config.

### Phase 2: Workflow Engine (Week 2)
1.  Implement `FormWorkflow` model.
2.  Implement `WorkflowEvaluator` service in the Response Submission pipeline.
3.  Update Form Submission controller to return "Next Action" instructions.
4.  Implement Data Mapping logic in `FormService.get_initial_data()`.

### Phase 3: Integration & Testing (Week 3)
1.  Connect "Saved Searches" to "Dashboard Widgets".
2.  Test "Patient Registration" -> "Admission" flow (Auto-fill).
3.  Validate Role-based dashboard access (Admin vs DEO views).
