# Entrypoint: Future Planning

## Purpose

Analyze the existing codebase and generate a comprehensive library of actionable future plans (Epics) in SRS format.

## Inputs

- Existing `src/` directory.
- Existing `plans/` directory.

## Procedure

1. **Profile**: `profile_planner.md`.
2. **Execute Skill**: Run `agent/06_skills/planning/skill_future_planning.md`.
3. **Validation**: Check against `agent/05_gates/global/gate_global_docs.md`.

## Stop Conditions

- `future_plans/` directory is populated with SRS-style docs relative to identified Epics.
- `future_plans/README.md` index is created.

## Related Files

- `agent/06_skills/planning/skill_future_planning.md`
