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

- [ ] FR-FORM-018: Bulk Export/Import Improvements

