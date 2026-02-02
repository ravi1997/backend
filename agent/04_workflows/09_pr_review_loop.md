# Workflow: PR Review Loop

## Purpose

Peer-review of changes to ensure long-term maintainability.

## Inputs

- Proposed changes (from a feature task).

## Procedure

1. **Adopt Profile**: `profile_pr_reviewer.md`.
2. **Criteria Check**: Apply `agent/12_checks/rubrics/code_quality_rubric.md`.
3. **Logic Review**: Verify the algorithm is sound and follows the Architecture.
4. **Stylistic Review**: Verify repo hygiene and naming conventions.
5. **Sign-off**: Merge if passed, otherwise return to `profile_implementer.md` with notes.

## STOP Condition

- Review is Approved.

## Required Gates

- `agent/05_gates/global/gate_global_quality.md` (Must Pass)
- `agent/12_checks/rubrics/code_quality_rubric.md` (Must Pass)

## State Update

- Update `agent/09_state/PROJECT_STATE.md`:
  - Mark feature as merged (if applicable).
- Update `agent/09_state/BACKLOG_STATE.md`:
  - Close task ID.

## Related Files

- `agent/07_templates/pr/pull_request_template.md`
