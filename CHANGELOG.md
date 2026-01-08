# Changelog

All notable changes to the Form Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Form status validation on submit (block draft/archived)
- Permission check fix (UUID string comparison)
- Soft delete for responses
- Response edit history
- Conditional required fields
- Approval workflow
- Email notifications
- Webhook integration
- AI-powered form generation

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
- 12 field types: input, textarea, select, radio, checkbox, boolean, rating, date, file_upload, api_search, calculated, file
- 4 UI layouts: flex, grid-cols-2, tabbed, custom
- Form versioning support
- Form cloning
- Form sharing (editors, viewers, submitters)
- Form publishing, archiving, restoring
- Public form toggle
- Slug availability check
- Form expiration scheduling
- Visibility conditions for sections/questions
- Validation rules for fields
- Repeatable sections and questions
- Response templates

#### Response Management
- Submit responses (JSON and multipart)
- Field-level validation
- Required field validation
- Type validation
- Custom validation rules (min_length, max_length, min_selections, max_selections)
- File upload validation
- Paginated response listing
- Advanced search with filters
- Cursor-based pagination
- Response archiving
- Duplicate submission check
- Response count
- Last response retrieval
- Delete all responses (bulk)

#### File Management
- File upload within responses
- Allowed extensions: txt, pdf, png, jpg, jpeg, gif, doc, docx, xls, xlsx, ppt, pptx, csv
- 10MB file size limit
- Secure file retrieval
- MIME type detection
- Unique filename generation

#### Export Module
- CSV export of responses
- JSON export with form metadata

#### API Integrations
- eHospital UHID lookup
- SMS OTP integration
- Cross-form data search
- Employee ID lookup
- Custom script execution

#### Analytics
- Form response analytics (count, latest)
- Submission history by field value

#### Security
- JWT authentication
- Role-based route protection
- Form-level permissions
- Password hashing (bcrypt)
- CORS support
- Response compression

#### Infrastructure
- MongoDB with MongoEngine ODM
- Rotating log files
- Flask-Compress middleware
- Health check endpoint

### Documentation
- Comprehensive SRS document (2300+ lines)
- Implementation plan with priorities
- Form builder specifications
- AI integration roadmap
- User-form management integration guide

---

## [0.1.0] - 2025-12-15

### Added
- Initial project setup
- Flask application factory
- MongoDB connection
- Basic user model
- Basic form model

---

## Version History

| Version | Date | Summary |
|---------|------|---------|
| 1.0.0 | 2026-01-08 | Full feature release |
| 0.1.0 | 2025-12-15 | Initial setup |

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
