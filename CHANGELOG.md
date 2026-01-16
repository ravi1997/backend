# Changelog

All notable changes to the Form Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0-staging] - 2026-01-16

### Added

- Deployment workflow configuration.
- Dockerfile for application.
- `mongomock` and `pytest` to requirements.txt.

### Fixed

- Missing dependencies for testing.

## [Unreleased]

### Planned

- Frontend application development
- Mobile application
- Real-time collaborative editing
- Advanced analytics dashboard

## [1.25.0] - 2026-01-16

### Added

- **Agent Route Documentation**:
  - Added `agent/ROUTE_DOCUMENTATION.md` detailing routing logic for AI Agent integration.
  - Defines routing priorities (Incidents -> Build -> Feature -> Quality).
  - Documents intent triggers and target workflows for development efficiency.

### Enhanced

- **Authentication**:
  - Improved error handling in `register` endpoint.
  - Now explicitly catches `marshmallow.ValidationError` to return detailed validation messages.
  - Added warning logs for validation failures.

### Cleanup

- Removed temporary script files (`apply_fix.py`, `debug_eval.py`, etc.).

## [1.24.0] - 2026-01-09

### Fixed

- **Critical Test Fix - Approval Workflow**:
  - Fixed `test_approval_workflow` failure caused by UUID serialization issue in mongomock.
  - Updated `ApprovalStep` model in `Form.py` to use `binary=False` for `UUIDField`.
  - Aligned UUID representation with `uuidRepresentation=standard` configuration.
  - All 78 tests now passing (100% pass rate).

### Enhanced

- **Test Reporting System**:
  - Enhanced `scripts/run_tests_with_report.py` to include `-o junit_logging=all` for comprehensive output capture.
  - Improved `TEST_FAILURE_REPORT.md` generation with detailed stack traces and contextual information.
  - Added industry-standard failure reporting with actionable fix suggestions.

### Added

- **Frontend SRS Documentation (v2.0)**:
  - **Comprehensive Specification**: 4-part detailed Frontend Software Requirements Specification matching backend SRS depth.
  - **Part 1 (Main)**: Enhanced introduction, complete tech stack with versions, role-based access matrix, detailed navigation structure.
  - **Part 2 (Functional Requirements)**:
    - 8 detailed modules: Authentication, Dashboard, Form Builder, Public Submission, Response Management, Approval Workflow, AI Features, Workflows.
    - 40+ functional requirements with UI mockups, implementation details, and API integration specs.
    - Complete UHID/OTP integration UI specifications.
    - Repeatable sections/questions UI specifications (FR-FRONT-BLDR-07).
  - **Part 3 (Data Models & API)**:
    - Complete TypeScript interfaces for all entities (IUser, IForm, IFormResponse, etc.).
    - Comprehensive enum definitions (UserRole, FormStatus, FieldType).
    - Full API Endpoints Reference with 50+ endpoints documented.
    - Zod validation specifications with dynamic schema generation.
    - Visibility condition evaluation algorithms.
  - **Part 4 (Non-Functionals & Testing)**:
    - Performance requirements with specific Core Web Vitals targets.
    - WCAG 2.1 AA accessibility specifications.
    - PWA requirements (manifest, service worker, background sync).
    - Security specifications (XSS, CSRF, CSP, route guards).
    - Comprehensive error handling strategy.
    - Complete testing requirements (Unit, Component, E2E, Accessibility, Performance).
  - **Gap Analysis Report**: Identified and documented all critical gaps, missing specifications, and required improvements.

### Documentation

- Created `FRONTEND_SRS.md` - Main frontend specification document (v2.0).
- Created `FRONTEND_SRS_PART2.md` - Detailed functional requirements (Sections 4-7).
- Created `FRONTEND_SRS_PART3.md` - Data models, API reference, validation (Sections 10-12).
- Created `FRONTEND_SRS_PART4.md` - Non-functionals, security, error handling, testing (Sections 5, 8, 13-14).
- Created `FRONTEND_SRS_ANALYSIS.md` - Comprehensive gap analysis and improvement roadmap.
- Created `FRONTEND_PLAN.md` - Initial frontend implementation plan.
- Updated test configuration in `conftest.py` for proper UUID handling.

