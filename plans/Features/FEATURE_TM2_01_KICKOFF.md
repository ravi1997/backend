# Feature Kickoff: Multi-form Cross-analysis API

## Name: Multi-form Cross-analysis API

## Linked Task: T-M2-01

## Description

Implement an endpoint that allows comparing analytical data across multiple forms. This will include distribution comparison, sentiment performance across forms, and correlation detection if common fields are present.

## Implementation Plan

1. **New Endpoint**: Create `POST /form/api/v1/ai/cross-analysis`.
2. **Payload Validation**: Ensure `form_ids` is a list and contains valid/accessible IDs.
3. **Data Aggregation**:
   - Fetch metadata for all forms.
   - Fetch AI results (sentiment distribution) for each form.
   - Identify common questions (based on labels or same UUIDs if cloned).
4. **Comparison Logic**:
   - Aggregate sentiment counts per form.
   - Calculate average response rates (if possible).
   - Cross-tabulate any common fields.
5. **Response Structure**:
   - `comparison_summary`: High-level stats.
   - `form_metrics`: Per-form breakdown.
   - `common_field_analysis`: Comparison of overlapping questions.

## Tests

- [ ] Test with valid form IDs and existing AI results.
- [ ] Test with unauthorized form ID (should return 403 or exclude).
- [ ] Test with non-existent form ID.
- [ ] Test with empty forms (no responses).

## Checkpoints

- [x] Feature Kickoff created.
- [ ] Payload validation implemented.
- [ ] Core comparison logic implemented.
- [ ] Tests passing.
