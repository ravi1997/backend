# Frontend SRS - Part 3: Data Models, API, Validation (Sections 10-12)

## 10. Data Models & Type Definitions

### 10.1 User Types

```typescript
// Enums
export enum UserType {
  EMPLOYEE = 'employee',
  GENERAL = 'general'
}

export enum UserRole {
  SUPERADMIN = 'superadmin',
  ADMIN = 'admin',
  CREATOR = 'creator',
  EDITOR = 'editor',
  PUBLISHER = 'publisher',
  DEO = 'deo',
  USER = 'user',
  GENERAL = 'general',
  MANAGER = 'manager'
}

// User Interface
export interface IUser {
  id: string;
  username: string;
  email: string;
  employee_id?: string;
  mobile: string;
  user_type: UserType;
  roles: UserRole[];
  is_active: boolean;
  is_admin: boolean;
  is_email_verified: boolean;
  failed_login_attempts: number;
  lock_until?: Date;
  last_login?: Date;
  password_expiration?: Date;
  created_at: Date;
  updated_at: Date;
}

// Auth State
export interface IAuthState {
  user: IUser | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}
```

### 10.2 Form Types

```typescript
export enum FormStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived'
}

export enum FieldType {
  INPUT = 'input',
  TEXTAREA = 'textarea',
  SELECT = '

select',
  RADIO = 'radio',
  CHECKBOX = 'checkbox',
  DATE = 'date',
  RATING = 'rating',
  FILE_UPLOAD = 'file_upload',
  BOOLEAN = 'boolean',
  API_SEARCH = 'api_search',
  CALCULATED = 'calculated'
}

export interface IForm {
  id: string;
  title: string;
  description?: string;
  slug: string;
  created_by: string;
  status: FormStatus;
  ui: 'flex' | 'grid-cols-2' | 'tabbed' | 'custom';
  is_public: boolean;
  approval_enabled: boolean;
  approval_steps?: IApprovalStep[];
  versions: IFormVersion[];
  tags?: string[];
  editors: string[]; // User IDs
  viewers: string[];
  submitters: string[];
  expires_at?: Date;
  created_at: Date;
  updated_at: Date;
}

export interface IFormVersion {
  version: string;
  created_by?: string;
  created_at: Date;
  sections: ISection[];
}

export interface ISection {
  id: string;
  title: string;
  description?: string;
  order: number;
  ui: 'flex' | 'grid-cols-2' | 'tabbed' | 'custom';
  is_disabled: boolean;
  visibility_condition?: string;
  validation_rules?: string;
  is_repeatable_section: boolean;
  repeat_min?: number;
  repeat_max?: number;
  questions: IQuestion[];
  meta_data?: Record<string, any>;
}

export interface IQuestion {
  id: string;
  label: string;
  field_type: FieldType;
  is_required: boolean;
  help_text?: string;
  default_value?: any;
  order: number;
  visibility_condition?: string;
  validation_rules?: string;
  is_repeatable_question: boolean;
  repeat_min?: number;
  repeat_max?: number;
  onChange?: string;
  calculated_value?: string;
  is_disabled: boolean;
  options?: IOption[];
  field_api_call?: 'uhid' | 'otp' | 'form' | 'custom';
  custom_script?: string;
  meta_data?: Record<string, any>;
}

export interface IOption {
  id: string;
  option_label: string;
  option_value: string;
  description?: string;
  is_default: boolean;
  is_disabled: boolean;
  order: number;
  followup_visibility_condition?: string;
}

export interface IApprovalStep {
  id: string;
  name: string;
  required_role: string;
  order: number;
}
```

### 10.3 Response Types

```typescript
export interface IFormResponse {
  id: string;
  form: string; // Form ID
  data: Record<string, any>;
  submitted_by: string;
  submitted_at: Date;
  updated_by?: string;
  updated_at?: Date;
  deleted: boolean;
  deleted_by?: string;
  deleted_at?: Date;
  approval_status?: 'pending' | 'approved' | 'rejected';
  current_approval_step?: number;
  metadata?: Record<string, any>;
}

export interface IApprovalAction {
  step_id: string;
  action: 'approve' | 'reject' | 'send_back';
  comment: string;
  actioned_by: string;
  actioned_at: Date;
}
```

