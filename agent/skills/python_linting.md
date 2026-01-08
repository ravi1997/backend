# Skill: Python Linting & Formatting

**Purpose**: Ensure Python code meets project standards.

## 1. Standard Tools
-   **Format**: `black` or `ruff format`.
-   **Lint**: `pylint`, `flake8`, or `ruff check`.
-   **Imports**: `isort`.

## 2. Execution
**Check Config**: Look for `pyproject.toml`, `.flake8`.

```bash
# Auto-fix common issues
ruff check --fix .
black .
isort .
```

## 3. Pre-Commit
If pre-commit is installed:
```bash
pre-commit run --all-files
```
