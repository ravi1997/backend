# Docker Caveats & Footguns

## Purpose

Critical Docker pitfalls, anti-patterns, and gotchas that cause production issues. These are the "things you wish you knew before."

---

## CAVEAT-DOCKER-001: The :latest Tag Trap

### The Problem

Using `:latest` tag gives you **unpredictable, non-reproducible builds**.

### Why It's Dangerous

- `latest` doesn't mean "newest" — it's just a default tag
- Upstream can push breaking changes to `latest` anytime
- Different machines may pull different versions
- No way to rollback or reproduce exact build

### The Footgun

```dockerfile
# This is a ticking time bomb:
FROM node:latest
FROM python:latest
FROM nginx:latest
```

### The Right Way

```dockerfile
# Pin to specific version:
FROM node:20.11.0-alpine3.19

# Even better - use digest for immutability:
FROM node:20.11.0-alpine3.19@sha256:c7d0f9c...

# Document why this version:
# Using Node 20.11.0 for async/await improvements
# Alpine 3.19 for security patches
FROM node:20.11.0-alpine3.19
```

### Detection

```bash
grep "FROM.*:latest" Dockerfile
```

### Enforcement

Add to CI:

```bash
if grep -q ":latest" Dockerfile; then
  echo "ERROR: :latest tag not allowed"
  exit 1
fi
```

---

## CAVEAT-DOCKER-002: The Layer Cache Invalidation Cascade

### The Problem

One wrong line order in Dockerfile = rebuild everything every time.

### Why It's Dangerous

- Wastes CI/CD time (10+ minutes per build)
- Increases costs (compute + bandwidth)
- Slows down development iteration

### The Footgun

```dockerfile
# BAD: Copy everything first
FROM node:20-alpine
WORKDIR /app
COPY . .              # ← Any file change invalidates cache
RUN npm ci            # ← Reinstalls EVERY TIME
RUN npm run build     # ← Rebuilds EVERY TIME
```

### The Right Way

```dockerfile
# GOOD: Copy by change frequency
FROM node:20-alpine
WORKDIR /app

# 1. Dependency files (rarely change)
COPY package*.json ./

# 2. Install (cached unless package.json changes)
RUN npm ci

# 3. Source code (changes frequently)
COPY . .

# 4. Build (only if source changed)
RUN npm run build
```

### The Rule

**Order Dockerfile instructions from least-frequently-changed to most-frequently-changed.**

### Advanced: BuildKit Cache Mounts

```dockerfile
# syntax=docker/dockerfile:1
RUN --mount=type=cache,target=/root/.npm \
    npm ci
```

---

## CAVEAT-DOCKER-003: The Bind Mount node_modules Disaster

### The Problem

Mounting source code overwrites `node_modules` installed in container.

### Why It's Dangerous

- App crashes with "Cannot find module"
- Works in production, fails in development
- Confusing for new developers

### The Footgun

```yaml
# docker-compose.yml
services:
  app:
    volumes:
      - .:/app  # ← Overwrites /app/node_modules in container!
```

### The Right Way

```yaml
# Option 1: Anonymous volume
services:
  app:
    volumes:
      - .:/app
      - /app/node_modules  # ← Preserves container's node_modules

# Option 2: Named volume
services:
  app:
    volumes:
      - .:/app
      - node_modules:/app/node_modules

volumes:
  node_modules:
```

### For Python (venv)

```yaml
volumes:
  - .:/app
  - /app/venv  # Preserve virtual environment
```

### For Java (Maven)

```yaml
volumes:
  - .:/app
  - /app/target  # Preserve build artifacts
```

---

## CAVEAT-DOCKER-004: The Default Bridge Network DNS Trap

### The Problem

Default bridge network has **no DNS resolution** between containers.

### Why It's Dangerous

- Services can't find each other by name
- Must use IP addresses (which change)
- Breaks service discovery

### The Footgun

```bash
# Using default bridge:
docker run --name api myapi
docker run --name db postgres

# In api container:
curl http://db:5432  # ← FAILS: "Could not resolve host: db"
```

### The Right Way

```bash
# Create user-defined network:
docker network create myapp-network

docker run --network myapp-network --name api myapi
docker run --network myapp-network --name db postgres

# Now DNS works:
curl http://db:5432  # ✓ Works!
```

### In docker-compose (automatic)

