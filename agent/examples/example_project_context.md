# Example: Filled Project Context

This is a complete example of a filled `01_PROJECT_CONTEXT.md` for a Flask-based eye donation pledge application.

## AUTO_CONTEXT

```yaml
app_name: "eye-donation-pledge"
env: "dev"
domain: "localhost:8000"
repo_root: "."
backend_dir: "."
frontend_dir: "none"
python_package: "app"
entrypoint: "wsgi:app"
listen_host: "0.0.0.0"
app_port: 8000
nginx_port: 80
health_path: "/healthz"

compose_file: "docker-compose.yml"
compose_project: "eye-donation"
compose_backend_service: "web"
compose_frontend_service: ""
compose_nginx_service: "nginx"

systemd_unit: "eye-donation.service"
systemd_user: "www-data"
systemd_workdir: "/opt/eye-donation"

nginx_access_log: "/var/log/nginx/access.log"
nginx_error_log: "/var/log/nginx/error.log"
app_log: "journald"

db_kind: "postgres"
db_url_env: "DATABASE_URL"
migration_tool: "alembic"

test_cmd: "pytest -q"
lint_cmd: "ruff check . && ruff format ."
```

## Identity
- Project name: Eye Donation Pledge System
- Repo URL (GitHub/GitLab): https://github.com/example/eye-donation-pledge
- Primary language/runtime: Python 3.11
- Framework: Flask 3.0, Jinja2, Tailwind CSS

## Environments
- Dev URL: http://localhost:8000
- Staging URL: https://staging.eyepledge.example.com
- Production URL: https://eyepledge.example.com

## Run & deploy
- Local run command: `docker compose up`
- Docker compose files: `docker-compose.yml`, `docker-compose.prod.yml`
- systemd services (if any): `eye-donation.service`
- Reverse proxy: nginx + `/etc/nginx/sites-available/eye-donation`
- WSGI server: gunicorn + `gunicorn.conf.py`

## Data
- DB type(s): PostgreSQL 15
- Migration tool: Alembic (via Flask-Migrate)
- Redis/Queue: Redis for rate limiting

## Tests & quality
- Test runner: pytest
- Lint/format: ruff
- CI: GitHub Actions (`.github/workflows/ci.yml`)

## Sensitive/PHI notes
- PHI present? yes
- Any endpoints needing extra masking: `/pledge`, `/admin/pledges`

## Agent permissions
- Dev/staging can auto-fix and commit? yes
- Production write actions blocked? yes
