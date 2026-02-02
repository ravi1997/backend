# C++ Gate: Security

## Purpose

Prevent memory leaks, buffer overflows, and unsafe practices.

## Rules

1. **Static Analysis**: Run `cppcheck` if available.
2. **Memory Safety**: No raw `new`/`delete`. Use `std::unique_ptr` and `std::shared_ptr`.
3. **Input Validation**: All external inputs must be validated before processing.

## Check Command

```bash
cppcheck --enable=warning,performance,portability --error-exitcode=1 .
```

## Failure criteria

- Critical severity issues found by static analysis.
- Presence of `strcpy` or `sprintf` (use `strncpy` or `snprintf`).
