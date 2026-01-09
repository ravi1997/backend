# Plan: Multi-language Support (FR-FORM-017)

## Objective
Enable form creators to provide localized versions of forms (labels, placeholders, options) to support non-English speaking users.

## Proposed Changes

### 1. Data Models (`app/models/Form.py`)
- **Main Form Model**:
    - Add `supported_languages`: `ListField(StringField())` (e.g., `["en", "hi", "mr"]`).
    - Add `default_language`: `StringField(default="en")`.
- **FormVersion Model**:
    - Add `translations`: `DictField()`.
    - Structure of `translations`:
        ```json
        {
          "language_code": {
            "title": "...",
            "description": "...",
            "sections": {
              "section_id": { "title": "...", "description": "..." }
            },
            "questions": {
              "question_id": {
                "label": "...",
                "help_text": "...",
                "placeholder": "...",
                "options": {
                  "option_id": "localized_label"
                }
              }
            }
          }
        }
        ```

### 2. API Endpoints
- **Update Form Config**:
    - `PUT /form/<id>` should allow updating `supported_languages` and `default_language`.
- **Add Translations**:
    - `POST /form/<id>/translations/<lang_code>`: Add/Update translations for a specific version.
- **Get Translated Form**:
    - `GET /form/<id>?lang=<lang_code>`: Returns the form with merged translations.
    - `GET /form/<id>/public-view?lang=<lang_code>`: (If public view exists) Returns translated public form.

### 3. Logic Implementation
- **Translation Helper**:
    - Create a utility to merge translations into a form object.
    - If a translation is missing for a specific field, fall back to the base (default) value.
- **Validation**:
    - Submissions should continue to use the base IDs/Values to remain language-independent.

## Implementation Steps

1.  **Update Models**: Modify `app/models/Form.py`.
2.  **Create Helper**: Add `merge_translations(form_dict, lang_code)` in a new utility or helper file.
3.  **Update Routes**:
    - Modify `get_form` in `app/routes/v1/form/form.py` to handle the `lang` parameter.
    - (Optional) Add a dedicated route for managing translations if complex. Otherwise, just include it in `update_form`.
4.  **Testing**:
    - Test form creation with translations.
    - Test fetching the form in different languages.
    - Test fallback logic.
