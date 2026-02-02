# Workflow: Testing and Validation

## Purpose

Exhaustive verification of the system's correctness using automated and manual validation loops.

## Required Inputs

- **Implementation Summary**: From `agent/07_templates/feature/implementation_summary.md`.
- **Test Specs**: From `agent/07_templates/feature/TEST_SPEC.md`.

## Expected Outputs

- **Validated Results**: Updated `agent/09_state/TEST_STATE.md`.
- **Final Test Report**: Saved to `plans/Tests/FINAL_REPORT.md`.

## Procedure (Adopt `agent/03_profiles/profile_tester.md`)

1. **Token Risk Check**: Assess budget. Large test suites may require chunking of logs.
2. **Isolation**: Run `agent/06_skills/testing/skill_unit_tests.md` on modified files.
3. **Integration**: Execute `agent/06_skills/testing/skill_integration_tests.md` to verify component boundaries.
4. **Environmental Validation**:
    - If Docker: Run `agent/06_skills/devops/skill_compose_local_dev.md` and run tests within the isolated stack.
5. **Regression Suite**: Run the full project test suite. Log any regressions in `agent/14_known_issues/`.
6. **CI Validation**: Run `agent/06_skills/devops/skill_github_actions_ci.md` steps locally to anticipate pipeline failures.
7. **Edge Case Hunt**: Run `agent/06_skills/testing/skill_discover_edge_cases.md` and implement tests for detected gaps.
8. **Performance Check**: Verify NON-FUNCTIONAL requirements from SRS.
9. **Gate Sign-off**: Verify `agent/05_gates/global/gate_global_quality.md`.

## Failure Modes & Recovery

- **Flaky Tests**: If a test fails inconsistently, route to `agent/01_entrypoints/scenarios/scenario_flaky_test.md`.
- **Infrastructure Failure**: If Docker/CI fails to initialize, request `agent/03_profiles/profile_devops_engineer.md` assistance.

## Required Gates

- `agent/12_checks/rubrics/testing_rubric.md` (Must achieve "High Quality" score).
- Stack-specific Testing Gate (Must Pass).

## State Update

- Update `agent/09_state/TEST_STATE.md`:
  - Update `last_run_date`.
  - Update `coverage_percent`.
  - Update `pass_rate`.

## Related Files

- `agent/11_rules/testing_rules.md`
- `agent/09_state/TEST_STATE.md`
