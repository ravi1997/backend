# Workflow: Deep Feature Implementation Loop

## Purpose

The primary execution engine for building validated, high-quality features.

## Inputs

- **Task ID**: A "Todo" task from the Backlog (e.g., T-001).
- **SRS**: Approved requirements in `agent/07_templates/srs/`.
- **Stack**: Identified project stack from `agent/02_detection/`.

## Outputs

- **Implemented Code**: Functional code in the repository.
- **Unit Tests**: Coverage for the new feature.
- **Implementation Summary**: Completed `agent/07_templates/feature/implementation_summary.md`.

## Procedure (Adopt `agent/03_profiles/profile_implementer.md`)

### Phase 0: Token Risk Check

1. **Assess Token Budget**: Check current token usage per `agent/00_system/12_token_budget_and_model_switching.md`.
2. **Risk Evaluation**: If usage > 60% (YELLOW), create continuity snapshot using `agent/06_skills/metacognition/skill_continuity_snapshot.md`.
3. **Chunking Plan**: If feature is large (> 500 lines), plan to implement in chunks with incremental writes.

### Phase 1: Scaffolding & Design

1. **Kickoff**: Update `agent/09_state/BACKLOG_STATE.md` set Task to "In Progress".
2. **Requirement Analysis**: Read the linked SRS section and all relevant User Stories.
3. **Drafting**: Create a plan using `agent/07_templates/feature/feature_kickoff.md`:
    - Define affected files and new modules.
    - Identify external dependencies.
    - List potential side-effects.
4. **Sign-off**: Present the plan to the User. **GATE**: Do not proceed without User approval.

### Phase 2: Implementation & Self-Correction

1. **Atomic Development**: Divide the task into small commits.
2. **Build-Fast Loop**:
    - Write code for a single logical unit.
    - Run stack-specific build command (refer to `agent/05_gates/by_stack/`).
    - If it fails: Use `agent/06_skills/implementation/skill_refactor_safely.md`.
3. **Internal Testing**:
    - Create test spec using `agent/07_templates/feature/TEST_SPEC.md`.
    - Write unit tests using `agent/06_skills/testing/skill_unit_tests.md`.
    - **Recursion**: If tests fail, fix before proceeding.
4. **Token Check**: If token usage > 75% (ORANGE), update `plans/Continuity/PROGRESS.md` with current state.
5. **Clean Code Audit**: Run `agent/11_rules/code_style_rules.md`.

### Phase 3: Recursive Verification (Adopt `agent/03_profiles/profile_tester.md`)

1. **Local Integrity**: Run `agent/06_skills/testing/skill_integration_tests.md`.
2. **Global Stability**: Run full suite; verify no regressions in `agent/09_state/TEST_STATE.md`.
3. **Docker Validation**: If applicable, run `agent/06_skills/devops/skill_docker_baseline.md`.
4. **Security Check**: MANDATORY run `agent/06_skills/security/skill_secrets_handling.md`.
5. **Quality Gate**: ENSURE 100% pass on `agent/05_gates/global/gate_global_quality.md`.

### Phase 4: Finalization (Adopt `agent/03_profiles/profile_rule_checker.md`)

1. **Documentation**: Update README and API docs using `agent/11_rules/documentation_rules.md`.
2. **State Sync**: Update `agent/09_state/PROJECT_STATE.md` and `agent/09_state/BACKLOG_STATE.md` to "DONE".
3. **Summary**: Generate `agent/07_templates/feature/implementation_summary.md`.
4. **Continuity Update**: If snapshot was created, update `plans/Continuity/PROGRESS.md` to mark feature complete.
5. **Self-Audit**: Run `agent/06_skills/metacognition/skill_self_audit.md`.

## Failure Modes & Handling

- **Build Failure**: Consult `agent/05_gates/enforcement/gate_failure_playbook.md`.
- **Design Drift**: If implementation deviates from SRS, revert and re-plan.
- **Logic Hole**: If a recurring error is found, log in `agent/14_known_issues/`.
- **Token Budget Exhausted**: Create final snapshot in `plans/Continuity/`, inform user to resume in new session.

## Mandatory Gates

- `agent/05_gates/global/gate_global_quality.md` (Must Pass)
- Stack-specific Build Gate (Must Pass)

## State Update

- Update `agent/09_state/BACKLOG_STATE.md`:
  - Mark task as "Completed".
- Update `agent/09_state/PROJECT_STATE.md`:
  - Increment "features_completed".

## Related Files

- `agent/00_system/12_token_budget_and_model_switching.md`
- `agent/06_skills/metacognition/skill_continuity_snapshot.md`
- `agent/11_rules/code_style_rules.md`
- `agent/05_gates/global/gate_global_quality.md`
- `agent/06_skills/metacognition/skill_self_audit.md`
- `agent/09_state/BACKLOG_STATE.md`
- `plans/Continuity/PROGRESS.md`