### 10.4 API Response Types

```typescript
// Standard API Response
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

// Paginated Response
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Error Response
export interface ApiError {
  error: string;
  message: string;
  status: number;
  details?: Record<string, string[]>; // Validation errors
}
```

---

## 11. API Endpoints Reference

### 11.1 Authentication Endpoints

| Method | Endpoint | Request Body | Response | Frontend Usage |
|--------|----------|--------------|----------|----------------|
| POST | `/api/v1/auth/register` | `{ username, email, password, ... }` | `{ message }` | FR-FRONT-AUTH-02 |
| POST | `/api/v1/auth/login` | `{ email, password }` OR `{ mobile, otp }` | `{ access_token, user }` | FR-FRONT-AUTH-01 |
| POST | `/api/v1/auth/generate-otp` | `{ mobile }` | `{ message }` | FR-FRONT-AUTH-03 |
| POST | `/api/v1/auth/logout` | `{}` | `{ message }` | FR-FRONT-AUTH-05 |
| GET | `/api/v1/user/status` | - | `IUser` | FR-FRONT-AUTH-04 |

**Example: Login Request**
```typescript
const loginWithPassword = async (email: string, password: string) => {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
    credentials: 'include' // For cookie
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new ApiError(error);
  }
  
  return await response.json();
};
```

---

### 11.2 Form Management Endpoints

| Method | Endpoint | Auth | Request | Response | Frontend Usage |
|--------|----------|------|---------|----------|----------------|
| POST | `/api/v1/form/` | ✅ | `IForm` (partial) | `{ form_id }` | Create form |
| GET | `/api/v1/form/` | ✅ | - | `IForm[]` | List forms |
| GET | `/api/v1/form/{id}` | ✅ | - | `IForm` | Get form details |
| PUT | `/api/v1/form/{id}` | ✅ | `Partial<IForm>` | `{ message }` | Update form |
| DELETE | `/api/v1/form/{id}` | ✅ | - | `{ message }` | Delete form |
| PATCH | `/api/v1/form/{id}/publish` | ✅ | - | `{ message }` | Publish form |
| POST | `/api/v1/form/{id}/clone` | ✅ | - | `{ form_id }` | Clone form |

---

### 11.3 Response Endpoints

| Method | Endpoint | Auth | Request | Response | Frontend Usage |
|--------|----------|------|---------|----------|----------------|
| POST | `/api/v1/form/{id}/responses` | ✅ | `{ data: Record<string, any> }` | `{ response_id }` | Submit (auth) |
| POST | `/api/v1/form/{id}/public-submit` | ❌ | `{ data: Record<string, any> }` | `{ response_id }` | Submit (public) |
| GET | `/api/v1/form/{id}/responses` | ✅ | `?page=1&limit=10` | `PaginatedResponse<IFormResponse>` | List responses |
| GET | `/api/v1/form/{id}/responses/{rid}` | ✅ | - | `IFormResponse` | Get single |
| POST | `/api/v1/form/{id}/responses/search` | ✅ | `{ filters, sort, limit }` | `{ data, cursors }` | Advanced search |
| DELETE | `/api/v1/form/{id}/responses/{rid}` | ✅ | - | `{ message }` | Delete response |

**Example: Public Submission**
```typescript
const submitForm = async (formId: string, data: Record<string, any>) => {
  return await api.post(`/api/v1/form/${formId}/public-submit`, { data });
};
```

---

### 11.4 File Upload Endpoints

| Method | Endpoint | Auth | Content-Type | Response | Frontend Usage |
|--------|----------|------|--------------|----------|----------------|
| POST | `/api/v1/form/{id}/files/{qid}` | Conditional | `multipart/form-data` | `{ filename, filepath, size }` | Upload file |
| GET | `/api/v1/form/{id}/files/{qid}/{filename}` | Conditional | - | File stream | Download file |