### Technical Debt Resolved

- MongoDB UUID representation standardized across test and production environments.
- Test suite now fully compatible with mongomock 4.3.0.
- Eliminated all UUID serialization warnings and errors.

## [1.23.0] - 2026-01-09

### Added

- **Workflow Engine (Phase 2)**:
  - **Form Workflows**: Create and manage conditional logic between forms (`FR-WORK-001`).
  - **CRUD API**: Endpoints for creating, listing, updating, and deleting workflows.
  - **Condition Evaluator**: Secure pythonic execution environment for complex trigger conditions.
  - **Response Integration**: `submit_response` now evaluates active workflows and returns `workflow_action`.
  - **Next-Step Actions**: Support for `redirect_to_form` with data mapping instructions.
  - New endpoints: `CRUD /workflows`.

## [1.22.0] - 2026-01-09

### Added

- **Dynamic Dashboards**:
  - **Customizable Views**: Create role-specific dashboards with configured widgets (`FR-DASH-001`).
  - **Widget Types**: Supported widgets include `counter`, `list_view`, `chart_bar`, `chart_pie`, and `shortcut`.
  - **Data Resolution**: Automatic data fetching for widgets based on form references and saved searches (`FR-DASH-002`).
  - **RBAC**: Dashboards are assigned to specific roles (e.g., DEO, Admin) for secured access.
  - New endpoints: `CRUD /dashboards`.

## [1.14.0] - 2026-01-09

### Added

- **Bulk Response Export**:
  - New `POST /form/export/bulk` endpoint to export multiple forms' responses into a single ZIP file.
  - Re-usable CSV generation logic for individual and bulk exports.
- **Bulk Option Import**:
  - New `POST /form/<id>/section/<sid>/question/<qid>/options/import` endpoint for populating question options from a CSV file.
  - Support for replacing or appending to existing options.

## [1.21.0] - 2026-01-09

### Added

- **Automated AI Security Audit**:
  - Scanning engine for form definitions to proactively identify vulnerabilities.
  - **Exposure Detection**: Flags sensitive fields (SSN, Passwords) configured in publicly accessible forms.
  - **Spam Vulnerability Check**: Recommends validation rules for forms with high ratios of open text fields.
  - **Privacy Score**: Mathematical scoring (0-100) based on configuration safety.
  - **Remediation Engine**: Provides specific actionable advice for each finding.
  - New endpoint: `POST /ai/<form_id>/security-scan`.

## [1.20.0] - 2026-01-09

### Added

- **AI Deep Content Moderation**:
  - **Sensitive PII Discovery**: Detects SSNs, Credit Card numbers, and other identity markers.
  - **PHI Identification**: Special medical terminology scanning to protect health-specific data.
  - **Safety Filters**: automated profanity and inappropriate content blocking.
  - **Security Shield**: Heuristic-based detection of XSS (Script) and SQL Injection patterns in text responses.
  - New endpoint: `POST /ai/<form_id>/responses/<id>/moderate`.

## [1.19.0] - 2026-01-09

### Added

- **AI Anomaly Detection**:
  - Automatically identifies suspicious response patterns using statistical analysis and heuristics.
  - **Duplicate Detection**: Flags near-identical submissions (spam control).
  - **Outlier Detection**: Uses Z-Score (2-Sigma) to identify numerical anomalies in form fields.
  - **Quality Guard**: Detects gibberish or low-effort text submissions based on entropy and character distribution.
  - New endpoint: `POST /ai/<form_id>/anomalies`.

## [1.18.0] - 2026-01-09

### Added

