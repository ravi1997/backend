# Autofill: Path & Service Inference Rules

Goal: avoid deep inputs. If `AUTO_CONTEXT` is incomplete, infer using repo contents and common conventions.

## 1) Repo root
- If file `pyproject.toml` exists at root → `repo_root="."`
- Else if `backend/pyproject.toml` exists → `repo_root="backend"`
- Else if `app/pyproject.toml` exists → `repo_root="app"`

## 2) Backend directory
Prefer in order:
1. `backend/` if contains `pyproject.toml` or `requirements.txt`
2. `app/` if contains Flask entry files
3. `server/`
4. root `.` if contains Flask package

## 3) Flask package name (python_package)
Try in order:
- directory inside backend_dir that contains `__init__.py` and `routes.py` or `wsgi.py`
- if `wsgi.py` exists, parse import line (best effort)
Fallback: `yourapp`

## 4) Entrypoint (wsgi)
Try in order:
- `wsgi.py` exists → `wsgi:app`
- `app.py` exists → `app:app`
- `yourapp/wsgi.py` exists → `yourapp.wsgi:app`

## 5) Docker Compose service names
If `docker-compose.yml` exists:
- If service contains `gunicorn`/`flask` command → `compose_backend_service`
- If service has `nginx` image → `compose_nginx_service`
- If service builds from `frontend/` → `compose_frontend_service`

Common defaults:
- backend: `web` or `api`
- nginx: `nginx`
- frontend: `frontend`

## 6) Ports
- If compose exposes `8000:8000` → app_port=8000
- Else if gunicorn config uses `:8000` → app_port=8000
Fallback: app_port=8000, nginx_port=80

## 7) systemd unit name
If `deploy/` or `systemd/` directory exists, search for `*.service`.
Else infer as `{app_name}.service`.

## 8) Log locations
- If nginx present: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- If systemd: use `journalctl -u {unit} -e`
- If docker: use `docker compose logs --tail=200 {service}`

## 9) Minimal follow-up questions (only if needed)
Ask at most one line for each missing “critical” field:
- app_name
- env
- backend_dir (only if not inferable)
- compose_backend_service (only if docker is used)

If env unclear → assume production rules (read-only).
