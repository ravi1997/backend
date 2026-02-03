# Docker Hard Cases & Failure Scenarios

## Overview

This document catalogs real-world Docker failure scenarios with detailed symptoms, diagnosis, and fixes.

---

## BUILD FAILURES

### HC-DOCKER-001: Missing Build Context

**Symptom:**

```
ERROR [internal] load build context
ERROR: failed to solve: failed to read dockerfile: open /var/lib/docker/tmp/.../Dockerfile: no such file or directory
```

**Likely Causes:**

- Dockerfile not in build context path
- `.dockerignore` excluding Dockerfile
- Wrong working directory when running `docker build`

**Fast Diagnosis:**

```bash
ls -la Dockerfile
cat .dockerignore | grep -i dockerfile
pwd
```

**Fix Steps:**

1. Ensure Dockerfile is in current directory or specify path: `docker build -f path/to/Dockerfile .`
2. Check `.dockerignore` doesn't exclude Dockerfile
3. Verify build context path (the `.` in `docker build .`)

**Prevention:**

- Add pre-build check in CI: `test -f Dockerfile`
- Document Dockerfile location in README

---

### HC-DOCKER-002: Multi-Stage COPY Failure

**Symptom:**

```
COPY failed: file not found in build context or excluded by .dockerignore: stat app/dist: file does not exist
```

**Likely Causes:**

- Source stage didn't produce expected artifacts
- Wrong stage name in `COPY --from=`
- Build artifacts in wrong directory

**Fast Diagnosis:**

```bash
docker build --target=builder -t debug-stage .
docker run --rm debug-stage ls -la /expected/path
```

**Fix Steps:**

1. Verify source stage builds successfully: `docker build --target=<stage-name> .`
2. Check artifact paths match between stages
3. Ensure stage names are correct in `COPY --from=<stage>`

**Prevention:**

- Add intermediate stage validation
- Use explicit paths, avoid wildcards in multi-stage COPY
- Gate: Verify multi-stage builds produce expected artifacts

---

### HC-DOCKER-003: Architecture Mismatch (ARM64 vs AMD64)

**Symptom:**

```
WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)
exec /usr/local/bin/docker-entrypoint.sh: exec format error
```

**Likely Causes:**

- Building on Apple Silicon (M1/M2) for AMD64 deployment
- Base image doesn't support target architecture
- Missing `--platform` flag

**Fast Diagnosis:**

```bash
docker inspect <image> | grep Architecture
uname -m
```

**Fix Steps:**

1. Specify platform explicitly: `docker build --platform=linux/amd64 .`
2. Use multi-arch base images
3. For M1/M2 Macs, enable Rosetta in Docker Desktop or use buildx:

   ```bash
   docker buildx build --platform=linux/amd64,linux/arm64 -t myapp .
   ```

**Prevention:**

- Always specify `--platform` in Dockerfile FROM statements
- Use `docker buildx` for multi-platform builds
- CI gate: Verify image architecture matches deployment target

---

### HC-DOCKER-004: Node-gyp / Native Dependencies Compile Errors

**Symptom:**

```
gyp ERR! build error
gyp ERR! stack Error: `make` failed with exit code: 2
npm ERR! node-gyp rebuild
```

**Likely Causes:**

- Missing build tools (gcc, g++, make, python)
- Wrong Node.js version for native module
- Alpine Linux missing glibc

**Fast Diagnosis:**

```bash
docker run --rm <image> which gcc make python3
docker run --rm <image> node --version
```

**Fix Steps:**

1. Install build dependencies:

   ```dockerfile
   # Debian/Ubuntu
   RUN apt-get update && apt-get install -y python3 make g++
   
   # Alpine
   RUN apk add --no-cache python3 make g++
   ```

2. Use correct Node.js version matching native module requirements
3. For Alpine, consider switching to Debian slim or install compatibility libs

**Prevention:**

- Use official Node.js images with build tools: `node:20-bullseye` instead of `node:20-alpine`
- Document native dependencies in README
- Pin native module versions

---

### HC-DOCKER-005: Python Wheels Failing to Build

**Symptom:**

