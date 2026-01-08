# SKILL: Docker / Compose

Patterns:
- Use **multi-stage builds** to keep final image sizes small.
- Use named volumes for persistent data (DB, uploads).
- Keep build context small using `.dockerignore`.
- Separate dev (reload-enabled) vs prod (optimized) compose profiles.
- Use non-root users inside containers for security.
- Prefer official slim/alpine images as base.

Optimization:
- Order layers by frequency of change (OS -> Deps -> App Code).
- Combine `RUN` commands where logical to reduce Layer count.
- Clear package manager caches (`apt-get clean`) in the same layer.

Common Commands:
- Build: `docker compose build`
- Up (detached): `docker compose up -d`
- Logs: `docker compose logs -f [service]`
- Prune: `docker system prune -f`

Troubleshooting:
- Diagnose rebuild loops by watching file watchers and volume mounts.
- Check `docker inspect` for network or mount issues.

Evidence checklist:
- `checklists/DOCKER_BUILD_FAIL_EVIDENCE.md`
