# Stack Fingerprint: Python FastAPI

## Purpose

Identifies and configures for a FastAPI backend.

## Signals

- `from fastapi import FastAPI`.
- `uvicorn` in `requirements.txt` or `scripts`.

## Configuration

- **Entrypoint**: `main.py` or `api/main.py`.
- **Run Command**: `uvicorn main:app --reload`.
- **Docs**: Usually at `/docs` (Swagger UI).
- **Style Rule**: PEP8 + Pydantic types.

## Docker Baseline

- **Base Image**: `python:3.11-slim` or `python:3.11-alpine`.
- **Multi-stage**: Use builder stage for dependencies, runtime stage for execution.
- **User**: Run as non-root user (e.g., `USER appuser`).
- **Port**: Expose `8000` (default uvicorn port).
- **Healthcheck**: `CMD curl --fail http://localhost:8000/health || exit 1`.
- **Hot Reload**: Mount code volume in docker-compose for local dev.

## GitHub Actions Baseline

- **Workflow**: `.github/workflows/ci.yml`.
- **Jobs**: lint (ruff/flake8), test (pytest), build (docker build).
- **Python Version Matrix**: Test on `[3.10, 3.11, 3.12]`.
- **Caching**: Cache pip dependencies using `actions/cache`.
- **Security**: Run `pip-audit` or `safety check`.

## Recommended Gates

- `gate_python_pep8.md`
- `gate_global_docker.md`
- `gate_global_ci_github.md`
