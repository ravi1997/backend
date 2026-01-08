# Contract: Repo Layout (Flask + Jinja + Tailwind)

Recommended:
- `app/` or `src/` contains Flask package
- `templates/` for Jinja
- `static/` for built assets
- `tests/` for pytest
- `migrations/` if Alembic

Agent assumptions:
- app factory: `create_app()`
- gunicorn entry: `module:create_app()`
