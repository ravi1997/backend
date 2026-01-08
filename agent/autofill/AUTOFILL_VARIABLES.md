# Autofill Variables Dictionary

Agents must prefer these variables when generating steps, commands, and artifacts.

## Canonical variables
- `{APP}` = app_name
- `{ENV}` = env
- `{ROOT}` = repo_root
- `{BACKEND}` = backend_dir
- `{FRONTEND}` = frontend_dir
- `{PKG}` = python_package
- `{ENTRY}` = entrypoint
- `{PORT}` = app_port
- `{NGINX_PORT}` = nginx_port
- `{HEALTH}` = health_path
- `{COMPOSE}` = compose_file
- `{SVC_BACKEND}` = compose_backend_service
- `{SVC_NGINX}` = compose_nginx_service
- `{SVC_FRONTEND}` = compose_frontend_service
- `{UNIT}` = systemd_unit

## Default values (if missing)
- `{ENV}` = `production` (prod-safe)
- `{PORT}` = `8000`
- `{HEALTH}` = `/healthz`
- `{SVC_BACKEND}` = `web`
- `{SVC_NGINX}` = `nginx`
- `{SVC_FRONTEND}` = `frontend`
- `{COMPOSE}` = `docker-compose.yml`
