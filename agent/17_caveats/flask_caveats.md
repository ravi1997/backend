# Flask Caveats & Footguns

Issue-Key example: `Issue-Key: FLASK-7c9d10`.

- Always use app factory; avoid global app imports to prevent circular dependencies.
- Blueprints must be registered inside factory; keep route files free of side-effect imports.
- Load config per environment; default to production-safe (DEBUG off, secure cookies, CSRF enabled).
- SECRET_KEY must come from env/secret manager, never committed.
- CORS setup must avoid `supports_credentials` with wildcard origin.
- Session cookies need Secure/HttpOnly/SameSite; enforce via config and tests.
- Database sessions should close in teardown; connection leaks will starve pools.
- Alembic migrations must stay in sync; require migration for model changes.
- Gunicorn worker counts/timeouts must match workload; async apps need async workers.
- Static assets should be served by proxy/CDN; configure `static_url_path` accordingly.
- File uploads must use `secure_filename` and size/extension allowlists.
- Security headers and rate limiting are not default—add middleware and tests.