```yaml
# docker-compose automatically creates user-defined network
services:
  api:
    # Can reference other services by name
    environment:
      - DATABASE_URL=postgres://db:5432/mydb
  db:
    image: postgres
```

### The Rule

**Never use default bridge network for multi-container apps. Always use user-defined networks or docker-compose.**

---

## CAVEAT-DOCKER-005: The ARG vs ENV Secret Leak

### The Problem

`ARG` values are **baked into image layers** and visible to anyone with the image.

### Why It's Dangerous

- Secrets exposed in `docker history`
- Secrets in image registries
- Compliance violations

### The Footgun

```dockerfile
# DANGER: Secret is now in image forever!
ARG DATABASE_PASSWORD=supersecret
RUN echo "DB_PASS=$DATABASE_PASSWORD" > /app/.env
```

### The Right Way

```dockerfile
# Option 1: BuildKit secrets (best)
# syntax=docker/dockerfile:1
RUN --mount=type=secret,id=db_password \
    echo "DB_PASS=$(cat /run/secrets/db_password)" > /app/.env

# Build with:
# docker build --secret id=db_password,src=.secrets/db_password .

# Option 2: ENV at runtime (not build time)
# Don't put secrets in Dockerfile at all
# Pass via docker run:
# docker run -e DATABASE_PASSWORD=secret myapp

# Option 3: External secret management
# Use Docker secrets, Vault, AWS Secrets Manager, etc.
```

### Detection

```bash
# Check if secrets leaked:
docker history <image> --no-trunc
docker save <image> -o image.tar && tar -xf image.tar && grep -r "PASSWORD" .
```

### The Rule

**Never use ARG for secrets. Use BuildKit secrets, runtime ENV, or external secret managers.**

---

## CAVEAT-DOCKER-006: The depends_on Readiness Lie

### The Problem

`depends_on` only waits for container **start**, not **readiness**.

### Why It's Dangerous

- App tries to connect to DB before it's ready
- Crashes on startup
- Race conditions in CI/CD

### The Footgun

```yaml
services:
  app:
    depends_on:
      - db  # ← Only waits for container to START, not be READY
  db:
    image: postgres
```

### The Right Way

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy  # ← Wait for health check
  db:
    image: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
```

### Alternative: Retry Logic in App

```javascript
// Node.js example
const connectWithRetry = async (maxRetries = 10, delay = 2000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await db.connect();
      return;
    } catch (err) {
      if (i === maxRetries - 1) throw err;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
};
```

### The Rule

**Always add healthchecks to dependencies and use `condition: service_healthy`, or implement retry logic in your app.**

---

## CAVEAT-DOCKER-007: The Multi-Stage COPY Trap

### The Problem

Copying from wrong stage or non-existent path silently fails or errors.

### Why It's Dangerous

- Build succeeds but app is broken
- Missing files in production
- Hard to debug

### The Footgun

```dockerfile
FROM node:20 AS builder
WORKDIR /app
RUN npm run build  # Creates /app/dist

FROM node:20-alpine
COPY --from=builder /app/build ./build  # ← WRONG PATH! Should be /app/dist
```

### The Right Way

```dockerfile
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build  # Verify output path

FROM node:20-alpine
WORKDIR /app
# Copy from correct path:
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

# Verify files exist:
RUN ls -la dist/
```

### Validation

```bash
# Test intermediate stage:
docker build --target=builder -t test-builder .
docker run --rm test-builder ls -la /app/dist

# Ensure files exist before final stage
```

### The Rule

**Always verify paths in multi-stage builds. Test intermediate stages independently.**

---

## CAVEAT-DOCKER-008: The Alpine glibc Gotcha

### The Problem

Alpine Linux uses **musl libc**, not **glibc**. Many binaries expect glibc.

### Why It's Dangerous

- Native Node modules fail
- Python wheels fail
- Pre-compiled binaries crash

### The Footgun

```dockerfile
FROM node:20-alpine
# Install native module:
RUN npm install bcrypt  # ← May fail or crash at runtime
```

### The Right Way

```dockerfile
# Option 1: Install build tools for Alpine
FROM node:20-alpine
RUN apk add --no-cache python3 make g++
RUN npm install bcrypt  # Now compiles from source

# Option 2: Use Debian slim instead
FROM node:20-slim  # Uses glibc, more compatible
RUN npm install bcrypt  # Works out of box

# Option 3: Use pre-built Alpine-compatible packages
FROM node:20-alpine
RUN apk add --no-cache python3 make g++ && \
    npm install bcrypt && \
    apk del python3 make g++  # Remove build tools after
