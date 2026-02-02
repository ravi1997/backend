# Entrypoint: Run Test Only

## Purpose

Used to execute the test suite and report on quality metrics.

## Inputs

- Existing test suite or test plan.

## Procedure

1. **Profile**: `profile_tester.md`.
2. **Discovery**: Identify all test files and runners.
3. **Execution**: Run unit, integration, and E2E tests.
4. **Report**: Write results to `plans/Tests/LATEST_RESULTS.md`.
5. **Gate**: Verify `agent/05_gates/global/gate_global_quality.md`.

## Related Files

- `agent/04_workflows/07_testing_and_validation.md`
