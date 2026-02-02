# Docker Recovery Playbook

## Purpose

Step-by-step recovery procedures for Docker failures. Each playbook maps to hard cases and provides fast resolution paths.

---

## RECOVERY-DOCKER-001: Build Failure Recovery

### When to Use

- Build fails with context, dependency, or compilation errors
- Maps to: HC-DOCKER-001, HC-DOCKER-002, HC-DOCKER-004, HC-DOCKER-005

### Recovery Steps

**Step 1: Capture Build Output**

```bash
docker build . 2>&1 | tee build-failure.log
```

**Step 2: Identify Failure Stage**

```bash
grep -i "error\|failed" build-failure.log
```

**Step 3: Quick Fixes by Error Pattern**

**Pattern: "no such file or directory"**

```bash
# Verify build context
ls -la Dockerfile
cat .dockerignore
# Fix: Ensure Dockerfile in context, check .dockerignore
```

**Pattern: "COPY failed"**

```bash
# Test source stage
docker build --target=<stage-name> -t debug .
docker run --rm debug ls -la /expected/path
# Fix: Verify artifact paths match
```

**Pattern: "gyp ERR! build error"**

```bash
# Add build tools
# In Dockerfile, before npm install:
RUN apt-get update && apt-get install -y python3 make g++
```

**Pattern: "Failed building wheel"**

```bash
# Install Python dev dependencies
RUN apt-get update && apt-get install -y \
    build-essential libssl-dev libffi-dev python3-dev
RUN pip install --upgrade pip setuptools wheel
```

**Step 4: Rebuild with Verbose Output**

```bash
DOCKER_BUILDKIT=0 docker build --progress=plain --no-cache .
```

**Step 5: Validate Fix**

```bash
docker build -t test-build .
docker run --rm test-build sh -c "echo 'Build successful'"
```

---

## RECOVERY-DOCKER-002: Container Won't Start

### When to Use

- Container exits immediately or crashes on startup
- Maps to: HC-DOCKER-006, HC-DOCKER-007, HC-DOCKER-009

### Recovery Steps

**Step 1: Check Container Logs**

```bash
docker ps -a  # Find container ID
docker logs <container-id>
docker logs --tail 100 <container-id>
```

**Step 2: Inspect Container State**

```bash
docker inspect <container-id> | jq '.[0].State'
docker inspect <container-id> | jq '.[0].Config.Cmd'
```

**Step 3: Interactive Debug Session**

```bash
# Override entrypoint to get shell
docker run -it --entrypoint sh <image>

# Inside container, test manually:
ls -la /app
id
env
# Try running the actual command manually
```

**Step 4: Common Fixes**

**Fix: Permission Issues**

```bash
# Check file ownership
docker run --rm <image> ls -la /app

# In Dockerfile, add:
COPY --chown=node:node . /app
# Or create user with specific UID:
RUN useradd -u 1000 -m appuser && chown -R appuser:appuser /app
USER appuser
```

**Fix: Missing Environment Variables**

```bash
# Check what's set
docker run --rm <image> env

# Add to docker-compose.yml:
environment:
  - NODE_ENV=production
  - DATABASE_URL=${DATABASE_URL}
```

**Fix: Process Exits Too Quickly**

```dockerfile
# Ensure CMD runs long-lived process
CMD ["node", "server.js"]  # Good
# NOT: CMD ["npm", "start"]  # Can exit unexpectedly
```

**Step 5: Validate Fix**

```bash
docker run -d --name test <image>
sleep 5
docker ps | grep test  # Should be running
docker logs test
```

---

## RECOVERY-DOCKER-003: Network Connectivity Issues

### When to Use

- Services can't communicate
- DNS resolution failures
- Connection refused errors
- Maps to: HC-DOCKER-011, HC-DOCKER-012, HC-DOCKER-013

### Recovery Steps

**Step 1: Verify Network Topology**

```bash
docker network ls
docker network inspect <network-name>
docker-compose ps
```

**Step 2: Test DNS Resolution**

