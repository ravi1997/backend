# Python Gate: Tests

## Purpose

Verify behavior with Pytest.

## Rules

1. **Runner**: `pytest` is the standard runner.
2. **Structure**: Tests in `tests/` directory or `test_*.py` files.
3. **Fixtures**: Use `pftest` fixtures instead of `unittest.TestCase` where possible.

## Check Command

```bash
pytest
```

## Failure criteria

- Failed tests.
- Test collection failure.
