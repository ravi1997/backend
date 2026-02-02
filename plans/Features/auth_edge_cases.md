# Feature Spec: Auth Edge Cases

## 1. Overview

Enhance the authentication test suite to cover edge cases such as invalid roles, expired tokens, and unauthorized access to role-protected routes.

## 2. Requirements

- Test that a user with 'employee' role cannot access 'admin' routes.
- Test that an invalid session/token returns 401.
- Test that a blocked token (after logout) cannot be reused.

## 3. Implementation Plan

- Modify `tests/test_auth.py` or create `tests/test_auth_edge_cases.py`.
- Implement tests for role verification using `@require_roles` decorator check.

## 4. Acceptance Criteria

- All new tests pass.
- No regression in existing auth tests.
