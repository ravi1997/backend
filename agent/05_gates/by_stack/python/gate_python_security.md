# Python Gate: Security

## Purpose

Detect python-specific vulnerabilities.

## Rules

1. **Static SAST**: Run `bandit` on source code.
2. **Dependencies**: Check for known CVEs in `requirements.txt`.
3. **Asserts**: Do not use `assert` in production logic (removed in -O mode).

## Check Command

```bash
bandit -r . -ll
pip-audit
```

## Failure criteria

- Bandit finds High/Medium confidence issues.
- `pip-audit` finds known vulnerabilities.
