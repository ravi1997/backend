# Flask Recovery Playbook

Use Issue-Key `Issue-Key: FLASK-<hash>`. Map to HC-FLASK-XXX.

## RECOVERY-FLASK-001: App Factory/Blueprint Issues
- Verify WSGI entry calls `create_app`; ensure blueprints registered in factory.
- Break circular imports by moving registration inside factory; isolate shared code.
- Validate: `flask routes` shows endpoints; sample request returns 200.

## RECOVERY-FLASK-002: Config/Env Problems
- Print `app.config` for environment; set `FLASK_ENV`/custom config var; ensure SECRET_KEY present via env/secret manager.
- Fix CORS/CSRF settings; set secure cookie flags.
- Validate: health endpoint succeeds; browser CORS preflight passes.

## RECOVERY-FLASK-003: DB/Migrations
- Check `DATABASE_URL`; install drivers; run `flask db current`/`flask db upgrade`.
- Resolve multiple migration heads via `flask db merge`; ensure sessions closed in teardown; tune pool.
- Validate: migrations apply cleanly; no pool exhaustion under simple load test.

## RECOVERY-FLASK-004: Deployment/Proxy
- Review gunicorn workers/timeouts; adjust worker class; confirm static files served by proxy.
- Add ProxyFix for forwarded headers; set MAX_CONTENT_LENGTH; configure upload dirs with secure filenames.
- Validate: app responds behind proxy; static assets served; uploads constrained.

## RECOVERY-FLASK-005: API/Logging/Security
- Add error handlers, structured logging with request IDs; enable rate limiting; set security headers.
- Validate: curl shows headers (HSTS, X-Content-Type-Options); rate limits enforced; errors return sanitized responses.