```bash
# From one service, test resolving another
docker exec <container> nslookup <service-name>
docker exec <container> ping <service-name>
docker exec <container> curl http://<service-name>:<port>
```

**Step 3: Check Network Attachment**

```bash
docker inspect <container> | jq '.[0].NetworkSettings.Networks'
```

**Step 4: Common Fixes**

**Fix: Services Not on Same Network**

```yaml
# docker-compose.yml
networks:
  app-network:

services:
  api:
    networks:
      - app-network
  db:
    networks:
      - app-network
```

**Fix: Using Default Bridge (No DNS)**

```bash
# Create user-defined network
docker network create app-network
docker run --network app-network --name api <image>
docker run --network app-network --name db <image>
```

**Fix: Connecting to Host Service**

```yaml
# docker-compose.yml
extra_hosts:
  - "host.docker.internal:host-gateway"

# In app, use: host.docker.internal:5432
```

**Step 5: Validate Connectivity**

```bash
docker exec <container-a> curl http://<container-b>:<port>/health
docker exec <container-a> nc -zv <container-b> <port>
```

---

## RECOVERY-DOCKER-004: Volume and Permission Problems

### When to Use

- Permission denied errors
- Files not persisting
- Bind mounts overriding dependencies
- Maps to: HC-DOCKER-007, HC-DOCKER-008, HC-DOCKER-017

### Recovery Steps

**Step 1: Identify Permission Issue**

```bash
docker exec <container> id
docker exec <container> ls -la /app
ls -la <host-mount-path>
```

**Step 2: Check Volume Configuration**

```bash
docker inspect <container> | jq '.[0].Mounts'
docker volume ls
docker volume inspect <volume-name>
```

**Step 3: Common Fixes**

**Fix: Bind Mount Overriding Dependencies**

```yaml
# docker-compose.yml
volumes:
  - .:/app
  - /app/node_modules  # Anonymous volume preserves node_modules
  - /app/venv          # For Python
```

**Fix: Permission Mismatch**

```yaml
# Option 1: Run as host user
user: "${UID}:${GID}"

# Option 2: Fix in entrypoint
# entrypoint.sh:
#!/bin/sh
chown -R $(id -u):$(id -g) /app/data
exec "$@"
```

**Fix: Wrong Ownership in Image**

```dockerfile
# Set ownership when copying
COPY --chown=node:node . /app

# Or after copying
COPY . /app
RUN chown -R node:node /app
USER node
```

**Step 4: Validate Fix**

```bash
docker exec <container> touch /app/test.txt
ls -la <host-mount-path>/test.txt  # Check ownership
docker exec <container> cat /app/node_modules/express/package.json  # Verify not overridden
```

---

## RECOVERY-DOCKER-005: Compose Service Dependencies

### When to Use

- Application starts before dependencies ready
- Race conditions on startup
- Maps to: HC-DOCKER-015

### Recovery Steps

**Step 1: Add Healthchecks**

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
  
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

**Step 2: Use Conditional Dependencies**

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
```

**Step 3: Implement Retry Logic in App**

```javascript
// Node.js example
const connectWithRetry = async (maxRetries = 10) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await db.connect();
      console.log('Database connected');
      return;
    } catch (err) {
      console.log(`Retry ${i + 1}/${maxRetries}...`);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  throw new Error('Failed to connect after retries');
};
```

**Step 4: Alternative - Use Wait Script**

```dockerfile
# Install wait-for-it
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# In docker-compose.yml:
command: ["wait-for-it", "db:5432", "--", "node", "server.js"]
```

**Step 5: Validate Startup Order**

```bash
docker-compose up -d
docker-compose logs -f
# Verify db/redis healthy before app starts
docker-compose ps  # Check health status
```

---

## RECOVERY-DOCKER-006: Image Size Optimization

### When to Use

- Image size too large (>500MB for typical apps)
- Slow deployments
- Maps to: HC-DOCKER-021, HC-DOCKER-022

### Recovery Steps

**Step 1: Analyze Current Image**

```bash
docker images | grep <image>
docker history <image>
dive <image>  # Install: https://github.com/wagoodman/dive
```

**Step 2: Identify Large Layers**

```bash
docker history <image> --no-trunc --format "{{.Size}}\t{{.CreatedBy}}" | sort -h
```

**Step 3: Optimization Strategies**

**Strategy 1: Use Smaller Base Image**

```dockerfile
# Before: FROM node:20 (900MB)
# After:
FROM node:20-alpine  # ~100MB