```
Building wheel for <package> (setup.py) ... error
ERROR: Failed building wheel for cryptography
```

**Likely Causes:**

- Missing system libraries (libssl-dev, libffi-dev, etc.)
- Wrong Python version
- Outdated pip/setuptools

**Fast Diagnosis:**

```bash
docker run --rm <image> python3 --version
docker run --rm <image> pip list | grep -E "pip|setuptools|wheel"
```

**Fix Steps:**

1. Install required system libraries:

   ```dockerfile
   RUN apt-get update && apt-get install -y \
       build-essential \
       libssl-dev \
       libffi-dev \
       python3-dev
   ```

2. Upgrade pip/setuptools before installing packages:

   ```dockerfile
   RUN pip install --upgrade pip setuptools wheel
   ```

3. Use pre-built wheels when available: `pip install --only-binary :all: <package>`

**Prevention:**

- Use official Python images with build tools
- Cache pip dependencies in separate layer
- Consider using pre-built wheels or conda

---

## RUNTIME FAILURES

### HC-DOCKER-006: Container Exits Immediately

**Symptom:**

```
docker ps -a
CONTAINER ID   STATUS                     EXITED (0) 2 seconds ago
```

**Likely Causes:**

- CMD/ENTRYPOINT runs and completes
- Application crashes on startup
- Missing environment variables

**Fast Diagnosis:**

```bash
docker logs <container-id>
docker inspect <container-id> | grep -A 10 "Cmd\|Entrypoint"
docker run --rm <image> sh -c "echo 'Container started'; sleep 10"
```

**Fix Steps:**

1. Check logs for crash/error messages
2. Ensure CMD runs a long-lived process (not a script that exits)
3. Add healthcheck to verify application readiness
4. Run interactively to debug: `docker run -it --entrypoint sh <image>`

**Prevention:**

- Use proper process managers (tini, dumb-init)
- Implement healthchecks
- Log startup sequence clearly

---

### HC-DOCKER-007: Permission Denied (Non-Root User)

**Symptom:**

```
Error: EACCES: permission denied, open '/app/data/file.txt'
touch: cannot touch '/app/file': Permission denied
```

**Likely Causes:**

- Running as non-root user without proper ownership
- Volume mounts owned by host user (UID mismatch)
- Files copied before USER directive

**Fast Diagnosis:**

```bash
docker run --rm <image> id
docker run --rm <image> ls -la /app
docker run --rm -v $(pwd)/data:/app/data <image> ls -la /app/data
```

**Fix Steps:**

1. Set ownership after COPY:

   ```dockerfile
   COPY --chown=node:node . /app
   ```

2. Create user with specific UID matching host:

   ```dockerfile
   RUN useradd -u 1000 -m appuser
   USER appuser
   ```

3. For volumes, use entrypoint script to fix permissions:

   ```bash
   chown -R $(id -u):$(id -g) /app/data
   ```

**Prevention:**

- Always use `--chown` with COPY when using USER directive
- Document UID/GID requirements
- Use named volumes instead of bind mounts when possible

---

### HC-DOCKER-008: Bind Mount Overrides node_modules / venv

**Symptom:**

```
Error: Cannot find module 'express'
ModuleNotFoundError: No module named 'flask'
```

**Likely Causes:**

- Volume mount of source code overrides installed dependencies
- Host's node_modules/venv different from container's

**Fast Diagnosis:**

```bash
docker compose config | grep -A 5 volumes
docker run --rm <image> ls -la /app/node_modules
```

**Fix Steps:**

1. Use anonymous volume to preserve dependencies:

   ```yaml
   volumes:
     - .:/app
     - /app/node_modules  # Anonymous volume prevents override
   ```

2. Or use named volume:

   ```yaml
   volumes:
     - .:/app
     - node_modules:/app/node_modules
   ```

3. For Python, exclude venv:

   ```yaml
   volumes:
     - .:/app
     - /app/venv
   ```

**Prevention:**

- Always use anonymous/named volumes for dependency directories
- Document volume strategy in docker-compose.yml comments
- Add to .dockerignore: node_modules, venv, **pycache**

