# Frontend SRS - Part 2: Functional Requirements (Sections 4-7)

## 4. Functional Requirements

### 4.1 Authentication Module

#### FR-FRONT-AUTH-01: Multi-Method Login
**Description:** Support multiple authentication methods based on user type.

| Attribute | Specification |
|-----------|---------------|
| **Input (Employee)** | Email/Username/EmployeeID + Password |
| **Input (General)** | Mobile + OTP (6 digits) |
| **Process** | POST to `/api/v1/auth/login` → Store JWT in HttpOnly cookie or memory → Update Zustand `authStore` |
| **UI Components** | LoginForm, OTPInput, PasswordInput with show/hide toggle |
| **Validation** | Required fields, email format, password min 8 chars |
| **Error Handling** | 401 → "Invalid credentials", 423 → "Account locked" |
| **Success** | Redirect to intended page or `/dashboard` |

**Business Rules:**
- Remember last login method (localStorage)
- Auto-redirect authenticated users away from `/login`
- Display account lock countdown if locked
- Support "Remember Me" (extended token expiry)

---

#### FR-FRONT-AUTH-02: User Registration
**Description:** Self-service registration for employee users.

| Attribute | Specification |
|-----------|---------------|
| **Input** | username, email, employee_id, mobile, password, confirm_password |
| **Validation (Client)** | Password strength (Zod), email uniqueness check (debounced API call) |
| **Process** | POST to `/api/v1/auth/register` → Show success toast → Redirect to login |
| **UI** | Multi-step wizard OR single scrollable form |
| **Password Requirements** | Min 8 chars, 1 uppercase, 1 number, 1 special char |

---

#### FR-FRONT-AUTH-03: OTP Flow
**Description:** Mobile-based OTP authentication.

| Step | Action | API | UI State |
|------|--------|-----|----------|
| 1 | User enters mobile | | Input active |
| 2 | Click "Send OTP" | POST `/api/v1/auth/generate-otp` | Button → Loading |
| 3 | OTP sent | | Show OTP input + timer (5:00) |
| 4 | User enters OTP | | 6-digit input boxes |
| 5 | Auto-submit on 6th digit | POST `/api/v1/auth/login` (otp) | Validating... |
| 6 | Success | | Redirect |

**Error Handling:**
- Invalid OTP → Shake animation + "Invalid code"
- Expired OTP → "Code expired. Request new one"
- Max attempts → "Too many attempts. Account locked for 24h"

---

#### FR-FRONT-AUTH-04: Session Management
**Description:** Maintain and validate user session.

**Initialization Flow:**
```typescript
// On app mount
async function initializeAuth() {
  const token = getTokenFromCookie() || getTokenFromMemory();
  if (!token) return redirectToLogin();
  
  try {
    const user = await api.get('/api/v1/user/status'); // FR-USER-001
    authStore.setUser(user);
    authStore.setAuthenticated(true);
  } catch (error) {
    if (error.status === 401) {
      clearAuth();
      redirectToLogin();
    }
  }
}
```

**Token Refresh:**
- No explicit refresh (backend handles via cookie)
- On 401, clear auth and redirect
- Optional: Silent token refresh if RT provided

---

#### FR-FRONT-AUTH-05: Logout
**Description:** Terminate user session.

| Attribute | Specification |
|-----------|---------------|
| **Trigger** | User menu → Logout button |
| **Process** | POST `/api/v1/auth/logout` → Clear authStore → Clear localStorage → Redirect to `/login` |
| **Confirmation** | Optional confirmation modal if unsaved work |

---

### 4.2 Dashboard Module

#### FR-FRONT-DASH-01: Role-Based Dashboard
**Description:** Display customized dashboard based on user role.

**Widget Types:**
| Widget | Data Source | Visualization | Refresh |
|--------|-------------|---------------|---------|
| **Stats Cards** | GET `/api/v1/dashboards/{id}` | Number + trend | Real-time |
| **Recent Forms** | GET `/api/v1/form/` (limit=5) | List | 5 min cache |
| **Pending Approvals** | GET `/api/v1/approvals/pending` | List + badge | Real-time |
| **Submission Chart** | GET `/api/v1/analytics/trends` | Line chart | 1 hour cache |
| **Quick Actions** | Static config | Button grid | N/A |

