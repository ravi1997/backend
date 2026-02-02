# Python Gate: Packaging

## Purpose

Ensure project dependencies are valid and installable.

## Rules

1. **Manifest**: Must have `requirements.txt`, `Pipfile`, or `pyproject.toml`.
2. **Locking**: Dependencies must be pinned (frozen) to specific versions.
3. **Environment**: Virtual environment support (`venv`, `poetry`, `conda`) is required.

## Check Command

```bash
pip install --dry-run -r requirements.txt
# OR
poetry check
```

## Failure criteria

- Conflicting dependencies.
- Missing manifest file.