# Before: FROM python:3.11 (1GB)
# After:
FROM python:3.11-slim  # ~150MB
```

**Strategy 2: Multi-Stage Build**

```dockerfile
# Build stage
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
CMD ["node", "dist/server.js"]
```

**Strategy 3: Clean Up in Same Layer**

```dockerfile
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*  # Clean in same RUN
```

**Strategy 4: Optimize .dockerignore**

```
# .dockerignore
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.vscode
coverage
.DS_Store
```

**Step 4: Rebuild and Compare**

```bash
docker build -t <image>:optimized .
docker images | grep <image>
# Compare sizes
```

**Step 5: Validate Functionality**

```bash
docker run --rm <image>:optimized sh -c "node --version && ls -la"
# Run full test suite
docker run --rm <image>:optimized npm test
```

---

## RECOVERY-DOCKER-007: Security Vulnerabilities

### When to Use

- Security scan failures
- Known CVEs in image
- Secrets leaked in layers
- Maps to: HC-DOCKER-018, HC-DOCKER-019, HC-DOCKER-020

### Recovery Steps

**Step 1: Scan for Vulnerabilities**

```bash
# Using Docker scan
docker scan <image>

# Using Trivy
trivy image --severity HIGH,CRITICAL <image>

# Using Grype
grype <image>
```

**Step 2: Identify Issues**

```bash
trivy image --severity HIGH,CRITICAL --format json <image> > scan-results.json
cat scan-results.json | jq '.Results[].Vulnerabilities[] | {pkg: .PkgName, vuln: .VulnerabilityID, severity: .Severity}'
```

**Step 3: Common Fixes**

**Fix: Update Base Image**

```dockerfile
# Check for newer version
# Before: FROM node:20.9.0-alpine
# After:
FROM node:20.11.0-alpine  # Latest patch version
```

**Fix: Remove Secrets from Layers**

```dockerfile
# Bad: Secrets in ARG
ARG API_KEY=secret123
RUN curl -H "Authorization: $API_KEY" ...

# Good: Use BuildKit secrets
# syntax=docker/dockerfile:1
RUN --mount=type=secret,id=api_key \
    curl -H "Authorization: $(cat /run/secrets/api_key)" ...

# Build with:
docker build --secret id=api_key,src=.secrets/api_key .
```

**Fix: Pin Versions, Avoid :latest**

```dockerfile
# Before:
FROM node:latest

# After:
FROM node:20.11.0-alpine3.19
# Or with digest for immutability:
FROM node:20.11.0-alpine3.19@sha256:abc123...
```

**Step 4: Rebuild and Rescan**

```bash
docker build -t <image>:secure .
trivy image --severity HIGH,CRITICAL <image>:secure
# Should show reduced/zero HIGH/CRITICAL vulnerabilities
```

**Step 5: Generate SBOM**

```bash
syft <image>:secure -o spdx-json > sbom.json
# Store SBOM for compliance
```

---

## RECOVERY-DOCKER-008: Build Cache Issues

### When to Use

- Builds are slow
- Cache not being utilized
- Unnecessary rebuilds
- Maps to: HC-DOCKER-022

### Recovery Steps

**Step 1: Analyze Cache Usage**

```bash
docker build --progress=plain . 2>&1 | grep -E "CACHED|RUN"
```

**Step 2: Optimize Layer Order**

```dockerfile
# Principle: Order by change frequency (least → most)

# Good:
FROM node:20-alpine
WORKDIR /app

# 1. Copy dependency files (changes rarely)
COPY package*.json ./

# 2. Install dependencies (cached unless package.json changes)
RUN npm ci

# 3. Copy source code (changes frequently)
COPY . .

