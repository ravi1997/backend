# Context Schema Contract (Autofill)

This pack is **MD-only**, but it uses a **structured block** inside `01_PROJECT_CONTEXT.md` so agents can reliably infer:
- paths (backend/frontend)
- compose service names
- ports
- systemd unit names
- nginx site names
- repo roots

## Rule
Agents MUST parse the `AUTO_CONTEXT` block first. If a field is missing:
1) infer using `autofill/PATH_AND_SERVICE_INFERENCE.md`
2) if still unsure, default to **prod-safe** behavior and ask only the *minimal* follow-up questions.

## AUTO_CONTEXT keys

### Identity
- `app_name`: short id, e.g. `research-excellence`
- `env`: `dev|staging|production`
- `domain`: optional, e.g. `app.example.com`
- `repo_root`: usually `.`

### Layout
- `backend_dir`: `app|backend|server|.`
- `frontend_dir`: `frontend|client|ui|none`
- `python_package`: `yourapp` (the import package)
- `entrypoint`: `wsgi:app` or `yourapp.wsgi:app`

### Runtime
- `listen_host`: usually `0.0.0.0`
- `app_port`: e.g. `8000`
- `nginx_port`: e.g. `80` or `443`
- `health_path`: `/healthz`

### Docker (optional)
- `compose_file`: `docker-compose.yml`
- `compose_project`: optional name
- `compose_backend_service`: e.g. `web|api|backend`
- `compose_frontend_service`: e.g. `frontend`
- `compose_nginx_service`: e.g. `nginx`

### systemd (optional)
- `systemd_unit`: e.g. `myapp.service`
- `systemd_user`: `www-data|ubuntu|root`
- `systemd_workdir`: absolute path

### Logs (optional)
- `nginx_access_log`: e.g. `/var/log/nginx/access.log`
- `nginx_error_log`: e.g. `/var/log/nginx/error.log`
- `app_log`: file path or `journald`

### DB (optional)
- `db_kind`: `sqlite|postgres|mysql|mongo`
- `db_url_env`: e.g. `DATABASE_URL`
- `migration_tool`: `alembic|flask-migrate|none`

### Tests & Lint
- `test_cmd`: default `pytest -q`
- `lint_cmd`: default `ruff check . && ruff format .`
