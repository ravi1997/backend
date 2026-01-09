# Test Documentation and Mapping

This document maps the project features (as defined in `SRS.md` and `PROJECT_STATUS.md`) to their corresponding test files in the `tests/` directory.

## 1. Authentication Module

| Feature ID | Feature Name | Test File | Test Type |
|------------|--------------|-----------|-----------|
| FR-AUTH-001 | User Registration | `tests/test_auth.py` | Integration |
| FR-AUTH-002 | Employee Login | `tests/test_auth.py` | Integration |
| FR-AUTH-003 | OTP Login | `tests/test_auth.py` | Integration |
| FR-AUTH-004 | OTP Generation | `tests/test_api.py` | Integration |
| FR-AUTH-005 | Logout | `tests/test_auth.py` | Integration |

## 2. User Management Module

| Feature ID | Feature Name | Test File | Test Type |
|------------|--------------|-----------|-----------|
| FR-USER-001 | List All Users | `tests/test_user.py` | Integration |
| FR-USER-002 | Get User Details | `tests/test_user.py` | Integration |
| FR-USER-003 | Create User | `tests/test_user.py` | Integration |
| FR-USER-004 | Update User | `tests/test_user.py` | Integration |
| FR-USER-005 | Delete User | `tests/test_user.py` | Integration |
| FR-USER-006 | Lock User Account | `tests/test_user.py` | Integration |
| FR-USER-007 | Unlock User Account | `tests/test_user.py` | Integration |
| FR-USER-008 | Change Password | `tests/test_user.py` | Integration |
| FR-USER-009 | Reset Password | `tests/test_auth.py` | Integration |
| FR-USER-010 | Extend Password Expiry | `tests/test_auth.py` | Integration |

## 3. Form Management Module

| Feature ID | Feature Name | Test File | Test Type |
|------------|--------------|-----------|-----------|
| FR-FORM-001 | Create Form | `tests/test_form.py` | Integration |
| FR-FORM-002 | List Forms | `tests/test_form.py` | Integration |
| FR-FORM-003 | Get Form Details | `tests/test_form.py` | Integration |
| FR-FORM-004 | Update Form | `tests/test_form.py` | Integration |
| FR-FORM-005 | Delete Form | `tests/test_form.py` | Integration |
| FR-FORM-006 | Publish Form | `tests/test_form.py` | Integration |
| FR-FORM-007 | Clone Form | `tests/test_cloning.py` | Integration |
| FR-FORM-008 | Share Form | `tests/test_form.py` | Integration |
| FR-FORM-009 | Archive Form | `tests/test_misc.py` | Integration |
| FR-FORM-010 | Restore Form | `tests/test_misc.py` | Integration |
| FR-FORM-011 | Toggle Public Access | `tests/test_misc.py` | Integration |
| FR-FORM-012 | Check Slug Availability | `tests/test_form.py` | Integration |
| FR-FORM-013 | Set Form Expiration | `tests/test_misc.py` | Integration |
| FR-FORM-014 | List Expired Forms | `tests/test_misc.py` | Integration |

## 4. Form Response Module

| Feature ID | Feature Name | Test File | Test Type |
|------------|--------------|-----------|-----------|
| FR-RESP-001 | Submit Response | `tests/test_responses.py` | Integration |
| FR-RESP-002 | Public Submit Response | `tests/test_responses.py` | Integration |
| FR-RESP-003 | List Responses | `tests/test_responses.py` | Integration |
| FR-RESP-004 | Get Single Response | `tests/test_responses.py` | Integration |
| FR-RESP-005 | Update Response | `tests/test_responses.py` | Integration |
| FR-RESP-006 | Delete Response | `tests/test_responses.py` | Integration |
| FR-RESP-007 | Paginated Responses | `tests/test_responses.py` | Integration |
| FR-RESP-008 | Archive Response | `tests/test_responses.py` | Integration |
| FR-RESP-009 | Search Responses | `tests/test_responses.py` | Integration |
| FR-RESP-010 | Delete All Responses | `tests/test_responses.py` | Integration |
| FR-RESP-011 | Count Responses | `tests/test_analytics.py` | Integration |
| FR-RESP-012 | Get Last Response | `tests/test_analytics.py` | Integration |
| FR-RESP-013 | Check Duplicate Submission | `tests/test_responses.py` | Integration |
| FR-RESP-014 | Response Drafts / Auto-save | `tests/test_response_drafts.py` | Integration |

## 5. Export Module

| Feature ID | Feature Name | Test File | Test Type |
|------------|--------------|-----------|-----------|
| FR-EXPORT-001 | Export Responses to CSV | `tests/test_export.py` | Unit/Integration |
| FR-EXPORT-002 | Export Form to JSON | `tests/test_export.py` | Unit/Integration |

## 6. File Management Module

| Feature ID | Feature Name | Test File | Test Type |
|------------|--------------|-----------|-----------|
| FR-FILE-001 | Upload File | `tests/test_responses.py` | Integration |
| FR-FILE-002 | Retrieve Uploaded File | `tests/test_responses.py` | Integration |

## 7. Analytics Module

| Feature ID | Feature Name | Test File | Test Type |
|------------|--------------|-----------|-----------|
| FR-ANALYTICS-001 | Form Analytics | `tests/test_analytics.py` | Integration |
| FR-ANALYTICS-002 | Submission History | `tests/test_analytics.py` | Integration |

## 8. API Integration & Advanced Features

| Feature ID | Feature Name | Test File | Test Type |
|------------|--------------|-----------|-----------|
| FR-API-001 | UHID Lookup | `tests/test_api.py` | Integration |
| FR-API-002 | OTP SMS | `tests/test_api.py` | Integration |
| FR-API-003 | Cross-Form Lookup | `tests/test_api.py` | Integration |
| FR-API-004 | Custom Script | `tests/test_custom_scripts.py` | Integration |
| FR-COND-001 | Conditional Validation | `tests/test_conditional_validation.py` | Unit |
| FR-HIST-001 | Response Edit History | `tests/test_advanced_features.py` | Integration |
| FR-HOOK-001 | Webhook Integration | `tests/test_advanced_features.py` | Integration |
| FR-EMAIL-001 | Email Notifications | `tests/test_email_notifications.py` | Integration |
| FR-STAT-001 | Response Status Workflow | `tests/test_response_status.py` | Flow |
| FR-SCHED-001 | Scheduled Publishing | `tests/test_scheduled_publishing.py` | Integration |
| FR-DASH-001 | Dashboards | `tests/test_dashboard.py` | Integration |
| FR-WORK-001 | Workflow Configuration | `tests/test_workflow.py` | Integration |
| FR-AI-001 | AI Generation | `tests/test_ai_generation.py` | Integration |

## Test Strategy Overview

The test suite is built using `pytest` and `flask.testing`.

- **Unit Tests**: Focus on specific functions (e.g. validation logic) without database interaction, though primarily most tests here are Integration tests using the database.
- **Integration Tests**: Focus on API endpoints, interacting with a test MongoDB database.
- **Flow Tests**: (e.g. `test_integration_flow.py`) simulate a user journey involving multiple steps (Login -> Create Form -> Submit -> View -> Export).
