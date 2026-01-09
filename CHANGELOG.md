# Changelog

All notable changes to the Form Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Response edit history
- Conditional required fields
- Approval workflow
- Email notifications
- Webhook integration
- AI-powered form generation
## [1.6.0] - 2026-01-09

### Added
- **Response Status Management**:
  - Added `status` (pending/approved/rejected) and `status_log` to `FormResponse`.
  - Created `PATCH /responses/<id>/status` endpoint for approval workflows.
  - Added permission checks (Edit access required for status changes).
  - Integrated status changes with Webhooks (`status_updated` event) and History tracking.

## [1.5.0] - 2026-01-09

### Added
- **Email Notifications**:
  - Added `notification_emails` to Form model.
  - Implemented generic `EmailService` utility.
  - Added email triggers on both authenticated and public submissions.
  - Integrated SMTP configuration support.

## [1.4.0] - 2026-01-08

### Added
- **Response Edit History**:
  - Implemented `ResponseHistory` model to track changes.
  - Added audit trail for updates and deletions (`data_before` vs `data_after`).
  - Added API endpoint to retrieve history logs.
- **Advanced Conditional Logic**:
  - Enhanced `Conditional Required` fields logic.
  - Implemented `safe_eval` for robust condition parsing.
- **Webhook Integration**:
  - Added webhook configuration to Form model.
  - Implemented HMAC-signed triggers for `submitted`, `updated`, and `deleted` events.

### Fixed
- **Submission Versioning**: Added `version` field to `FormResponse` to track form version at time of submission.
- **Soft Delete Refactor**: Unified soft delete logic across all response endpoints.
- **Permission Bug**: Fixed `has_form_permission` to correctly handle UUID objects.

---


## [1.3.1] - 2026-01-08

### Added
- **Conditional Required Fields**:
  - Added `required_condition` to Question model to make fields mandatory based on logic.
  - Implemented shared validation service `validate_form_submission`.
  - Added UUID sanitization for safe evaluation of conditions.

### Fixed
- **Public Submission Validation**:
  - Integrated validation service into `public_submit` endpoint to prevent invalid data from anonymous users.

---


## [1.3.0] - 2026-01-08

### Added
- **Backend Test Suite**: 
  - Implemented 30 comprehensive tests using `pytest` and `mongomock`.
  - Covered Authentication, User Management, Form CRUD, Responses, Analytics, and API Integrations.
  - Configured `conftest.py` for fully isolated database testing.
- **Improved Data Filtering**: Added global filtering for archived/deleted responses in listing and search endpoints.

### Fixed
- **Authentication Resilience**: Fixed `AttributeError` for `request.current_user` by switching to `get_current_user()` helper.
- **Model Security**: Resolved datetime comparison `TypeError` in `User` model by ensuring consistent timezone-aware objects.
- **User Management**: Fixed manual `User` instantiation in `create_user` route that caused 500 errors.
- **Response Management**: Standardized archive logic to use `deleted` field across all routes.
- **API Integrations**: Fixed internal routing prefix for form-to-form search and response JSON parsing.
- **Validation Stability**: Fixed `IndexError` in form creation by ensuring `versions` list is always present and valid.

---

## [1.2.0] - 2026-01-08

### Added
- **Security Enhancements**: 
  - Implemented account locking check in login flow.
  - Implemented password expiration check in login flow.
  - Added failed login attempt tracking logic.
- **New Features**:
  - **Saved Search**: Added endpoints to create, list, and delete saved searches for form responses.
- **Core Fixes**:
  - Fixed P0 permission resolution bug (UUID string comparison in `has_form_permission`).
  - Improved permission logic to ensure form creators always have full access.

---

## [1.1.0] - 2026-01-08

### Added

#### Documentation & Roadmap
- **Comprehensive SRS Document**: 2300+ lines covering 9 major areas including AI integration roadmaps and security matrices.
- **Detailed Implementation Plan**: Phase-based roadmap (P0-P3) for completing and hardening the system.
- **Form Builder Specifications**: Detailed technical guide for field types, visibility logic, and validation.
- **AI Integration Strategy**: Architecture and roadmap for NLP-based form generation and smart search.
- **User-Form Integration Matrix**: Permission inheritance models and data flow documentation.

#### Project Configuration
- **Agent Workspace Setup**: Configured project context for AI agent auto-detection and workflow optimization.
- **Project Structure Audit**: Completed thorough analysis of models, routes, and schemas to identify system gaps.

---

## [1.0.0] - 2026-01-08

### Added

#### Authentication Module
- User registration with email/username/employee_id
- Password-based login for employee users
- OTP-based login for all users
- JWT token generation and management
- Token blocklist for logout invalidation
- Account locking after failed attempts (5 attempts, 24h lock)
- Password expiration (90 days)

#### User Management
- Full CRUD operations for users
- Role-based access control (8 roles)
- Account lock/unlock functionality
- Password change and reset
- OTP resend with rate limiting
- Password expiry extension

#### Form Management
- Create forms with sections and questions
- 12 field types support (input, textarea, select, radio, checkbox, etc.)
- 4 UI layouts: flex, grid-cols-2, tabbed, custom
- Form versioning and cloning support
- Form sharing permissions (editors, viewers, submitters)
- Visibility conditions and validation rules
- Repeatable sections and questions support

#### Response Management
- Submit responses with file upload support
- Advanced search with cursor-based pagination
- Response archiving and duplicate check
- Metadata tracking for submissions

#### Infrastructure & Security
- MongoDB with MongoEngine ODM integration
- File upload management with MIME type security
- External API integrations (UHID, SMS OTP)
- Rotating log files and health check monitoring

---

## [0.1.0] - 2025-12-15

### Added
- Initial project setup
- Flask application factory
- MongoDB connection
- Basic user and form models

---

## Version History

| Version | Date | Summary |
|---------|------|---------|
| 1.6.0 | 2026-01-09 | Approval Workflows (Response Status) |
| 1.5.0 | 2026-01-09 | Workflow Automation (Email Notifications) |
| 1.4.0 | 2026-01-08 | Advanced Features (History, Webhooks, Logic) |
| 1.3.1 | 2026-01-08 | Conditional Required Fields |
| 1.3.0 | 2026-01-08 | Backend Test Suite & Critical Fixes |
| 1.2.0 | 2026-01-08 | Security & Saved Search |
| 1.1.0 | 2026-01-08 | Documentation & Roadmap Phase |
| 1.0.0 | 2026-01-08 | Core Feature Release |
| 0.1.0 | 2025-12-15 | Initial Setup |

---

## Upgrade Guide

### From 0.1.0 to 1.0.0

1. **Database Migration**: Run migrations for new fields
   ```bash
   # No automated migrations - manual verification required
   python -c "from app import create_app; create_app()"
   ```

2. **Environment Variables**: Add new required variables
   ```
   JWT_SECRET_KEY=your-secret-key
   UPLOAD_FOLDER=uploads
   ```

3. **Dependencies**: Install new packages
   ```bash
   pip install -r requirements.txt
   ```

---

## Contributors

- Development Team

---

## Links

- [SRS Document](file:///home/programmer/Desktop/form-frontend/backend/SRS.md)
- [Implementation Plan](file:///home/programmer/Desktop/form-frontend/backend/PLAN.md)
