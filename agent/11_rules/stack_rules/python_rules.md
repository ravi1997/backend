# Rules: Python & Flask/FastAPI

**Stack**: Python  
**Environment**: uv / poetry / venv  
**Linting**: ruff / black / pylint / mypy

---

## 1. Environment & Dependency Management

- **Virtual Envs**: NEVER install packages globally. Always use a virtual environment.
- **Dependency Files**: `pyproject.toml` (preferred) or `requirements.txt` MUST reflect current environment.
- **Pinning**: Production requirements MUST have pinned versions.

## 2. Code Style & Typing

- **Formatting**: Enforce `black` or `ruff format`.
- **Linting**: Enforce `ruff check` or `pylint`.
- **Type Hints**: ALL function signatures (args and return types) MUST have type hints.
- **Docstrings**: Public functions/classes MUST have Google-style or NumPy-style docstrings.

## 3. Flask/FastAPI Patterns

- **Blueprints/Routers**: Break application into modules (Blueprints for Flask, APIRouters for FastAPI).
- **Pydantic**: Use Pydantic models for data validation (FastAPI standard, supported in Flask).
- **Async**: Use `async def` explicitly where non-blocking I/O is performed (FastAPI).
- **Context Managers**: Use `with` statements for resource management (files, DB sessions).

## 4. Testing

- **Framework**: `pytest`.
- **Fixtures**: Use `conftest.py` for shared fixtures.
- **Mocking**: Use `unittest.mock` or `pytest-mock` to isolate unit tests.
- **Coverage**: `pytest-cov` required with minimum threshold.

## 5. Security (Python Specific)

- **Input Validation**: Never trust user input. Validate with Pydantic or Marshmallow.
- **SQL Injection**: Use ORM (SQLAlchemy, Tortoise) or parameterized queries.
- **Debug Mode**: `debug=True` MUST be disabled in production.
- **Secrets**: Load secrets from Environment Variables (use `python-dotenv`), never hardcoded.

---

## Enforcement Checklist

- [ ] Virtual environment used
- [ ] Type hints present (mypy verification)
- [ ] Black/Ruff formatting applied
- [ ] Pytest suite passes
- [ ] No hardcoded secrets
