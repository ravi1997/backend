# Stack State

## Detected Environment

- **Primary Language**: Python 3.12
- **Framework**: Flask 3.1.1
- **Build System**: Makefile / Docker
- **Package Manager**: pip (requirements.txt)
- **Runtime Version**: Python 3.12

## Infrastructure

- **Database**: MongoDB (mongoengine, pymongo)
- **Caching**: Flask-Compress
- **Containerization**: Docker (Dockerfile, docker-compose.yml)

## Tooling

- **Linter**: Ruff (configured in pyproject.toml)
- **Formatter**: Black (configured in pyproject.toml)
- **Type Checker**: mypy (configured in pyproject.toml)
- **Test Runner**: pytest (88 tests passing)

## Code Quality Standards

- **Type Hints**: Partial coverage (~15%), actively being improved
- **Datetime**: Fully modernized to timezone-aware (datetime.now(timezone.utc))
- **Deprecation Warnings**: 0 (application code)
- **Flask Patterns**: App factory, blueprints, proper configuration
- **Security**: Environment variables, JWT auth, input validation

## Recent Improvements (2026-02-02)

1. ✅ Eliminated all datetime.utcnow() deprecation warnings
2. ✅ Added type hints to utility functions (webhooks, email, file handling)
3. ✅ Created pyproject.toml with Ruff, Black, pytest, mypy configuration
4. ✅ Documented standardization status in STANDARDIZATION_REPORT.md
