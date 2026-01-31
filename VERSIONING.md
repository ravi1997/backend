# Form Versioning Strategy

To prevent historic data corruption when a form is edited, we implement an immutable versioning strategy.

## Workflow

1. **The Draft State**:
   - The user works on the `forms` table.
   - Any edits here are "live" but only visible to the builder.

2. **The "Publish" Action**:
   - When "Publish" is clicked, the backend:
     - Calculates the next version string (e.g., `1.1.0`).
     - Takes the current `sections`, `style`, and `layout` from the `forms` table.
     - Saves this as a new row in `form_versions`.
     - Marks this `version_id` as the current "active" version for respondents.

3. **Respondents**:
   - Respondents always interact with the **latest published version** in `form_versions`.
   - If the user makes new drafts, it does not affect respondents until they publish again.

4. **Analytics**:
   - Responses are linked to both `form_id` and `version_id`.
   - This allows the dashboard to show how answers changed across different versions of the form.
