# Java Gate: Tests

## Purpose

Validate logical correctness using JUnit.

## Rules

1. **Framework**: JUnit 5 preferred.
2. **Coverage**: Jacoco report should show > 80% coverage on new classes.
3. **Integration**: `@SpringBootTest` for integration layers.

## Check Command

```bash
mvn test
```

## Failure criteria

- Any test failure.
- Coverage below threshold (if configured).