- **Enhanced AI Response Analysis**:
  - **Bulk Sentiment Trends**: Aggregate sentiment distribution (Positive/Negative/Neutral) and average scoring for all form responses.
  - **Expanded Sentiment Dictionary**: Integration of 30+ new emotional keywords (e.g., "helpful", "useless", "efficient", "difficult").
  - New endpoint: `GET /ai/<form_id>/sentiment`.

## [1.17.0] - 2026-01-09

### Added

- **AI Form Template Generation**:
  - New catalog of industry-standard form templates (HR, Medical, Safety, events).
  - New endpoints: `GET /ai/templates` (list) and `GET /ai/templates/<id>` (fetch).
  - Automated ID generation for all template components for immediate database compatibility.
- **Improved AI Blueprint**:
  - Centralized simulated AI logic for content generation and assistance.

## [1.16.0] - 2026-01-09

### Added

- **Advanced Response Management**:
  - **Response Merge**: Combine multiple submissions into a single record with intelligent `None` value handling.
  - **Multi-step Approval Workflow**: Support for sequential approval steps based on user roles (e.g., Manager -> Admin).
  - New endpoints: `POST /responses/merge`, `POST /responses/<id>/approve`, `POST /responses/<id>/reject`.
- 🛡️ **Deep Content Moderation**: Comprehensive scanning for PII, PHI, Profanity, and Injections.
- 🔄 **AI Features (P4)** - Most integration targets achieved.
- **AI Integration (Phase 4 Foundation)**:
  - **Sentiment Analysis**: Keyword-based sentiment scoring for text responses.
  - **PII Scanning**: Basic pattern-based detection for emails and phone numbers.
  - New `ai_results` storage in `FormResponse`.
- **User Management**:
  - Added `manager` role to the system.

## [1.15.0] - 2026-01-09

### Added

- **Response Management Enhancements**:
  - Comprehensive **Edit History** tracking (Creation, Updates, Status Changes, Deletion, Restoration).
  - **Internal Commenting** system for responses to aid team collaboration.
  - **Soft Delete** (Archive/Restore) functionality for responses.
  - **Status Change Notifications**: Automatic email alerts on response approval/rejection.
- **Form Versioning Management**:
  - Explicit **Active Version** selection for each form.
  - API endpoints to create new versions and switch the currently active version.
  - Validation and submission logic now prioritize the selected active version.

## [1.13.0] - 2026-01-09

### Added

- **Multi-language Support**:
  - Implemented localized labels and options for forms (`FR-FORM-017`).
  - Added `translations` field to `FormVersion` model to store language-specific strings.
  - Added `supported_languages` and `default_language` configuration to the `Form` model.
  - New `POST /form/<id>/translations` endpoint for easy translation management.
  - Updated `GET /form/<id>` to support the `lang` query parameter for delivering merged, localized forms.
  - Integrated translation logic into the Server-Side Rendering (SSR) `view_form` route.

## [1.12.0] - 2026-01-09

### Added

- **Response Drafts / Auto-save**:
  - Implemented `is_draft` functionality for responses (`FR-RESP-014`).
  - Added lenient validation for drafts, allowing incomplete submissions to be saved without triggering required field errors or minimum limit checks.
  - Updated `POST /responses` and `PUT /responses/<id>` to handle the `?draft=true` query parameter.
  - Added draft filtering to listing and search endpoints (`?is_draft=true`).
- **Architectural Stability**:
  - Refactored `FormResponse` model to use `UUIDField` for form references instead of `ReferenceField`, resolving persistent dereferencing issues in testing and high-concurrency environments.
  - Standardized MongoDB connection to use `uuidRepresentation=standard` for improved cross-driver compatibility.
  - Improved data serialization for Webhooks and Response History to prevent unsafe database dereferences.

## [1.11.0] - 2026-01-09

### Added

- **Custom Script Execution**:
  - Implemented secure server-side script execution for fields (`FR-API-004`).
  - Added `execute_safe_script` utility with restricted globals and allowed modules (math, random, datetime, json, re).
  - Updated API route to handle `custom` field type with input parameters.
