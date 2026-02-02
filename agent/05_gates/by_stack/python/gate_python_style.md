# Python Gate: Style

## Purpose

Enforce PEP 8 and consistent formatting.

## Rules

1. **PEP 8**: Code must conform to standard.
2. **Formatter**: `black` or `autopep8` usage is mandatory.
3. **Linter**: `flake8` or `pylint` must pass without errors.
4. **Imports**: Sorted imports (`isort`).

## Check Command

```bash
black --check .
flake8 .
```

## Failure criteria

- Unformatted code.
- Flake8 errors (undefined names, etc).
