# C++ Gate: Tests

## Purpose

Verify functional correctness via automated tests.

## Rules

1. **Framework**: Usage of Google Test (`gtest`) or Catch2 is required.
2. **Coverage**: New code must have associated unit tests.
3. **Pass Rate**: 100% of tests must pass.

## Check Command

```bash
cd build
ctest --output-on-failure
```

## Failure criteria

- Any test failure.
- Test executable fails to compile.