---

### HC-DOCKER-009: Healthcheck Failing

**Symptom:**

```
docker ps
STATUS: Up 2 minutes (unhealthy)
```

**Likely Causes:**

- Application not listening on expected port
- Healthcheck endpoint not implemented
- Healthcheck timeout too short
- Wrong protocol (HTTP vs HTTPS)

**Fast Diagnosis:**

```bash
docker inspect <container> | grep -A 20 Healthcheck
docker exec <container> curl -f http://localhost:3000/health || echo "Failed"
docker logs <container>
```

**Fix Steps:**

1. Verify application is listening:

   ```bash
   docker exec <container> netstat -tlnp
   ```

2. Adjust healthcheck parameters:

   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
     CMD curl -f http://localhost:3000/health || exit 1
   ```

3. Implement proper health endpoint in application
4. Install curl/wget in image if using CMD healthcheck

**Prevention:**

- Implement /health endpoint in all services
- Test healthcheck locally before deploying
- Use appropriate start-period for slow-starting apps

---

### HC-DOCKER-010: Port Binding Conflicts

**Symptom:**

```
Error response from daemon: driver failed programming external connectivity: 
Bind for 0.0.0.0:3000 failed: port is already allocated
```

**Likely Causes:**

- Another container using the same port
- Host service using the port
- Previous container not cleaned up

**Fast Diagnosis:**

```bash
docker ps -a | grep 3000
sudo lsof -i :3000
sudo netstat -tlnp | grep 3000
```

**Fix Steps:**

1. Stop conflicting container: `docker stop <container>`
2. Change port mapping: `docker run -p 3001:3000 <image>`
3. Clean up stopped containers: `docker container prune`
4. Use dynamic port allocation: `docker run -P <image>`

**Prevention:**

- Use docker compose with unique port assignments
- Document port usage in README
- Use reverse proxy (Traefik, nginx) to avoid port conflicts

---

## NETWORKING ISSUES

### HC-DOCKER-011: Service DNS Not Resolving

**Symptom:**

```
getaddrinfo ENOTFOUND postgres
curl: (6) Could not resolve host: api
```

**Likely Causes:**

- Services not on same Docker network
- Using default bridge network (no DNS)
- Wrong service name in connection string

**Fast Diagnosis:**

```bash
docker network ls
docker network inspect <network-name>
docker exec <container> nslookup postgres
docker exec <container> ping api
```

**Fix Steps:**

1. Use user-defined network (not default bridge):

   ```yaml
   networks:
     app-network:
   services:
     api:
       networks:
         - app-network
   ```

2. Verify service names match in connection strings
3. Ensure all services are on the same network

**Prevention:**

- Always use user-defined networks in docker-compose
- Use service names (not localhost) for inter-container communication
- Document network topology

---

### HC-DOCKER-012: Wrong Network Attachment

**Symptom:**

```
Connection refused when connecting to other service
Services can't communicate despite being in same compose file
```

**Likely Causes:**

- Service not attached to correct network
- Multiple networks causing routing issues
- Network mode: host preventing container networking

**Fast Diagnosis:**

```bash
docker inspect <container> | grep -A 20 Networks
docker network inspect <network> | grep -A 5 Containers
```

**Fix Steps:**

1. Explicitly define networks in docker-compose:

   ```yaml
   services:
     api:
       networks:
         - backend
     db:
       networks:
         - backend
   networks:
     backend:
   ```

2. Remove `network_mode: host` if using service discovery
3. Verify network attachment: `docker network inspect <network>`

**Prevention:**

- Explicitly define networks in compose files
- Avoid mixing network_mode: host with service networking
- Use network aliases for complex topologies

---

### HC-DOCKER-013: Cannot Reach Host Service from Container

**Symptom:**

```
Connection refused when trying to connect to localhost:5432 from container
Cannot access host's PostgreSQL/MySQL from container
```

**Likely Causes:**

- Using localhost/127.0.0.1 instead of host gateway
- Host firewall blocking container traffic
- Service not listening on 0.0.0.0

**Fast Diagnosis:**

```bash
docker run --rm <image> ping host.docker.internal
docker run --rm <image> curl host.docker.internal:5432
sudo netstat -tlnp | grep 5432
```

**Fix Steps:**

1. Use special DNS name:
   - Linux: `host.docker.internal` (requires --add-host)
   - Mac/Windows: `host.docker.internal` (built-in)

   ```yaml
   extra_hosts:
     - "host.docker.internal:host-gateway"
   ```

2. Ensure host service listens on 0.0.0.0, not 127.0.0.1
3. Check firewall rules allow Docker bridge network

**Prevention:**

- Use `host.docker.internal` for host services
- Configure host services to listen on all interfaces
- Document host service requirements

---

### HC-DOCKER-014: Reverse Proxy Misrouting

**Symptom:**

```
502 Bad Gateway from nginx
Traefik routes to wrong container
```

**Likely Causes:**

- Wrong upstream port in proxy config
- Service not ready when proxy starts
- Missing proxy network attachment

**Fast Diagnosis:**

```bash
docker logs <proxy-container>
docker exec <proxy> curl http://backend:3000
docker network inspect <proxy-network>
```

**Fix Steps:**

1. Verify backend service is on proxy network:

   ```yaml
   services:
     backend:
       networks:
         - proxy-network
   ```

2. Check proxy configuration points to correct service:port
3. Add depends_on and healthchecks:

   ```yaml
   proxy:
     depends_on:
       backend:
         condition: service_healthy
   ```

**Prevention:**

- Use healthchecks for all proxied services
- Attach proxy and backends to same network
- Test proxy config with `nginx -t` or equivalent

---

## DOCKER COMPOSE PITFALLS

### HC-DOCKER-015: depends_on Doesn't Wait for Readiness

**Symptom:**

```
Application starts before database is ready
Connection refused errors on startup
```

**Likely Causes:**

- depends_on only waits for container start, not readiness
- No healthcheck defined
- Application doesn't retry connections

**Fast Diagnosis:**

```bash
docker compose logs
docker compose ps
```

**Fix Steps:**

1. Add healthcheck to dependency:

   ```yaml
   db:
     healthcheck:
       test: ["CMD", "pg_isready", "-U", "postgres"]
       interval: 5s
       timeout: 5s
       retries: 5
   ```

2. Use condition in depends_on:

   ```yaml
   app:
     depends_on:
       db:
         condition: service_healthy
   ```

3. Implement retry logic in application
4. Use wait-for-it.sh or dockerize tool

**Prevention:**

- Always add healthchecks to databases and dependencies
- Use `condition: service_healthy` in depends_on
- Implement connection retry logic in applications

---

### HC-DOCKER-016: env_file Missing or Wrong Path

**Symptom:**

```
Environment variable not set in container
Application fails due to missing config
```

**Likely Causes:**

- .env file not in correct location
- Wrong path in env_file directive
- .env in .gitignore but not .dockerignore

**Fast Diagnosis:**

```bash
ls -la .env
docker compose config | grep -A 10 environment
docker exec <container> env
```

**Fix Steps:**

1. Verify .env file exists: `test -f .env || cp .env.example .env`
2. Check env_file path in docker-compose.yml:

   ```yaml
   env_file:
     - .env  # Relative to docker-compose.yml location
   ```

3. Ensure .env is not in .dockerignore
4. Use explicit environment variables for critical config

**Prevention:**

- Provide .env.example in repo
- Add validation: `test -f .env || (echo ".env missing" && exit 1)`
- Document required environment variables

---

### HC-DOCKER-017: Volume Ownership Mismatch

**Symptom:**

```
Permission denied writing to mounted volume
Files created in container owned by root on host
```

**Likely Causes:**

- Container runs as root, host user is non-root
- UID/GID mismatch between host and container
- Named volume with wrong permissions

**Fast Diagnosis:**

```bash
docker exec <container> id
ls -la <mounted-volume-path>
docker volume inspect <volume-name>
```

**Fix Steps:**

1. Run container as host user:

   ```yaml
   user: "${UID}:${GID}"
   ```

2. Use entrypoint to fix permissions:

   ```bash
   chown -R $(id -u):$(id -g) /app/data
   ```

3. Create user in Dockerfile with matching UID:

   ```dockerfile
   ARG UID=1000
   RUN useradd -u $UID -m appuser
   USER appuser
   ```

**Prevention:**

- Always specify user in docker compose for development
- Use consistent UID/GID across team
- Document ownership requirements

---

## SECRETS & SECURITY

### HC-DOCKER-018: Leaked Secrets in Image Layers

**Symptom:**

```
docker history <image> shows sensitive data
Secrets visible in image layers
```

**Likely Causes:**

- ARG used for secrets (persisted in image)
- Secrets copied into image
- Multi-stage build not removing secrets

**Fast Diagnosis:**

```bash
docker history <image>
docker save <image> -o image.tar && tar -xf image.tar && grep -r "SECRET" .
```

**Fix Steps:**

1. Use build secrets (BuildKit):

   ```dockerfile
   # syntax=docker/dockerfile:1
   RUN --mount=type=secret,id=mysecret \
     cat /run/secrets/mysecret
   ```

2. Never use ARG for secrets
3. Use multi-stage builds and don't COPY secrets to final stage
4. Use environment variables at runtime, not build time

**Prevention:**

- Enable BuildKit: `DOCKER_BUILDKIT=1`
- Use Docker secrets or external secret management
- Scan images for secrets: `docker scan <image>`
- Gate: Verify no secrets in image layers

---

### HC-DOCKER-019: Using 'latest' Tags

**Symptom:**

```
Inconsistent builds across environments
"Works on my machine" issues
Unexpected breaking changes
```

**Likely Causes:**

- Base image using :latest tag
- No version pinning
- Upstream image updated with breaking changes

**Fast Diagnosis:**

```bash
grep "FROM.*:latest" Dockerfile
docker inspect <image> | grep -A 5 "RepoTags\|RepoDigests"
```

**Fix Steps:**

1. Pin to specific versions:

   ```dockerfile
   FROM node:20.11.0-alpine3.19
   # NOT: FROM node:latest
   ```

2. Use digest for immutability:

   ```dockerfile
   FROM node:20.11.0@sha256:abc123...
   ```

3. Update regularly with controlled process

**Prevention:**

- Never use :latest in production Dockerfiles
- Use Dependabot or Renovate for automated updates
- Gate: Reject Dockerfiles with :latest tags

---

### HC-DOCKER-020: No SBOM / Vulnerability Scanning

**Symptom:**

```
Unknown vulnerabilities in production
Compliance failures
Security incidents from known CVEs
```

**Likely Causes:**

- No vulnerability scanning in CI/CD
- Outdated base images
- No dependency tracking

**Fast Diagnosis:**

```bash
docker scan <image>
trivy image <image>
syft <image> -o json
```

**Fix Steps:**

1. Add scanning to CI:

   ```yaml
   - name: Scan image
     run: docker scan --severity high <image>
   ```

2. Use Trivy or Grype:

   ```bash
   trivy image --severity HIGH,CRITICAL <image>
   ```

3. Generate SBOM:

   ```bash
   syft <image> -o spdx-json > sbom.json
   ```

4. Update base images regularly

**Prevention:**

- Integrate scanning in CI/CD pipeline
- Set vulnerability thresholds (fail on HIGH/CRITICAL)
- Automate base image updates
- Gate: No HIGH/CRITICAL vulnerabilities in production images

---

## PERFORMANCE ISSUES

### HC-DOCKER-021: Huge Image Sizes

**Symptom:**

```
Image size: 2.5GB for simple Node.js app
Slow pulls and deployments
High storage costs
```

**Likely Causes:**

- Using full OS base images
- Not using multi-stage builds
- Including build tools in final image
- Not cleaning up package manager cache

**Fast Diagnosis:**

```bash
docker images | grep <image>
docker history <image>
dive <image>  # Interactive layer analysis
```

**Fix Steps:**

1. Use slim/alpine base images:

   ```dockerfile
   FROM node:20-alpine  # ~100MB vs node:20 ~900MB
   ```

2. Multi-stage builds:

   ```dockerfile
   FROM node:20 AS builder
   RUN npm ci && npm run build
   
   FROM node:20-alpine
   COPY --from=builder /app/dist /app/dist
   ```

3. Clean up in same layer:

   ```dockerfile
   RUN apt-get update && apt-get install -y curl \
       && rm -rf /var/lib/apt/lists/*
   ```

4. Use .dockerignore:

   ```
   node_modules
   .git
   *.md
   ```

**Prevention:**

- Target image size limits (e.g., <500MB for Node apps)
- Use dive or docker-slim for analysis
- Gate: Fail if image size exceeds threshold

---

### HC-DOCKER-022: Slow Rebuild Due to Cache Bust

**Symptom:**

```
Every build reinstalls all dependencies
Build time: 10+ minutes for small changes
```

**Likely Causes:**

- COPY . before dependency installation
- Changing files invalidate cache
- No layer optimization

**Fast Diagnosis:**

```bash
docker build --progress=plain . 2>&1 | grep "CACHED"
```

**Fix Steps:**

1. Optimize layer order:

   ```dockerfile
   # Good: Copy dependency files first
   COPY package*.json ./
   RUN npm ci
   COPY . .
   
   # Bad: Copy everything first
   # COPY . .
   # RUN npm ci
   ```

2. Use BuildKit cache mounts:

   ```dockerfile
   RUN --mount=type=cache,target=/root/.npm \
     npm ci
   ```

3. Leverage multi-stage caching:

   ```dockerfile
   FROM node:20 AS deps
   COPY package*.json ./
   RUN npm ci
   ```

**Prevention:**

- Order Dockerfile layers by change frequency (least → most)
- Use BuildKit cache mounts
- Document layer optimization strategy
- Gate: Build time should not exceed baseline + 20%

---

## Extended Cases (Add-On)

### HC-DOCKER-023: Build Context Explosion

**Symptom:**

```
Sending build context to Docker daemon 1.5GB
docker build ... takes several minutes before first step
```

**Likely Causes:**

- `.dockerignore` missing or incomplete
- Monorepo root used as context with unnecessary assets

**Fast Diagnosis:**

```bash
du -sh .
cat .dockerignore
docker build --no-cache . | head -n 5
```

**Fix Steps:**

1. Add `.dockerignore` covering .git, node_modules, venv, test artifacts, tmp.
2. Build from subdirectory if service lives under packages/<svc>.
3. Use `docker build -f path/to/Dockerfile path/to/context`.

**Prevention:**

- CI gate to reject build contexts > target size (e.g., >200MB).
- Document per-service context path.

---

### HC-DOCKER-024: BuildKit Secret Mount Not Working

**Symptom:**

```
mount type=secret not allowed: secrets not enabled
```

**Likely Causes:**

- DOCKER_BUILDKIT disabled
- daemon.json not permitting secrets

**Fast Diagnosis:**

```bash
echo $DOCKER_BUILDKIT
cat /etc/docker/daemon.json 2>/dev/null | grep buildkit
```

**Fix Steps:**

1. Enable BuildKit: `export DOCKER_BUILDKIT=1` and daemon config `"features": {"buildkit": true}` then restart daemon.
2. Invoke build with `--secret id=...` and ensure file exists.

**Prevention:**

- Standardize BuildKit enabled in CI and dev.
- Document secret mount usage; avoid ARG for secrets.

---

### HC-DOCKER-025: Rootless Docker Volume Permissions

**Symptom:**

```
operation not permitted on bind mount with rootless daemon
```

**Likely Causes:**

- Rootless engine cannot write to privileged host paths
- UID/GID mismatch on host mount

**Fast Diagnosis:**

```bash
id
stat -c "%u:%g" /host/path
ps -ef | grep dockerd-rootless
```

**Fix Steps:**

1. Use user-writable paths for bind mounts or adjust ownership (`chown -R $(id -u):$(id -g)`).
2. Prefer named volumes when running rootless.
3. For dev, switch to rootful daemon if mount constraints block workflow.

**Prevention:**

- Document rootless limitations; use consistent UID/GID strategy.
- CI runs in rootful containerized runner when mounts required.

---

### HC-DOCKER-026: Overlay/Inode Exhaustion

**Symptom:**

```
no space left on device (inode exhaustion)
ENOSPC during build
```

**Likely Causes:**

- Too many small files in build cache
- Overlay2 inode limit reached

**Fast Diagnosis:**

```bash
df -i
docker system df -v
```

**Fix Steps:**

1. Prune aggressively: `docker system prune -af --volumes`.
2. Relocate Docker data-root to larger filesystem.
3. Reduce generated files in build context.

**Prevention:**

- Scheduled cache pruning in CI/hosts.
- Limit build artifacts and exclude with .dockerignore.

---

### HC-DOCKER-027: Healthcheck Binary Missing

**Symptom:**

```
OCI runtime exec failed: exec: "curl": executable file not found
```

**Likely Causes:**

- Healthcheck uses curl/wget not installed (especially on distroless/alpine)

**Fast Diagnosis:**

```bash
docker inspect <image> | jq '.[0].Config.Healthcheck'
docker run --rm <image> which curl wget || true
```

**Fix Steps:**

1. Install lightweight client (busybox wget) or use native health command (e.g., `CMD ["CMD-SHELL","[ -f /tmp/ready ]"]`).
2. For distroless, move healthcheck to sidecar or orchestrator probe.

**Prevention:**

- Keep healthcheck dependencies in final image or use exec form without extra tools.
- Validate healthcheck in CI.

---

### HC-DOCKER-028: Host DNS Overrides Container Resolution

**Symptom:**

```
Container resolves service to host /etc/hosts entries causing wrong target
```

**Likely Causes:**

- Host /etc/hosts mounted or custom DNS options overriding compose network DNS

**Fast Diagnosis:**

```bash
docker exec <ctr> cat /etc/resolv.conf
docker exec <ctr> cat /etc/hosts | head
```

**Fix Steps:**

1. Remove custom `--dns` unless required; rely on Docker embedded DNS.
2. Avoid mounting host /etc/hosts; use compose network aliases instead.

**Prevention:**

- Keep DNS config minimal; document required overrides.

---

### HC-DOCKER-029: Compose Variable Substitution Missing

**Symptom:**

```
services.app.environment contains ${VAR} literally at runtime
```

**Likely Causes:**

- env var not exported; .env not loaded; using compose v2 with wrong env file path

**Fast Diagnosis:**

```bash
cat .env || true
docker compose config | grep VAR
```

**Fix Steps:**

1. Ensure .env exists in compose project root; export needed vars.
2. Pass `--env-file` explicitly if not default.
3. Use `${VAR:-default}` to avoid empty values.

**Prevention:**

- Add preflight `docker compose config` in CI to catch unresolved variables.

---

### HC-DOCKER-030: Image Push Architecture Mix-Up

**Symptom:**

```
remote registry rejects manifest list or pulls wrong arch on server
```

**Likely Causes:**

- buildx not pushing multi-arch manifest; tags overwritten by single-arch build

**Fast Diagnosis:**

```bash
docker buildx imagetools inspect <image:tag>
```

**Fix Steps:**

1. Use `docker buildx build --platform=linux/amd64,linux/arm64 --push -t <image>`.
2. Avoid overwriting multi-arch tags with single-arch rebuilds; use arch-specific tags if needed.

**Prevention:**

- Enforce multi-arch pipeline for shared tags; protect tags from being overwritten by local builds.

---

## Issue-Key Format and Prompt Mapping

- All Docker hard cases use the format: `HC-DOCKER-XXX` and incident records should include `Issue-Key: DOCKER-<hash>` (example: `Issue-Key: DOCKER-12af9c`).
- Prompt: `prompts/hard_cases/docker_hard_cases.txt`
- Recovery Playbook: `agent/16_recovery_playbooks/docker_recovery.md`
- Caveats: `agent/17_caveats/docker_caveats.md`
- Diagnostics: `agent/18_diagnostics/docker_diagnostics.md`
