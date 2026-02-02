# Flask Hard Cases & Failure Scenarios

Issue-Key example: `Issue-Key: FLASK-4c1d2e`. Prompt: `prompts/hard_cases/flask_hard_cases.txt`.

## App Factory & Blueprints

### HC-FLASK-001: App Factory Not Called
**Symptom:**
```
RuntimeError: Working outside of application context
```
**Likely Causes:** using global app instead of factory; not calling `create_app` in WSGI entry.
**Fast Diagnosis:** inspect wsgi.py/app.py; check environment var `FLASK_APP`.
**Fix Steps:** ensure WSGI/gunicorn calls `create_app`; use app_context in CLIs.
**Prevention:** use app factory pattern with explicit entrypoint tests.

### HC-FLASK-002: Blueprint Circular Imports
**Symptom:**
```
AttributeError: 'Blueprint' object has no attribute 'route'
```
**Likely Causes:** circular imports between blueprints and app creation.
**Fast Diagnosis:** check import graph; enable `python -X importtime`.
**Fix Steps:** register blueprints inside factory after creation; move shared code to separate module.
**Prevention:** keep routes in blueprint modules, avoid cross-importing app.

### HC-FLASK-003: Missing Blueprint Registration
**Symptom:** routes return 404 though defined.
**Likely Causes:** blueprint not registered or url_prefix mismatch.
**Fast Diagnosis:** print `app.url_map`; check factory registration.
**Fix Steps:** register blueprint with correct prefix; ensure import executed.
**Prevention:** test route discovery in integration tests.

## Configuration & Environments

### HC-FLASK-004: Wrong Config for Environment
**Symptom:** dev config loaded in prod (debug on).
**Likely Causes:** FLASK_ENV/FLASK_CONFIG not set; default config path wrong.
**Fast Diagnosis:** inspect `app.config`; log current env.
**Fix Steps:** set `FLASK_ENV`/custom env var; load config class by env; ensure `.env` read order correct.
**Prevention:** config loader tests per environment; default to production-safe config.

### HC-FLASK-005: Secrets Missing
**Symptom:**
```
RuntimeError: The session is unavailable because no secret key was set.
```
**Likely Causes:** SECRET_KEY not configured.
**Fast Diagnosis:** check app.config for SECRET_KEY.
**Fix Steps:** set SECRET_KEY via env/secret manager; avoid committing keys.
**Prevention:** config validation on startup; CI check env vars.

### HC-FLASK-006: CORS Misconfiguration
**Symptom:** browser CORS errors.
**Likely Causes:** flask-cors not configured; wildcard origins with credentials.
**Fast Diagnosis:** inspect CORS setup; check response headers.
**Fix Steps:** configure flask-cors with allowed origins/methods; avoid `supports_credentials` with `*`.
**Prevention:** integration tests from browser-like client.

### HC-FLASK-007: CSRF Handling Broken
**Symptom:** form submissions fail; CSRF token missing.
**Likely Causes:** not including CSRF token in forms; incorrect cookie settings.
**Fast Diagnosis:** check templates for `{{ csrf_token() }}`; inspect headers.
**Fix Steps:** enable Flask-WTF CSRF; ensure SameSite/secure flags; include token in API requests if required.
**Prevention:** CSRF tests; document API/token expectations.

### HC-FLASK-008: Session/Cookie Flags Insecure
**Symptom:** security review flags cookies missing Secure/HttpOnly/SameSite.
**Likely Causes:** default cookie settings not overridden.
**Fast Diagnosis:** inspect response headers; app.config cookie flags.
**Fix Steps:** set `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE` appropriately.
**Prevention:** security gate to assert cookie flags in tests.

## Database & Migrations

### HC-FLASK-009: DB URL Missing/Bad
**Symptom:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Likely Causes:** DATABASE_URL missing/wrong; wrong driver.
**Fast Diagnosis:** check env; try `psql`/`mysql` from container.
**Fix Steps:** set correct URL; install driver (psycopg2/mysqlclient); handle SSL params.
**Prevention:** config validation; connection test on startup.

### HC-FLASK-010: Alembic Migration Drift
**Symptom:** migrations out of sync; runtime errors on deploy.
**Likely Causes:** models changed without migration; multiple heads.
**Fast Diagnosis:** `flask db heads`, `flask db current`, `flask db history`.
**Fix Steps:** generate migration `flask db migrate`; resolve multiple heads with merge; apply `flask db upgrade`.
**Prevention:** CI gate: `flask db check` or compare models vs migrations; require migration in PRs with model changes.

### HC-FLASK-011: SQLAlchemy Connection Pool Exhaustion
**Symptom:** hanging requests/timeouts.
**Likely Causes:** connections not closed; pool too small.
**Fast Diagnosis:** enable pool logging; check `engine.pool.status()`.
**Fix Steps:** use scoped_session; ensure sessions closed in teardown; tune pool_size/max_overflow.
**Prevention:** add middleware/teardown to close sessions; monitor pool metrics.

### HC-FLASK-012: N+1 Query Issues
**Symptom:** slow endpoints, many repeated queries.
**Likely Causes:** lazy loading inside loops.
**Fast Diagnosis:** enable SQL echo; profile queries with flask-sqlalchemy-debugtoolbar.
**Fix Steps:** use selectinload/joinedload; batch queries.
**Prevention:** perf tests; query count assertions.