**Layout:**
- Grid system: 12 columns
- Responsive breakpoints: sm, md, lg, xl
- Drag-to-reorder (Admin only)

---

#### FR-FRONT-DASH-02: Form Management Grid
**Description:** Comprehensive form listing with actions.

**Columns:**
| Column | Width | Sortable | Filterable |
|--------|-------|----------|------------|
| Title | 30% | ✅ | ✅ (text search) |
| Status | 10% | ✅ | ✅ (dropdown) |
| Created | 15% | ✅ | ✅ (date range) |
| Responses | 10% | ✅ | ❌ |
| Actions | 10% | ❌ | ❌ |

**Actions Menu (Kebab):**
- 📝 Edit (if has edit permission)
- 👁️ Preview
- 📊 View Responses
- 🔗 Copy Link
- 📋 Clone
- 🗑️ Delete (with confirmation)

**Pagination:**
- Server-side pagination
- 10/25/50/100 per page options
- URL state sync (`?page=2&limit=25`)

---

### 4.3 Form Builder Module (Core)

#### FR-FRONT-BLDR-01: Drag-and-Drop System
**Description:** Visual form construction via drag-and-drop.

**Implementation:** Using `@dnd-kit/core`

**Droppable Zones:**
1. **Component Library** (Source)
2. **Canvas** (Target - Section containers)
3. **Trash** (Delete action)

**Drag Feedback:**
- Dragging: 50% opacity on source
- Drop zone: Blue highlight + insertion indicator
- Invalid drop: Red X cursor

**Keyboard Alternative:**
- Select field → Arrow keys to reorder
- Enter to edit
- Delete key to remove

---

#### FR-FRONT-BLDR-02: Field Type Library
**Description:** Complete catalog of supported field types.

| Category | Field Types | Icon | Backend Mapping |
|----------|-------------|------|-----------------|
| **Text** | Input, Textarea, Number | 📝 | `input`, `textarea` |
| **Choice** | Select, Radio, Checkbox | ☑️ | `select`, `radio`, `checkbox` |
| **Date/Time** | Date, Time, DateTime | 📅 | `date` |
| **Rating** | Stars (1-5) | ⭐ | `rating` |
| **Boolean** | Toggle, YesNo | 🔘 | `boolean` |
| **File** | File Upload, Image Upload | 📎 | `file_upload` |
| **Integration** | UHID Search, OTP Verify | 🔌 | `api_search` (uhid, otp) |
| **Advanced** | Calculated Field | 🔢 | `calculated` |
| **Layout** | Section, Divider | 📐 | Section model |

**Compound Components:**
- **Section**: Container with title, description, collapsible
- **Repeatable Section**: Section with +/- controls (min/max)

---

#### FR-FRONT-BLDR-03: Properties Panel
**Description:** Context-sensitive field configuration.

**Panels by Field Type:**

**Common Properties (All Fields):**
```typescript
{
  label: string;
  id: string; // Auto-generated UUID, read-only
  helpText?: string;
  placeholder?: string;
  defaultValue?: any;
  required: boolean;
  disabled: boolean;
  visibilityCondition?: string; // Expression editor
}
```

**Text Fields (Input, Textarea):**
```typescript
{
  minLength?: number;
  maxLength?: number;
  pattern?: string; // Regex with tester
}
```

**Choice Fields (Select, Radio, Checkbox):**
```typescript
{
  options: Array<{
    id: string;
    label: string;
    value: string;
    isDefault?: boolean;
    isDisabled?: boolean;
  }>;
  minSelections?: number; // Checkbox only
  maxSelections?: number; // Checkbox only
}
```

**File Upload:**
```typescript
{
  maxSize: number; // MB, default 10
  allowedTypes: string[]; // MIME types
  multiple: boolean;
}
```

**Integration Fields:**
```typescript
{
  apiType: 'uhid' | 'otp' | 'form' | 'custom';
  mappingConfig: Record<string, string>; // Source field → Target field
}
```

---

#### FR-FRONT-BLDR-04: Conditional Logic Builder
**Description:** Visual interface for visibility conditions.

**UI:**
```
[Show this field] IF [Question: Name] [equals] [value: "John"]
                     ↓ Dropdown      ↓ Operator  ↓ Input

Operators: equals, not equals, contains, greater than, less than, is empty, is not empty
```

