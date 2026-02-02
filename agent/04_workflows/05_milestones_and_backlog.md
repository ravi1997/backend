# Workflow: Milestones and Backlog

## Purpose

Transform high-level requirements (SRS) and architecture into a granular, prioritized, and traceable execution roadmap.

## Required Inputs

- **SRS**: Approved documentation in `agent/07_templates/srs/`.
- **Architecture**: Approved blueprint in `plans/Architecture/`.

## Expected Outputs

- **Milestones**: Strategic phases recorded in `plans/Milestones/INDEX.md`.
- **Backlog**: Atomic tasks in `agent/09_state/BACKLOG_STATE.md`.

## Procedure (Adopt `agent/03_profiles/profile_planner.md`)

1. **Phase Definition**: Use `agent/06_skills/planning/skill_milestone_planning.md` to define 3-5 major delivery phases.
2. **Strategic Prioritization**: Apply MoSCoW (Must, Should, Could, Won't) to all requirements using `agent/11_rules/global_rules.md`.
3. **Task Decomposition**:
    - Use `agent/06_skills/metacognition/skill_subtask_decomposition.md` to break milestones into tasks.
    - **Rule**: No task should exceed 4 hours of effort.
4. **Risk Assessment**: Run `agent/06_skills/planning/skill_risk_register.md` to identify blockers for M1.
5. **State Seeding**:
    - Populate `agent/09_state/BACKLOG_STATE.md` with M1 tasks.
    - Set initial status to "Todo".
6. **Dependency Mapping**: Use `agent/06_skills/analysis/skill_dependency_mapping.md` to sequence tasks correctly.

## Failure Modes & Recovery

- **Scope Creep**: If tasks exceed the original SRS, trigger a "Scope Split" using `agent/06_skills/planning/skill_scope_split.md` and request User sign-off.
- **Dependency Deadlock**: If Task A needs Task B but Task B is blocked, re-prioritize using `agent/06_skills/planning/skill_backlog_grooming.md`.

## Required Gates

- `agent/12_checks/checklists/intake_checklist.md` (Self-Audit).
- `agent/08_plan_output_contract/naming_conventions.md` (Path Validation).

## State Update

- Update `agent/09_state/PROJECT_STATE.md`:
  - Set `current_milestone` to "M1".
- Update `agent/09_state/BACKLOG_STATE.md`:
  - Ensure all tasks are indexed.

## Related Files

- `agent/09_state/BACKLOG_STATE.md`
- `agent/09_state/PROJECT_STATE.md`