## Deployment/WSGI

### HC-FLASK-013: Gunicorn Worker Misconfig
**Symptom:**
```
[CRITICAL] WORKER TIMEOUT
```
**Likely Causes:** workers too few/too slow; sync worker blocking.
**Fast Diagnosis:** check gunicorn config; request latency.
**Fix Steps:** increase workers/timeout; use gevent/uvicorn workers for async; profile app.
**Prevention:** perf test under load; set timeouts per workload.

### HC-FLASK-014: Static Files 404 in Production
**Symptom:** static assets missing.
**Likely Causes:** wrong static_folder path; not served by proxy.
**Fast Diagnosis:** check `app.static_folder`; review nginx config.
**Fix Steps:** serve static via proxy; set correct static_url_path; collect assets in container.
**Prevention:** deploy check hitting static assets; document asset pipeline.

### HC-FLASK-015: Reverse Proxy Headers Missing
**Symptom:** Flask sees http instead of https; URL generation wrong.
**Likely Causes:** missing `ProxyFix` or forwarded headers.
**Fast Diagnosis:** inspect request headers; check WSGI middleware.
**Fix Steps:** add `from werkzeug.middleware.proxy_fix import ProxyFix`; configure num_proxies; set `PREFERRED_URL_SCHEME`.
**Prevention:** proxy integration tests; enforce forwarded headers config.

### HC-FLASK-016: Request Body Size Limits
**Symptom:**
```
Request Entity Too Large
```
**Likely Causes:** proxy/app limits too small.
**Fast Diagnosis:** check nginx/proxy configs; Flask `MAX_CONTENT_LENGTH`.
**Fix Steps:** raise limits carefully; stream uploads; validate file size.
**Prevention:** document size limits; add tests for max upload.

### HC-FLASK-017: File Upload Path Traversal
**Symptom:** files written outside upload dir.
**Likely Causes:** unsanitized filename.
**Fast Diagnosis:** attempt `../../tmp/pwn` upload; inspect saved path.
**Fix Steps:** use `werkzeug.utils.secure_filename`; store in dedicated directory.
**Prevention:** security tests for traversal; allowlist extensions.

## APIs & Middleware

### HC-FLASK-018: JSON Body Parsing Errors
**Symptom:**
```
BadRequest: Failed to decode JSON object
```
**Likely Causes:** missing `Content-Type: application/json`; large body; trailing commas.
**Fast Diagnosis:** inspect request headers/body.
**Fix Steps:** enforce content-type; handle errors gracefully; add size limits.
**Prevention:** client validation; request schema validation with marshmallow/pydantic.

### HC-FLASK-019: Error Handling Missing
**Symptom:** stack traces leaked to clients.
**Likely Causes:** DEBUG on; no errorhandlers.
**Fast Diagnosis:** check app.config DEBUG; errorhandler registration.
**Fix Steps:** disable DEBUG; add error handlers; log safely.
**Prevention:** prod config disables debug; tests for error responses.

### HC-FLASK-020: Logging Not Structured
**Symptom:** hard to trace requests; missing request IDs.
**Likely Causes:** default logging; no request context info.
**Fast Diagnosis:** check logs for request ids.
**Fix Steps:** add logging formatter with request id; propagate X-Request-ID.
**Prevention:** logging middleware; CI check for structured logging config.

### HC-FLASK-021: Caching Stale Data
**Symptom:** outdated responses.
**Likely Causes:** cache invalidation missing; shared cache key collisions.
**Fast Diagnosis:** inspect cache keys; logs.
**Fix Steps:** namespace keys by user/env; set TTLs; add cache busting on updates.
**Prevention:** caching strategy doc; tests for cache invalidation.

## Security

### HC-FLASK-022: Open Redirects
**Symptom:**
```
redirect to user-provided url
```
**Likely Causes:** redirecting unvalidated next URL.
**Fast Diagnosis:** search for `request.args.get("next")` usage.
**Fix Steps:** validate host/paths; use allowlist.
**Prevention:** security tests for redirects.

### HC-FLASK-023: Missing Rate Limiting
**Symptom:** excessive requests overwhelm app.
**Likely Causes:** no rate limiting middleware.
**Fast Diagnosis:** inspect extensions; logs show flood.
**Fix Steps:** add Flask-Limiter or proxy rate limits; set sensible defaults.
**Prevention:** rate limit policy; load test.

### HC-FLASK-024: Headers Security Gaps
**Symptom:** security scan flags missing headers.
**Likely Causes:** default responses lack security headers.
**Fast Diagnosis:** check response headers via curl.
**Fix Steps:** add headers (HSTS, X-Content-Type-Options, X-Frame-Options, CSP where applicable).
**Prevention:** middleware to set headers; security test in CI.

### HC-FLASK-025: CLI Commands Without App Context
**Symptom:**
```
RuntimeError: No application found. Either work inside a view function or push an application context.
```
**Likely Causes:** CLI defined without app context push.
**Fast Diagnosis:** inspect CLI code; check use of `with app.app_context():`.
**Fix Steps:** wrap CLI logic with app_context; import app factory in CLI entry.
**Prevention:** tests for CLI commands; standard CLI template using app context.

## Issue-Key and Prompt Mapping
- Example Issue-Key: `Issue-Key: FLASK-a2d3f0`
- Use prompt: `prompts/hard_cases/flask_hard_cases.txt`
