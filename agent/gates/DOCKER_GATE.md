# GATE: Docker Compliance Guard

**Purpose:** Final verification gate for Dockerfiles and container configurations.
**Source:** `gates/DOCKER_GATE.md`

## 1. Dockerfile Best Practices
- [ ] No `root` user used (checked with `USER` instruction)
- [ ] No fixed passwords or secrets in `ENV` or `RUN`
- [ ] Multistage builds used for compiled languages
- [ ] Smallest possible base image used

## 2. Image Metadata & Scanning
- [ ] `Trivy` or `Docker Scan` shows no High/Critical vulnerabilities
- [ ] `LABEL` metadata (maintainer, version, description) present
- [ ] Clear tagging strategy (no `:latest`)

## 3. Runtime Safety
- [ ] `HEALTHCHECK` is defined
- [ ] CPU and Memory limits are specified in `docker-compose.yml` or run script
- [ ] Non-essential ports are not exposed

## 4. Build Context
- [ ] `.dockerignore` exists and is effective (no `.git` or `node_modules` sent to daemon)
- [ ] Build context size is reasonable (e.g., < 100MB for most apps)

## Failure Procedure
If any of these fail:
1. Document the failure in `artifacts/BUILD_LOG.md`.
2. Re-route to `workflows/docker_image_optimization.md` if size/layer issues.
3. Do NOT mark task as complete.