**Complex Conditions:**
```
[Show] IF ( [Q1] = "Yes" AND [Q2] > 18 ) OR [Q3] is not empty
```

**Implementation:**
- Visual builder → Generated expression string
- Expression tester with mock data
- Validation: Prevent circular dependencies

---

#### FR-FRONT-BLDR-05: Preview Mode
**Description:** Toggle between edit and preview states.

| Mode | Canvas Behavior | Interactions | Purpose |
|------|-----------------|--------------|---------|
| **Edit** | Fields selectable, properties panel active | Click to select, drag to reorder | Form design |
| **Preview** | Fields interactive, no selection | Type, select, validate | Test form UX |

**Preview Features:**
- Full validation execution
- Conditional logic evaluation
- API integration testing (sandbox mode)
- Mock submission (no data saved)

---

#### FR-FRONT-BLDR-06: Version Management
**Description:** Form versioning UI.

**Version Dropdown:**
```
v2.0 (Active) ←Current
v1.5 (Draft)
v1.0
```

**Actions:**
- View version → Load schema into canvas (read-only)
- Create new version → Duplicate current + increment
- Restore version → Confirmation modal → Set as active

**Version Comparison:**
- Side-by-side diff view
- Highlight added/removed/modified fields
- Show response count per version

---

#### FR-FRONT-BLDR-07: Repeatable Sections/Questions
**Description:** UI for dynamic field repetition.

**Section-Level Repetition:**
```
┌─ Family Members (Repeatable: min=1, max=5) ─────┐
│  [Instance 1]                                    │
│    • Member Name: [_______]                      │
│    • Age: [___]                                  │
│  [+ Add Another Member]                          │
└──────────────────────────────────────────────────┘
```

**Question-Level Repetition:**
```
Phone Numbers (Repeatable)
1. [__________] [×]
2. [__________] [×]
[+ Add Phone Number]
```

**UI Controls:**
- Add button: Enabled if `count < max`
- Remove button: Enabled if `count > min`
- Reorder handles (drag icon)

---

### 4.4 Public Submission Module

#### FR-FRONT-PUB-01: Form Rendering Engine
**Description:** Dynamic form renderer from JSON schema.

**Route:** `/submit/[slug]`

**Rendering Strategy:**
- ISR with 60s revalidation
- Fallback: Loading skeleton
- Error: 404 page if form not found/expired

**Layout Components:**
```typescript
<PublicFormLayout>
  <FormHeader title={form.title} description={form.description} />
  <FormBody>
    {sections.map(section => (
      <Section key={section.id}>
        {section.questions.map(question => (
          <QuestionRenderer question={question} />
        ))}
      </Section>
    ))}
  </FormBody>
  <FormFooter>
    <SubmitButton />
  </FormFooter>
</PublicFormLayout>
```

---

#### FR-FRONT-PUB-02: Client-Side Validation
**Description:** Real-time validation before submission.

**Validation Triggers:**
- `onBlur`: Validate single field
- `onChange`: Clear error on valid input
- `onSubmit`: Validate entire form

**Zod Schema Generation:**
```typescript
// Dynamically generate from form schema
const schema = z.object({
  [questionId]: z.string()
    .min(minLength)
    .max(maxLength)
    .regex(pattern)
    .optional(!required)
});
```

**Error Display:**
```html
<Input />
<ErrorMessage>This field is required</ErrorMessage>
```

---

#### FR-FRONT-PUB-03: Draft Auto-Save
**Description:** Prevent data loss via auto-save.

**Implementation:**
```typescript
useEffect(() => {
  const timeout = setTimeout(() => {
    localStorage.setItem(`draft_${formId}`, JSON.stringify(formData));
  }, 1000); // Debounced 1s

  return () => clearTimeout(timeout);
}, [formData]);
```

**Draft Restoration:**
```typescript
onMount(() => {
  const draft = localStorage.getItem(`draft_${formId}`);
  if (draft) {
    showDialog({
      title: "Resume Draft?",
      message: "You have unsaved changes. Would you like to continue?",
      actions: ["Resume", "Start Fresh"]
    });
  }
});
```

---

#### FR-FRONT-PUB-04: File Upload Handler
**Description:** Async file upload with progress.

