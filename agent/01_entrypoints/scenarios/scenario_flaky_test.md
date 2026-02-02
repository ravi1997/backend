# Scenario: Flaky Test Investigation & Stabilization

## Purpose

Diagnosing and fixing tests that pass/fail inconsistently (non-deterministic behavior).

## Inputs

- Test suite with intermittent failures.
- CI/CD pipeline showing random test failures.

## Detection Phase (Adopt `profile_tester.md`)

1. **Pattern Recognition**: Run the flaky test 100 times and record:
   - Failure rate (e.g., fails 3 out of 100 runs).
   - Error messages (are they consistent?).
   - Environmental factors (time of day, load, etc.).
2. **Categorization**: Determine the likely cause:
   - **Timing**: Race conditions, async issues.
   - **State**: Tests affecting each other (shared state).
   - **External**: Network calls, file system, random data.
   - **Resource**: Memory/CPU exhaustion.

## Investigation Phase (Adopt `profile_implementer.md`)

1. **Isolation**: Run the flaky test in complete isolation (no other tests).
2. **Determinism Check**: Replace all randomness with fixed seeds.
3. **Async Audit**: Check for missing `await`, improper promise handling, or timeout issues.
4. **State Inspection**: Verify tests clean up after themselves (database rollback, file deletion).

## Stabilization Phase (Adopt `profile_implementer.md`)

1. **Fixes**:
   - Add proper waits/polling for async operations.
   - Mock external dependencies.
   - Increase timeouts (as a last resort).
   - Use test fixtures to ensure clean state.
2. **Retry Logic**: As a temporary measure, allow 1-2 retries for known flaky tests (but document this as tech debt).

## Verification Phase (Adopt `profile_tester.md`)

1. **Stress Test**: Run the fixed test 1000 times to verify 100% pass rate.
2. **CI Integration**: Ensure the test passes consistently in CI.

## STOP Condition

- Test has a 100% pass rate over 1000 runs.
- Root cause is documented in `plans/Tests/FLAKY_TEST_LOG.md`.

## Related Files

- `agent/11_rules/testing_rules.md`
- `agent/06_skills/testing/skill_discover_edge_cases.md`
