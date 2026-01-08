# Python Testing Strategy

## Overview

Dynamic language testing requiring strict type checking and speed.

## Recommended Tools

| Type | Tool | Notes |
| :--- | :--- | :--- |
| **Unit Testing** | Pytest | The gold standard. Rich ecosystem. |
| **Coverage** | pytest-cov | Integration with coverage.py. |
| **Linting** | Ruff / Flake8 | Fast styling/linting. |
| **Type Checking** | Mypy | Static type checking (Gates requirement). |

## QA Gates Profile

### 1. Build / Install
- `pip install` works cleanly.
- `pip check` (no conflict).

### 2. Tests
- Command: `pytest`
- **Unit:** 100% pass.

### 3. Lint & Types
- **Ruff:** Clean run.
- **Mypy:** Clean run (strict mode preferred).

## Sample Command Pattern

```bash
# Run Tests with coverage
pytest --cov=. --cov-report=term-missing tests/

# Type Check
mypy src/
```