- **Form Builder API**:
  - Added `PATCH /forms/<id>/reorder-sections` to reorder form sections.
  - Added `PATCH /forms/<id>/section/<sid>/reorder-questions` to reorder questions inside a section.
- **Preview & Validation**:
  - Implemented `POST /forms/<id>/preview` (FR-FORM-016).
  - Allows strict validation of form data including logic and scripts without creating a database record.

## [1.10.0] - 2026-01-09

### Added

- **Advanced Validation**:
  - Implemented form-level `custom_validations` for cross-field logic (e.g. `start_date < end_date`).
  - Added expression evaluation in `validate_form_submission`.
- **Collaboration**:
  - Added `ResponseComment` model and endpoints for discussion threads on responses.
  - `POST /responses/<id>/comments` to add feedback.
- **Usability**:
  - Added **Form Cloning** (`POST /forms/<id>/clone`) to duplicate form structure.
  - Added **Form Templates** support (`is_template` flag) and filtering in list API.

## [1.9.0] - 2026-01-09

### Added

- **Form Analytics**:
  - `GET /analytics/summary`: Real-time submission totals and status breakdown.
  - `GET /analytics/timeline`: Daily submission counts for trend analysis.
  - `GET /analytics/distribution`: Answer frequency distribution for choice-based questions.
- **Bug Fixes**:
  - Fixed `deleted_at` field in `FormResponse` model to default to `None` instead of `now()`, resolving issue where all new responses appeared deleted.

## [1.8.0] - 2026-01-09

### Added

- **Data Integrity**:
  - Enhanced `validate_form_submission` to return valid, cleaned data.
  - Automatically strips hidden fields (where `visibility_condition` is false) from submissions.
- **Export**:
  - Updated CSV export to flatten JSON structure into columns.
  - Dynamically generates headers based on form version.
  - Handles repeatable sections by aggregating values with pipes.

## [1.7.0] - 2026-01-09

### Added

- **Scheduled Publishing**:
  - Added `publish_at` to `Form` model.
  - Implemented logic to block access to future forms (unless Editor).
  - Updated `get_form` and submission endpoints.
  - Fixed bug in `Form` model (`uiers` -> `viewers`).
  - Fixed logic to allow public View access on `is_public` forms.

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
| 1.25.0 | 2026-01-16 | Agent Route Docs & Auth Validation |
| 1.24.0 | 2026-01-09 | Critical Tests & Frontend SRS |
| 1.23.0 | 2026-01-09 | Workflow Engine |
| 1.22.0 | 2026-01-09 | Dynamic Dashboards & Widgets |
| 1.21.0 | 2026-01-09 | Automated Form Security Audit |
| 1.20.0 | 2026-01-09 | Deep Content Moderation |
| 1.19.0 | 2026-01-09 | AI Anomaly Detection |
| 1.18.0 | 2026-01-09 | Enhanced Sentiment & Bulk Trends |
| 1.17.0 | 2026-01-09 | AI Form Template Generation |
| 1.16.0 | 2026-01-09 | Advanced Workflow & AI Analysis |
| 1.15.0 | 2026-01-09 | Response Management & Form Versioning |
| 1.14.0 | 2026-01-09 | Bulk Export/Import Enhancements |
| 1.13.0 | 2026-01-09 | Multi-language Support (Localization) |
| 1.12.0 | 2026-01-09 | Response Drafts / Auto-save & Stability Refactor |
| 1.11.0 | 2026-01-09 | Custom Scripts, Builder Reordering, Preview API |
| 1.10.0 | 2026-01-09 | Collaboration, Validation, Usability (Comments, Cloning) |
| 1.9.0 | 2026-01-09 | Analytics & Insights (Dashboard Metrics) |
| 1.8.0 | 2026-01-09 | Data Integrity & Export (Cleaning, Flattened CSV) |
| 1.7.0 | 2026-01-09 | Lifecycle Enhancements (Scheduled Publishing) |
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