**Upload Flow:**
1. User selects file(s)
2. Client validates: size (<10MB), type (allowed MIME)
3. Upload to `/api/v1/form/{id}/files/{questionId}` (multipart)
4. Show progress bar
5. On success, store `filepath` in form data
6. On error, show error + retry option

**UI Components:**
```tsx
<FileUploadZone>
  {!file && <DropZone />}
  {uploading && <ProgressBar progress={uploadProgress} />}
  {file && <FilePreview file={file} onRemove={handleRemove} />}
</FileUploadZone>
```

**Multiple Files:**
- Array of file objects
- Individual progress bars
- Remove individual files

---

#### FR-FRONT-PUB-05: Integration: UHID Lookup
**Description:** Frontend for Backend FR-API-001 (eHospital UHID).

**UI Flow:**
```
UHID: [_____________] [🔍 Search]
      ↓ (API Call)
Found: Ravikumar, Age 35, Male
[Auto-fill Patient Details?] [Yes] [No]
```

**Implementation:**
```typescript
const handleUHIDSearch = async (uhid: string) => {
  setLoading(true);
  try {
    const data = await api.get(`/api/v1/form/${formId}/section/${sectionId}/question/${questionId}/api?value=${uhid}`);
    
    // Show confirmation dialog
    const confirmed = await confirm("Auto-fill patient details?");
    if (confirmed) {
      // Map API response to form fields
      mappingConfig.forEach(({ source, target }) => {
        setValue(target, data[source]);
      });
    }
  } catch (error) {
    toast.error("UHID not found");
  } finally {
    setLoading(false);
  }
};
```

---

#### FR-FRONT-PUB-06: Integration: SMS OTP Verification
**Description:** Frontend for Backend FR-API-002 (OTP).

**UI Flow:**
```
Mobile: [+91 __________] [Send OTP]
        ↓
OTP: [_] [_] [_] [_] [_] [_]  ⏱️ 4:32
     [Resend OTP] (disabled for 60s)
     ↓ (Auto-submit on 6th digit)
✅ Verified
```

**State Machine:**
```
IDLE → SENDING → OTP_SENT → VERIFYING → VERIFIED
                     ↓ Timeout (5 min)
                  EXPIRED
```

---

### 4.5 Response Management & Analytics

#### FR-FRONT-RESP-01: Advanced Data Grid
**Description:** TanStack Table with server-side features.

**Features:**
- Column visibility toggle
- Column resizing
- Column reordering (drag headers)
- Row selection (checkboxes)
- Bulk actions (delete, export selected)

**Implementation:**
```typescript
const columns: ColumnDef<Response>[] = [
  { id: 'select', header: Checkbox },
  { accessorKey: 'id', header: 'ID', size: 100 },
  { accessorKey: 'submitted_at', header: 'Date', cell: DateCell },
  { accessorKey: 'status', header: 'Status', cell: StatusBadge },
  ...dynamicQuestionColumns, // First 3 questions
  { id: 'actions', cell: ActionsCell }
];
```

---

#### FR-FRONT-RESP-02: Advanced Filtering
**Description:** Multi-criteria filter builder.

**Filter UI:**
```
[+ Add Filter]

Filters:
• [Submitted Date] [is between] [2026-01-01] and [2026-01-31]
• [Status] [equals] [Pending]
• [Question: Name] [contains] [John]

[Clear All] [Apply]
```

**Backend Mapping:**
```typescript
const filters = {
  date_range: { start: '2026-01-01', end: '2026-01-31' },
  status: 'pending',
  data: {
    [questionId]: { value: 'John', type: 'string', fuzzy: true }
  }
};

POST /api/v1/form/{id}/responses/search
```

---

#### FR-FRONT-RESP-03: Response Detail View
**Description:** Single response inspection and approval.

**Layout:**
```
┌─ Response Detail ────────────────────────────────┐
│ [← Back] #12345 | Submitted: 2026-01-09 10:30 AM │
├──────────────────────────────────────────────────┤
│ Main Area (Left 70%)     │ Sidebar (Right 30%)   │
│ ┌─ Personal Info ──────┐ │ ┌─ Status ──────────┐│
│ │ Name: John Doe       │ │ │ Current: Pending  ││
│ │ Age: 35              │ │ │                   ││
│ │ ...                  │ │ │ [Approve]         ││
│ └──────────────────────┘ │ │ [Reject]          ││
│                          │ └───────────────────┘│
│                          │ ┌─ History ─────────┐│
│                          │ │ • Submitted       ││
│                          │ │ • Manager Review  ││
│                          │ └───────────────────┘│
└──────────────────────────────────────────────────┘
```

