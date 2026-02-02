# DevOps Stack Detection

## Heuristics

- **Docker**: Presence of `Dockerfile`, `docker-compose.yml`, or `Containerfile`.
- **GitHub Actions**: Presence of `.github/workflows/*.yml`.
- **Kubernetes**: Presence of `k8s/`, `helm/`, or `charts/`.
- **Terraform**: Presence of `*.tf`.

## Signals

- If `Dockerfile` detected -> Activate `gate_global_docker`.
- If `.github/workflows` detected -> Activate `gate_global_ci_github`.
