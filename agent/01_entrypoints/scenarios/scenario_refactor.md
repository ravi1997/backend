# Scenario: Deep Refactor

## Purpose

Improving code structure, readability, or performance without altering observable behavior.

## Inputs

- Target file or module for refactoring.
- Rationale (e.g., "Reduce cognitive complexity", "Remove duplication").

## Preparation Phase (Adopt `profile_tester.md`)

1. **Sanity Check**: Verify the current test suite passes with 100% success on the target module.
2. **Coverage Baseline**: Run a coverage report. If coverage is below 90%, the Agent MUST write new tests BEFORE refactoring.
3. **Snapshot**: Note the current file size and cyclomatic complexity (if tools available).

## Execution Phase (Adopt `profile_implementer.md`)

1. **Atomic Transformation**: Refactor in small, logical steps (e.g., one function at a time).
2. **Test-After-Step**: Run the target module's tests after *every* change.
3. **Idiomatic Update**: Ensure the new code follows the latest standards in `agent/11_rules/stack_rules/`.

## Validation Phase (Adopt `profile_tester.md`)

1. **Behavior Verification**: Ensure outputs for a range of inputs (using `agent/06_skills/testing/skill_discover_edge_cases.md`) are identical to the pre-refactor state.
2. **Performance Audit**: Ensure no regressions in memory or CPU usage.

## Completion (Adopt `profile_rule_checker.md`)

1. **State Update**: Update `agent/09_state/BACKLOG_STATE.md` (if the refactor was a task).
2. **Commentary**: Document the refactoring decisions in the file header or a separate architecture note.

## STOP Condition

- Refactor is complete, code is cleaner, and 100% of tests pass.