```

### When to Use Alpine

✅ **Use Alpine when:**

- Pure JavaScript/Python (no native deps)
- You control all dependencies
- Image size is critical

❌ **Avoid Alpine when:**

- Many native dependencies
- Using pre-compiled binaries
- Team unfamiliar with musl/glibc differences

---

## CAVEAT-DOCKER-009: The .dockerignore Oversight

### The Problem

Missing `.dockerignore` sends **entire directory** to Docker daemon, including `node_modules`, `.git`, etc.

### Why It's Dangerous

- Slow builds (sending GB of data)
- Secrets accidentally copied into image
- Cache invalidation from irrelevant files

### The Footgun

```bash
# Without .dockerignore:
Sending build context to Docker daemon  2.5GB  # ← HUGE!
```

### The Right Way

```
# .dockerignore
node_modules
npm-debug.log
.git
.gitignore
.env
.env.*
.vscode
.idea
coverage
*.md
!README.md
.DS_Store
dist
build
*.log
```

### For Python

```
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv
.venv
.pytest_cache
.mypy_cache
.coverage
htmlcov
```

### Validation

```bash
# Check build context size:
docker build --progress=plain . 2>&1 | grep "Sending build context"

# Should be <50MB for most apps
```

---

## CAVEAT-DOCKER-010: The Root User Security Risk

### The Problem

Running containers as **root** is a security vulnerability.

### Why It's Dangerous

- Container escape = root on host
- Privilege escalation attacks
- Compliance failures

### The Footgun

```dockerfile
FROM node:20
WORKDIR /app
COPY . .
RUN npm ci
CMD ["node", "server.js"]  # ← Runs as root!
```

### The Right Way

```dockerfile
FROM node:20
WORKDIR /app

# Copy with ownership
COPY --chown=node:node package*.json ./
RUN npm ci

COPY --chown=node:node . .

# Switch to non-root user
USER node

CMD ["node", "server.js"]  # ← Runs as 'node' user
```

### For Custom User

```dockerfile
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app
USER appuser

COPY --chown=appuser:appuser . .
RUN pip install --user -r requirements.txt

CMD ["python", "app.py"]
```

### Validation

```bash
docker run --rm <image> id
# Should show: uid=1000(node) gid=1000(node) NOT uid=0(root)
```

---

## CAVEAT-DOCKER-011: The Healthcheck Timeout Trap

### The Problem

Healthcheck timeout too short = false negatives. Too long = slow failure detection.

### Why It's Dangerous

- Container marked unhealthy when it's fine
- Or stays "healthy" when it's actually broken
- Orchestrators (K8s, Swarm) make wrong decisions

### The Footgun

```dockerfile
# Too aggressive:
HEALTHCHECK --interval=5s --timeout=1s --retries=2 \
  CMD curl -f http://localhost:3000/health
# ← App might take 2s to respond, marked unhealthy
```

### The Right Way

```dockerfile
# Balanced settings:
HEALTHCHECK \
  --interval=30s \      # Check every 30s
  --timeout=10s \       # Allow 10s for response
  --start-period=40s \  # Grace period for slow startup
  --retries=3 \         # Fail after 3 consecutive failures
  CMD curl -f http://localhost:3000/health || exit 1
```

### For Different App Types

```dockerfile
# Fast API (Node/Go):
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:3000/health

# Slow startup (Java/Spring):
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health

# Database:
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
  CMD pg_isready -U postgres
```

### The Rule

**Tune healthcheck parameters for your app's characteristics. Use `start-period` for slow-starting apps.**

---

## CAVEAT-DOCKER-012: The Build-Time vs Runtime Confusion

### The Problem

Mixing build-time (`ARG`) and runtime (`ENV`) variables incorrectly.

### Why It's Dangerous

- Configuration not available at runtime
- Secrets baked into image
- Can't change config without rebuild

### The Footgun

```dockerfile
# WRONG: Using ARG for runtime config
ARG NODE_ENV=production
ARG DATABASE_URL=postgres://...
CMD ["node", "server.js"]  # ← Can't access ARG at runtime!
```

### The Right Way

```dockerfile
# ARG: Only for build-time (e.g., base image version)
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-alpine

# ENV: For runtime configuration
ENV NODE_ENV=production
ENV PORT=3000

# Don't hardcode secrets - pass at runtime
# ENV DATABASE_URL=  # ← NO!

