# Tasks

- [x] FR-FORM-016: Form Preview Mode (Validation API) <!-- id: 8 -->
    - [x] Implement `POST /form/<id>/preview` for submission validation without saving <!-- id: 9 -->
    - [x] Ensure it supports custom scripts and conditional logic checks <!-- id: 10 -->
    - [x] Add `tests/test_preview_mode.py` <!-- id: 11 -->

- [x] FR-RESP-014: Response Drafts / Auto-save <!-- id: 12 -->
    - [x] Update `FormResponse` model to support `is_draft` or `status=draft` <!-- id: 13 -->
    - [x] Create `POST /responses/draft` endpoint (bypassing strict validation) <!-- id: 14 -->
    - [x] Test draft saving and retrieval <!-- id: 15 -->

- [x] FR-FORM-017: Multi-language Support
    - [x] Add `supported_languages` and `default_language` to Form model
    - [x] Add `translations` to FormVersion model
    - [x] Implement `apply_translations` helper
    - [x] Add `POST /form/<id>/translations` endpoint for management
    - [x] Update `GET /form/<id>?lang=<lang>` to deliver localized forms
    - [x] Add `tests/test_multi_language.py`

- [x] FR-RESP-015: Response Edit History & Comments
    - [x] Log creation, updates, status changes, and restores to `ResponseHistory`
    - [x] Add `GET /history` endpoint for responses
    - [x] Add comments system for internal team collaboration
    - [x] Add email notifications for status changes (approved/rejected)
    - [x] Add `tests/test_response_management.py`

- [x] FR-RESP-016: Soft Delete (Archive/Restore)
    - [x] Implement archival and restoration for individual responses
    - [x] Filter out deleted responses from list/search by default

- [x] FR-FORM-012: Form Versioning Management
    - [x] Endpoint to create new version explicitly (`POST /versions`)
    - [x] Endpoint to switch active version (`PATCH /activate`)
    - [x] Respect `active_version` in validation and submission
    - [x] Add `tests/test_form_versioning.py`

- [x] FR-FORM-018: Bulk Export/Import Improvements
    - [x] Implement `POST /form/export/bulk` for multi-form ZIP export
    - [x] Implement `POST /form/<id>/.../options/import` for CSV option import
    - [x] Add `tests/test_bulk_features.py`

- [x] FR-RESP-017: Advanced Response Management
    - [x] Implement **Response Merge** (`POST /merge`)
    - [x] Implement **Multi-step Approval Workflow** (`/approve`, `/reject`)
    - [x] Add roles (`manager`) to support approval steps
    - [x] Add `tests/test_response_merge.py` and `tests/test_approval_workflow.py`

- [x] Phase 4: AI Integration (Initial)
    - [x] Implement **Response Sentiment Analysis**
    - [x] Implement **PII Scanning** (Emails, Phones)
    - [x] Implement **Natural Language Form Generation** (`POST /ai/generate`)
    - [x] Implement **Smart Field Suggestions** (`POST /ai/suggestions`)
    - [x] Implement **Form Template Generation** (`GET /ai/templates`)
    - [x] Implement **AI-Powered Smart Search** (`POST /ai/<id>/search`)
    - [x] Implement **Anomaly Detection** (`POST /ai/<id>/anomalies`)
    - [x] Implement **Deep Content Moderation** (PII, PHI, Profanity, Injection)
    - [x] Implement **Automated Security Scanning** (`POST /ai/<id>/security-scan`)
    - [x] Create dedicated AI blueprint and results storage
    - [x] Add AI test suite (`tests/test_ai_analysis.py`, `tests/test_ai_generation.py`, `tests/test_ai_templates.py`, `tests/test_ai_search.py`, `tests/test_ai_anomalies.py`, `tests/test_ai_moderation.py`, `tests/test_ai_security_scan.py`)