**Example: File Upload**
```typescript
const uploadFile = async (formId: string, questionId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`/api/v1/form/${formId}/files/${questionId}`, {
    method: 'POST',
    body: formData,
    // Don't set Content-Type, browser handles it
  });
  
  return await response.json();
};
```

---

### 11.5 Integration Endpoints

| Method | Endpoint | Auth | Request | Response | Frontend Usage |
|--------|----------|------|---------|----------|----------------|
| GET | `/api/v1/form/{id}/section/{sid}/question/{qid}/api?value={input}` | ✅ | - | API-specific data | UHID/OTP/Custom |

**Example: UHID Lookup**
```typescript
const lookupUHID = async (
  formId: string,
  sectionId: string,
  questionId: string,
  uhid: string
) => {
  return await api.get(
    `/api/v1/form/${formId}/section/${sectionId}/question/${questionId}/api`,
    { params: { value: uhid } }
  );
};
```

---

### 11.6 Approval Endpoints

| Method | Endpoint | Auth | Request | Response | Frontend Usage |
|--------|----------|------|---------|----------|----------------|
| GET | `/api/v1/approvals/pending` | ✅ | - | `IFormResponse[]` | Pending list |
| POST | `/api/v1/approvals/{responseId}/action` | ✅ | `{ action, comment, step_id }` | `{ message }` | Approve/Reject |
| GET | `/api/v1/approvals/{responseId}/history` | ✅ | - | `IApprovalAction[]` | History timeline |

---

### 11.7 Export & Analytics Endpoints

| Method | Endpoint | Auth | Response Type | Frontend Usage |
|--------|----------|------|---------------|----------------|
| GET | `/api/v1/form/{id}/export/csv` | ✅ | `text/csv` | Download CSV |
| GET | `/api/v1/form/{id}/export/json` | ✅ | `application/json` | Download JSON |
| GET | `/api/v1/form/{id}/analytics` | ✅ | `{ total_responses, latest_submission }` | Stats cards |

---

## 12. Validation Specifications

### 12.1 Zod Schema Patterns

#### Basic Field Validation
```typescript
import { z } from 'zod';

// Text Input
const textInputSchema = (question: IQuestion) => {
  let schema = z.string();
  
  if (question.is_required) {
    schema = schema.min(1, 'This field is required');
  } else {
    schema = schema.optional();
  }
  
  const rules = JSON.parse(question.validation_rules || '{}');
  
  if (rules.min_length) {
    schema = schema.min(rules.min_length, `Minimum ${rules.min_length} characters`);
  }
  
  if (rules.max_length) {
    schema = schema.max(rules.max_length, `Maximum ${rules.max_length} characters`);
  }
  
  if (rules.pattern) {
    schema = schema.regex(new RegExp(rules.pattern), 'Invalid format');
  }
  
  return schema;
};

// Number Input
const numberInputSchema = (question: IQuestion) => {
  let schema = z.number({ invalid_type_error: 'Must be a number' });
  
  const rules = JSON.parse(question.validation_rules || '{}');
  
  if (rules.min !== undefined) {
    schema = schema.min(rules.min);
  }
  
  if (rules.max !== undefined) {
    schema = schema.max(rules.max);
  }
  
  return question.is_required ? schema : schema.optional();
};

// Select/Radio (Single Choice)
const selectSchema = (question: IQuestion) => {
  const allowedValues = question.options?.map(o => o.option_value) || [];
  return z.enum(allowedValues as [string, ...string[]]);
};

// Checkbox (Multiple Choice)
const checkboxSchema = (question: IQuestion) => {
  const allowedValues = question.options?.map(o => o.option_value) || [];
  let schema = z.array(z.enum(allowedValues as [string, ...string[]]));
  
  const rules = JSON.parse(question.validation_rules || '{}');
  
  if (rules.min_selections) {
    schema = schema.min(rules.min_selections, `Select at least ${rules.min_selections}`);
  }
  
  if (rules.max_selections) {
    schema = schema.max(rules.max_selections, `Select at most ${rules.max_selections}`);
  }
  
  return schema;
};

// File Upload
const fileUploadSchema = (question: IQuestion) => {
  return z.object({
    filename: z.string(),
    filepath: z.string(),
    size: z.number().max(10 * 1024 * 1024, 'File too large (max 10MB)'),
    mimetype: z.string()
  });
};
```

