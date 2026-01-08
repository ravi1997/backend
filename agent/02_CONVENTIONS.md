# Conventions

## Code style
- Python: ruff (format + lint) preferred.
- Use type hints for new code.
- Keep functions small; prefer early returns.
- Logging: structured where possible; include request_id/trace_id.

## Project layout defaults
- `app/` or `<package>/` for server code
- `tests/` for pytest
- `nginx/` for proxy config
- `scripts/` for dev helpers

## Git
- Branches: `fix/<slug>` or `feat/<slug>`
- Commits: imperative, scoped, with context:
  - `fix(nginx): handle upstream timeout`
  - `feat(auth): add refresh token rotation`

## Security
- Never log:
  - Authorization, cookies, tokens, passwords
  - request bodies containing PHI/PII
- Prefer allowlists to denylists for inputs.
- Validate file paths; block traversal.
- Use parameterized SQL.

## Documentation artifacts
Use templates under `agent/artifacts/`:
- PR summary
- Incident report
- Postmortem
- Runbook

---

## Default Decisions
(Minimize User Input)

When user input is incomplete, assume:
- Environment: **staging** unless explicitly production.
- Web stack: Nginx → Gunicorn → Flask.
- Logs: prefer `docker compose logs -f` or `journalctl -u <service> -f`.
- Testing: `pytest -q`; if missing, create minimal pytest setup.
- Formatting: `ruff format .` and `ruff check --fix .` if ruff exists; otherwise `black` + `flake8`.
- Database migrations:
  - Flask-SQLAlchemy + Alembic if relational.
  - If unknown, detect via repo contents and proceed.

Always add:
- Request IDs and correlation IDs
- Clear error boundaries and useful logs (redacted)
- Health endpoints (`/healthz`, `/readyz`)
- Timeouts aligned across Nginx/Gunicorn/app

---

## Project Bootstrap Conventions

### Flask-only
- app factory `create_app()`
- gunicorn service/compose uses that
- enable PHI-safe logging rules

### Flask + React
- backend: `/api/*`
- frontend: `/` routes
- CORS configured in dev only

### Always
- health endpoints: `/healthz` and `/readyz`
- request-id propagation at proxy and app
- tests + lint as standard gates
