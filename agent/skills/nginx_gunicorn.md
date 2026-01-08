# SKILL: Nginx + Gunicorn

Common checks:
- socket vs TCP mismatch
- permissions on unix socket
- proxy timeout vs gunicorn timeout mismatch
- worker count vs traffic
- preload vs lazy loading
- max request size limits

Golden defaults (starting points):
- `proxy_read_timeout` >= gunicorn timeout + margin
- set `X-Request-ID` and pass through
- enable `access_log` with request id

Use evidence checklist: `checklists/NGINX_502_EVIDENCE.md`
