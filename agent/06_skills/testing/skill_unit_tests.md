# Skill: Unit Test Generation & Execution

## Purpose

Ensures atomic correctness of individual functions or components using stack-specific testing frameworks.

## Execution Procedure

1. **Identify Target**: Select a single file or module.
2. **Mocking**: Use `unittest.mock` (Python) or `jest.mock` (JS) for external dependencies.
3. **Test Case Matrix**:
    - Happy Path (Valid inputs).
    - Boundary Values (Min/Max).
    - Error Handling (Invalid inputs/Exceptions).
4. **Creation**: Write tests in `tests/` directory with `test_` prefix.
5. **Run**: Execute `pytest`, `npm test`, or `mvn test`.

## Output Contract

- **Test Results**: Log of passing/failing assertions.
- **Coverage Update**: Update `agent/09_state/TEST_STATE.md`.