---

#### FR-FRONT-RESP-04: Export Functionality
**Description:** Download responses in multiple formats.

**Export Options:**
- CSV (all columns)
- JSON (raw data)
- PDF (formatted single response)
- Excel (with formatting)

**Implementation:**
```typescript
const handleExport = async (format: 'csv' | 'json') => {
  const blob = await api.get(`/api/v1/form/${formId}/export/${format}`, {
    responseType: 'blob'
  });
  
  downloadBlob(blob, `responses_${formId}.${format}`);
};
```

---

### 4.6 Approval Workflow Module

#### FR-FRONT-APPR-01: Approval Timeline
**Description:** Visual timeline of approval steps.

**UI Component:**
```
Approval Progress

○ Submitted ────●────── ○ Manager Review ────○────── ○ Admin Review
  Jan 9, 10:30    ✓     (Current Step)               (Pending)
  by: John Doe        Approved by: Mike
                      Jan 9, 11:00
```

**Status Icons:**
- ○ Pending (gray)
- ● In Progress (blue, pulsing)
- ✓ Approved (green)
- ✗ Rejected (red)

---

#### FR-FRONT-APPR-02: Approval Actions
**Description:** Approve/Reject interface.

**UI:**
```
┌─ Approval Controls ──────────────────┐
│ Your Action:                         │
│ ○ Approve   ○ Reject   ○ Send Back   │
│                                      │
│ Comments (Required for Reject):      │
│ [___________________________________]│
│ [___________________________________]│
│                                      │
│ [Cancel] [Submit Decision]           │
└──────────────────────────────────────┘
```

**Validation:**
- "Reject" requires comment (min 10 chars)
- "Send Back" requires reason
- Confirmation modal for final approval

**Backend Call:**
```typescript
POST /api/v1/approvals/{responseId}/action
{
  action: 'approve' | 'reject' | 'send_back',
  comment: string,
  step_id: string
}
```

---

### 4.7 AI & Smart Features

#### FR-FRONT-AI-01: Form Generator Chat
**Description:** Conversational form creation.

**UI:**
```
┌─ AI Form Generator ──────────────────────────────┐
│ 💬 Chat                                          │
│ ┌──You─────────────────────────────────────────┐│
│ │ Create a patient intake form with personal   ││
│ │ info, medical history, and insurance details ││
│ └──────────────────────────────────────────────┘│
│ ┌──AI──────────────────────────────────────────┐│
│ │ I'll create a patient intake form with 3     ││
│ │ sections:                                    ││
│ │ 1. Personal Information (Name, DOB, Contact) ││
│ │ 2. Medical History (Conditions, Allergies)   ││
│ │ 3. Insurance Details (Provider, Policy #)    ││
│ │                                              ││
│ │ [Preview Form] [Accept & Open in Builder]    ││
│ └──────────────────────────────────────────────┘│
│ [Type your message...]                [Send]    │
└──────────────────────────────────────────────────┘
```

---

#### FR-FRONT-AI-02: Smart Field Suggestions
**Description:** Context-aware suggestions.

**Triggers:**
- Adding a Select field with label "Country" → Suggest country options
- Adding a field with label "Email" → Suggest email validation
- Detecting pattern (Name, Age, Gender) → Suggest "Patient Info" section

**UI:**
```
💡 AI Suggestion
Pre-fill this select field with all countries?
[Accept] [Ignore] [Customize]
```

---

### 4.8 Workflow Automation Module

#### FR-FRONT-WORK-01: Visual Workflow Editor
**Description:** Node-based workflow builder.

**Using:** `React Flow` library

**Node Types:**
- **Trigger**: Form submission event
- **Condition**: If/else logic
- **Action**: Redirect, Create Draft, Send Email

**Example Workflow:**
```
[Patient Form Submitted]
    ↓
[Age >= 18?] ─Yes→ [Create Adult Consent Form Draft]
    ↓ No
[Create Pediatric Consent Form Draft]
```

---

**[Continue to Part 3 with Sections 8-14...]**
