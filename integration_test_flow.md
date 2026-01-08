# Integration Test Flow

This document defines the end-to-end integration testing flow for the Form Management System.

## Flow 1: Complete Form Management Life Cycle

```mermaid
graph TD
    A[Admin: Register & Login] --> B[Admin: Create Form v1.0]
    B --> C[User: Register & Login]
    C --> D[User: Submit Response 1]
    D --> E[Admin: Get Response & Verify Version 1.0]
    E --> F[User: Archive Response 1]
    F --> G[Admin: List Responses - Verify Hidden]
    G --> H[Admin: Restore Response 1]
    H --> I[Admin: List Responses - Verify Visible]
    I --> J[Admin: Delete Response 1 - Soft Delete]
    J --> K[Admin: Verify Soft Delete Fields in DB]
```

## Flow 2: Form Hardening & Security

```mermaid
graph TD
    A[User: Failed Logins x5] --> B[User: Verify Account Locked]
    B --> C[Admin: Unlock User]
    C --> D[User: Login Success]
    D --> E[Form: Set Expiry in Past]
    E --> F[User: Submit Response - Verify 403 Expired]
```

## Flow 3: Permission Matrix

| User Role | Action: View Form | Action: Edit Form | Action: Submit |
|-----------|-------------------|-------------------|----------------|
| Creator   | ✅ Pass            | ✅ Pass            | ✅ Pass         |
| Editor    | ✅ Pass            | ✅ Pass            | ✅ Pass         |
| Viewer    | ✅ Pass            | ❌ Forbidden      | ❌ Forbidden    |
| Anonymous | ❌ Forbidden*     | ❌ Forbidden      | ❌ Forbidden/✅ Public |

*\* Viewer restricted to forms they are assigned or public forms.*

## Flow 4: Advanced Logic & History

```mermaid
graph TD
    A["Admin: Create Form w/ Conditional Required Logic"] --> B["User: Submit Data (Condition Met, Field Missing)"]
    B --> C["User: Verify 422 Validation Error"]
    C --> D["User: Submit Valid Data (Condition Met, Field Present)"]
    D --> E["User: Update Response Data"]
    E --> F["Admin: Get Response History"]
    F --> G["Admin: Verify Change Log (create vs update)"]
    G --> H["Admin: Verify Data Snapshots (before/after)"]
```

## Flow 5: Webhook & Public Access

```mermaid
graph TD
    A["Admin: Configure Webhook on Form"] --> B["Anonymous: Submit Public Response"]
    B --> C["System: Validate Submission Logic"]
    C --> D["System: Save & Generate HMAC"]
    D --> E["System: Trigger Webhook (POST)"]
    E --> F["Mock Receiver: Verify Payload & Signature"]
```

## Implementation Status

- [x] **Core Registration/Login**: Verified in [test_auth.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_auth.py)
- [x] **Basic Submission**: Verified in [test_responses.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_responses.py)
- [x] **Draft Blocking**: Verified in [test_responses.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_responses.py)
- [x] **Response Versioning**: Verified in [test_integration_flow.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_integration_flow.py)
- [x] **Soft Delete Consistency**: Verified in [test_integration_flow.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_integration_flow.py)
- [x] **Restore Response**: Verified in [test_integration_flow.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_integration_flow.py)
- [x] **Filtering of Deleted**: Verified in [test_integration_flow.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_integration_flow.py)
- [x] **Account Lockout Flow**: Verified in [test_integration_flow.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_integration_flow.py)
- [x] **Conditional Logic**: Verified in [test_advanced_features.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_advanced_features.py)
- [x] **Response History**: Verified in [test_advanced_features.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_advanced_features.py)
- [x] **Webhook Triggers**: Verified in [test_advanced_features.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_advanced_features.py)
- [x] **Public Form Validation**: Verified in [test_advanced_features.py](file:///home/programmer/Desktop/form-frontend/backend/tests/test_advanced_features.py)
