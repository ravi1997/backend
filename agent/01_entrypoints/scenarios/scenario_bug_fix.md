# Scenario: Deep Bug Fix

## Purpose

A rigid, diagnostic-first approach to resolving software defects with zero regressions.

## Inputs

- Bug report or symptom description.
- Access to the codebase.

## Diagnostic Phase (Adopt `profile_tester.md`)

1. **Reproduction**: Create a minimal test case in `tests/repro_bug_[ID].py` (or equivalent) that consistently fails.
2. **Trace Analysis**: Run the reproduction test with verbose logging/tracing.
3. **Pinpoint**: Identify the exact file and line number where the "Truth" deviates from "Expectation".
4. **State Check**: Verify if this bug exists in the current Git baseline (`agent/09_state/PROJECT_STATE.md`).

## Implementation Phase (Adopt `profile_implementer.md`)

1. **Surgical Fix**: Modify only the necessary code to pass the reproduction test.
2. **Side-Effect Analysis**: Grep for all usages of the modified function/variable to identify potential breakages.
3. **Local Audit**: Run all tests in the same module as the fix.

## Verification Phase (Adopt `profile_tester.md`)

1. **Regression Suite**: Run the FULL project test suite.
2. **Performance Check**: Ensure the fix doesn't introduce significant latency.
3. **Clean Up**: Delete the temporary `repro_bug_[ID].py` file and move the test case into the permanent test suite.

## Documentation Phase (Adopt `profile_rule_checker.md`)

1. **Update State**: Log the bug and fix in `agent/09_state/TEST_STATE.md`.
2. **Post-Mortem**: (If bug was severe) Update `agent/11_rules/code_style_rules.md` to prevent this class of bug in the future.

## STOP Condition

- Reproduction test PASSES and 0 regressions found in the full suite.
