# Skill: Refactor Safely

## Purpose

Modify code structure without altering external behavior.

## Procedure

1. **Verify Baseline**: Run all tests. MUST be green. if tests are missing, WRITE THEM FIRST (Pinning Tests).
2. **Small Steps**:
   - Rename variable -> Run Tests.
   - Extract Method -> Run Tests.
   - Move Class -> Run Tests.
3. **Tools**: Use IDE refactoring tools if available (safest).
4. **Manual**: If valid, use Search/Replace carefully.
5. **Code Style**: Apply linter immediately after change.

## Verification

- Pre-refactor Test Result == Post-refactor Test Result.
- No regression in logic.

## Rollback

- If tests fail and the fix isn't obvious in < 2 mins, `git reset --hard` and try smaller step.
