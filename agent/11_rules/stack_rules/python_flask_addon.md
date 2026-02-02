# Python/Flask Rules Add-On

- Require app factory pattern; forbid global app instances in modules consumed by blueprints.
- Enforce SECRET_KEY from environment/secret manager; reject configs enabling DEBUG in production contexts.
- Mandate secure cookies (Secure, HttpOnly, SameSite=Lax or Strict) and CSRF protection for forms/session-backed APIs.
- Database: sessions must close per request; migrations required for schema changes; deployments block if `flask db heads` shows multiple heads.
- HTTP safety: CORS configured explicitly (no `*` with credentials); security headers (HSTS, X-Content-Type-Options, X-Frame-Options) applied via middleware.
- File uploads use `secure_filename`, size limits, and allowed extensions; reject path traversal.
- Logging: include request ID; prevent logging of secrets/request bodies unless masked.
- Deployment: gunicorn worker type matches app (async vs sync); proxy headers handled via ProxyFix where applicable.
