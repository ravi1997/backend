# Example: Feature Cycle (Task-Driven)

## 1. Selection & Context Extraction

1. **Backlog Scan**: Agent reads `agent/09_state/BACKLOG_STATE.md` and identifies `T-004: JWT Payload Hardening` as "High Priority".
2. **Context Rebuild**: Agent calls `agent/06_skills/metacognition/skill_context_budgeting.md` to load:
    - `agent/07_templates/srs/06_api_contracts.md`
    - `agent/11_rules/stack_rules/python_rules.md`
    - `agent/03_profiles/profile_implementer.md`

## 2. Planning (The Kickoff)

1. **Design**: Agent generates `agent/07_templates/feature/feature_kickoff.md`.
2. **Impact Analysis**: Identifies that changing the JWT payload involves updating the `auth_middleware.py` and `user_service.py`.
3. **SRS Sync**: Verifies against `agent/07_templates/srs/09_security_and_privacy.md`.

## 3. Atomic Implementation

1. **Code Change**: Implements the `exp` claim enforcement in `auth.py`.
2. **Continuous Build**: Runs `agent/05_gates/by_stack/python/gate_python.md` after every function update.
3. **Self-Correction**: Detected a type mismatch in mypy; Agent applies `agent/06_skills/implementation/skill_surgical_refactor.md` to fix the hint.

## 4. Recursive Validation

1. **Test Creation**: Updates `tests/test_auth_logic.py` to include expired token scenarios.
2. **Local Run**: Runs `pytest tests/test_auth_logic.py`. Result: `100% Pass`.
3. **Global Scan**: Runs `agent/04_workflows/07_testing_and_validation.md` to ensure no side effects on `Login` or `ProfileUpdate` flows.

## 5. Peer Review Logic

1. **Self-Audit**: Agent switches to `agent/03_profiles/profile_pr_reviewer.md`.
2. **Rubric Check**: Scores the changeset against `agent/12_checks/rubrics/quality_rubric.md`.
3. **Findings**: Identifies a missing log entry for unauthorized attempts. Fixes it immediately.

## 6. State Closure

1. **State Update**: Sets `T-004` status to `DONE` in `agent/09_state/BACKLOG_STATE.md`.
2. **Summary**: Generates `agent/07_templates/feature/implementation_summary.md`.
3. **History Log**: Records the architectural decision to enforce 1-hour expiry in `agent/00_system/05_glossary.md` (Decision Log).

## Result

A high-integrity feature merge with zero "Design Drift" and 100% compliance with Agent OS security rules.