CMD ["node", "server.js"]

# Pass secrets at runtime:
# docker run -e DATABASE_URL=postgres://... myapp
```

### When to Use Each

| Use Case | Use |
|----------|-----|
| Base image version | `ARG` |
| Build flags | `ARG` |
| Runtime config | `ENV` |
| Secrets | Neither (runtime or BuildKit secrets) |
| Default values | `ENV` (can override at runtime) |

---

## CAVEAT-DOCKER-013: The Volume Persistence Surprise

### The Problem

Named volumes persist **even after `docker-compose down`**.

### Why It's Dangerous

- Stale data in development
- "Works on my machine" (different data)
- Migrations not applied

### The Footgun

```bash
docker-compose down
docker-compose up  # ← Database still has old data!
```

### The Right Way

```bash
# Remove volumes when needed:
docker-compose down -v  # ← Removes volumes

# Or remove specific volume:
docker volume rm myapp_postgres_data

# List volumes:
docker volume ls

# Inspect volume:
docker volume inspect myapp_postgres_data
```

### For Development

```yaml
# docker-compose.yml
services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data
      # For dev, consider bind mount for easy reset:
      # - ./dev-data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### The Rule

**Understand volume lifecycle. Use `docker-compose down -v` to clean state in development.**

---

## CAVEAT-DOCKER-014: The Platform Architecture Mismatch

### The Problem

Building on ARM (M1/M2 Mac) for AMD64 (production servers) without `--platform`.

### Why It's Dangerous

- Image works locally, crashes in production
- "exec format error"
- Subtle performance issues

### The Footgun

```dockerfile
# On M1 Mac:
FROM node:20-alpine  # ← Pulls ARM64 version
# Builds fine locally, crashes on AMD64 server
```

### The Right Way

```dockerfile
# Specify platform explicitly:
FROM --platform=linux/amd64 node:20-alpine

# Or build with flag:
# docker build --platform=linux/amd64 .
```

### For Multi-Platform

```bash
# Use buildx:
docker buildx create --use
docker buildx build --platform=linux/amd64,linux/arm64 -t myapp:latest .
```

### In CI/CD

```yaml
# GitHub Actions
- name: Build
  run: docker build --platform=linux/amd64 -t myapp .
```

### The Rule

**Always specify `--platform` when building for different architecture than host.**

---

## Golden Docker Patterns

### Pattern 1: The Optimal Dockerfile Structure

```dockerfile
# syntax=docker/dockerfile:1

# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

# Dependencies (cached layer)
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

# Source code
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# Copy artifacts
COPY --from=builder --chown=appuser:appuser /app/dist ./dist
COPY --from=builder --chown=appuser:appuser /app/node_modules ./node_modules
COPY --chown=appuser:appuser package*.json ./

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/server.js"]
```

### Pattern 2: The Optimal docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://postgres:password@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

### Pattern 3: The Optimal .dockerignore

```
# Dependencies
node_modules
npm-debug.log
yarn-error.log

# Build outputs
dist
build
coverage

# Environment
.env
.env.*
!.env.example

# VCS
.git
.gitignore
.gitattributes

# IDE
.vscode
.idea
*.swp
*.swo
.DS_Store

# Docs
*.md
!README.md
docs

# CI/CD
.github
.gitlab-ci.yml

# Testing
.pytest_cache
.coverage
htmlcov
__pycache__
*.pyc
```

## Additional Hard Cases (Add-On)

- Keep build contexts lean; enforce `.dockerignore` coverage and avoid sending monorepo roots when only a subdir is needed.
- BuildKit-dependent features (secrets/cache mounts) require `DOCKER_BUILDKIT=1` on dev and CI; fail early if disabled.
- Rootless Docker has mount limitations—prefer named volumes or user-writable bind mounts; align UID/GID across team.
- Healthchecks must rely on binaries present in the final image; for distroless, shift probes to orchestrator or add minimal tools.
- Compose variable substitution must resolve before deploy; `docker compose config` should be part of CI to catch `${VAR}` placeholders.
- Multi-arch tags should only be built/pushed via buildx; block single-arch local builds from overwriting shared tags.

## Related Files

- Hard Cases: `agent/15_tech_hard_cases/docker.md`
- Recovery: `agent/16_recovery_playbooks/docker_recovery.md`
- Diagnostics: `agent/18_diagnostics/docker_diagnostics.md`
