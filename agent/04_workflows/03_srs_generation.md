# Workflow: SRS Generation

## Purpose

Convert vague ideas into rigid, testable requirements.

## Inputs

- Project context from Intake.

## Procedure

1. **Token Risk Check**: Assess budget. If large SRS (> 1000 lines), plan chunking.
2. **Adopt Profile**: `profile_analyst_srs.md`.
3. **Drafting**: Use `agent/07_templates/srs/` to fill `functional_reqs.md` and `non_functional_reqs.md`.
4. **User Stories**: Map requirements to User Stories.
5. **Validation**: Check for ambiguity (e.g., words like "Fast", "Easy", "Scalable" without metrics).
6. **User Review**: Present the draft for approval.
7. **Gate**: Verify `agent/05_gates/global/gate_global_docs.md`.

## STOP Condition

- User says "SRS Approved".

## State Update

- Update `agent/09_state/PROJECT_STATE.md`:
  - Set `current_stage` to "REQUIREMENTS_APPROVED".

## Related Files

- `agent/03_profiles/profile_analyst_srs.md`