#### Dynamic Form Schema Generation
```typescript
const generateFormSchema = (form: IForm) => {
  const schemaObject: Record<string, z.ZodType> = {};
  
  form.versions[form.versions.length - 1].sections.forEach(section => {
    section.questions.forEach(question => {
      // Skip if hidden by visibility condition
      if (shouldSkipQuestion(question, formData)) return;
      
      let fieldSchema: z.ZodType;
      
      switch (question.field_type) {
        case FieldType.INPUT:
        case FieldType.TEXTAREA:
          fieldSchema = textInputSchema(question);
          break;
        case FieldType.SELECT:
        case FieldType.RADIO:
          fieldSchema = selectSchema(question);
          break;
        case FieldType.CHECKBOX:
          fieldSchema = checkboxSchema(question);
          break;
        case FieldType.FILE_UPLOAD:
          fieldSchema = fileUploadSchema(question);
          break;
        // ... other types
        default:
          fieldSchema = z.any();
      }
      
      schemaObject[question.id] = fieldSchema;
    });
  });
  
  return z.object(schemaObject);
};
```

### 12.2 Frontend Validation Rules

#### Email Validation
```typescript
const emailSchema = z.string().email('Invalid email address');
```

#### Phone Validation (Indian)
```typescript
const phoneSchema = z.string()
  .regex(/^[6-9]\d{9}$/, 'Invalid Indian mobile number');
```

#### Password Strength
```typescript
const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Must contain at least one number')
  .regex(/[^A-Za-z0-9]/, 'Must contain at least one special character');
```

#### Conditional Required
```typescript
// Example: Email is required only if Contact Method = "Email"
const conditionalEmailSchema = z.string().superRefine((val, ctx) => {
  const contactMethod = ctx.formData.contact_method;
  if (contactMethod === 'email' && !val) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'Email is required when contact method is Email'
    });
  }
});
```

### 12.3 Error Message Customization

```typescript
const errorMap: z.ZodErrorMap = (issue, ctx) => {
  switch (issue.code) {
    case z.ZodIssueCode.invalid_type:
      if (issue.expected === 'number') {
        return { message: 'Please enter a valid number' };
      }
      break;
    case z.ZodIssueCode.too_small:
      if (issue.type === 'string') {
        return { message: `Minimum ${issue.minimum} characters required` };
      }
      if (issue.type === 'array') {
        return { message: `Select at least ${issue.minimum} options` };
      }
      break;
    case z.ZodIssueCode.too_big:
      if (issue.type === 'string') {
        return { message: `Maximum ${issue.maximum} characters allowed` };
      }
      break;
  }
  return { message: ctx.defaultError };
};

z.setErrorMap(errorMap);
```

### 12.4 Visibility Condition Evaluation

```typescript
const evaluateVisibilityCondition = (
  condition: string,
  formData: Record<string, any>
): boolean => {
  if (!condition) return true;
  
  try {
    // Create safe evaluation context
    const context = { ...formData };
    
    // Parse and evaluate expression
    // Example condition: "question_uuid == 'yes' and age > 18"
    const fn = new Function(...Object.keys(context), `return ${condition}`);
    return fn(...Object.values(context));
  } catch (error) {
    console.error('Visibility condition evaluation failed:', error);
    return true; // Fail open (show field on error)
  }
};
```

---

**[Continue to Part 4 with Sections 13-14 and Appendices...]**
