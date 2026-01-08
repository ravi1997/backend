# Skill: Docker Compose (Dev + Prod)

## Dev
- bind-mount only source directories
- keep build outputs in named volumes
- avoid watching node_modules/dist/build

## Prod
- pinned image tags
- healthchecks
- restart policies
- env via .env or secrets

## Debug commands
- `docker compose ps`
- `docker compose logs -f <svc>`
- `docker inspect <container>`
