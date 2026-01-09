# Tasks

- [x] FR-FORM-016: Form Preview Mode (Validation API) <!-- id: 8 -->
    - [x] Implement `POST /form/<id>/preview` for submission validation without saving <!-- id: 9 -->
    - [x] Ensure it supports custom scripts and conditional logic checks <!-- id: 10 -->
    - [x] Add `tests/test_preview_mode.py` <!-- id: 11 -->

- [ ] FR-RESP-014: Response Drafts / Auto-save <!-- id: 12 -->
    - [ ] Update `FormResponse` model to support `is_draft` or `status=draft` <!-- id: 13 -->
    - [ ] Create `POST /responses/draft` endpoint (bypassing strict validation) <!-- id: 14 -->
    - [ ] Test draft saving and retrieval <!-- id: 15 -->