# 4. Build (only runs if source changed)
RUN npm run build

# Bad:
# COPY . .  # Invalidates cache on any file change
# RUN npm ci  # Reinstalls every time
```

**Step 3: Use BuildKit Cache Mounts**

```dockerfile
# syntax=docker/dockerfile:1

# Cache npm packages
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Cache pip packages
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Cache apt packages
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y curl
```

**Step 4: Enable BuildKit**

```bash
export DOCKER_BUILDKIT=1
docker build .

# Or in docker-compose.yml:
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build
```

**Step 5: Validate Improvement**

```bash
# First build (cold cache)
time docker build --no-cache -t test .

# Second build (warm cache)
time docker build -t test .

# Should be significantly faster
```

---

## Quick Reference: Error → Recovery Mapping

| Error Pattern | Recovery Playbook | Hard Case |
|--------------|-------------------|-----------|
| `no such file or directory` | RECOVERY-DOCKER-001 | HC-DOCKER-001 |
| `COPY failed` | RECOVERY-DOCKER-001 | HC-DOCKER-002 |
| `gyp ERR!` | RECOVERY-DOCKER-001 | HC-DOCKER-004 |
| `Failed building wheel` | RECOVERY-DOCKER-001 | HC-DOCKER-005 |
| `EXITED (0)` | RECOVERY-DOCKER-002 | HC-DOCKER-006 |
| `permission denied` | RECOVERY-DOCKER-004 | HC-DOCKER-007 |
| `Cannot find module` | RECOVERY-DOCKER-004 | HC-DOCKER-008 |
| `unhealthy` | RECOVERY-DOCKER-002 | HC-DOCKER-009 |
| `port is already allocated` | RECOVERY-DOCKER-002 | HC-DOCKER-010 |
| `ENOTFOUND` | RECOVERY-DOCKER-003 | HC-DOCKER-011 |
| `Connection refused` | RECOVERY-DOCKER-003 | HC-DOCKER-012, 013 |
| `502 Bad Gateway` | RECOVERY-DOCKER-003 | HC-DOCKER-014 |
| `depends_on` issues | RECOVERY-DOCKER-005 | HC-DOCKER-015 |
| Large image size | RECOVERY-DOCKER-006 | HC-DOCKER-021 |
| Slow builds | RECOVERY-DOCKER-008 | HC-DOCKER-022 |
| Security vulnerabilities | RECOVERY-DOCKER-007 | HC-DOCKER-018, 019, 020 |

---

## Extended Cases (Add-On)

### RECOVERY-DOCKER-009: Build Context / BuildKit / Multi-Arch
- Trim context: audit `.dockerignore`, move Dockerfile closer to app, or set correct build context; target context size <200MB.
- Ensure BuildKit enabled (`DOCKER_BUILDKIT=1`, daemon feature flag) before using secret mounts or cache mounts.
- For multi-arch pushes, inspect with `docker buildx imagetools inspect <image:tag>`; rebuild with `--platform=linux/amd64,linux/arm64 --push` and avoid overwriting manifest lists with single-arch rebuilds.

### RECOVERY-DOCKER-010: Rootless/Permissions and Filesystem Exhaustion
- Rootless bind mount issues: use user-writable host paths or named volumes; align UID/GID; switch to rootful daemon only if unavoidable.
- Inode/disk exhaustion: `df -i`, `docker system df -v`; prune (`docker system prune -af --volumes`) and relocate Docker data-root if needed.

### RECOVERY-DOCKER-011: Compose Substitution and Healthcheck Tooling
- Run `docker compose config` to ensure env substitution; provide `--env-file` or defaults via `${VAR:-default}`; fail CI if unresolved.
- If healthcheck commands rely on missing tools (curl/wget), install minimal dependencies or move probe to orchestrator; validate with `docker inspect ...Healthcheck`.

## Related Files

- Hard Cases: `agent/15_tech_hard_cases/docker.md`
- Caveats: `agent/17_caveats/docker_caveats.md`
- Diagnostics: `agent/18_diagnostics/docker_diagnostics.md`
