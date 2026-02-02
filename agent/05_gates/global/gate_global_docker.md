# Gate: Global Docker

**Type**: Global DevOps Gate  
**Purpose**: Ensure Docker implementation follows best practices and security standards

---

## Overview

This gate validates Docker configuration across all stacks. It ensures:

- Secure Dockerfile practices
- Optimized image builds
- Proper docker-compose setup
- Security hardening

---

## Checks

### 1. Dockerfile Best Practices

#### Security

- [ ] Non-root user configured (`USER` directive)
- [ ] No secrets in image layers
- [ ] Minimal base image (alpine, distroless, or slim)
- [ ] Specific version tags (not `latest`)
- [ ] Security scanning passed (Trivy, Snyk, or similar)

#### Optimization

- [ ] Multi-stage builds used (where applicable)
- [ ] Layer caching optimized (COPY package files before source)
- [ ] Minimal layers (combine RUN commands)
- [ ] .dockerignore file present
- [ ] Image size reasonable (< 500MB for apps, < 100MB for services)

#### Maintainability

- [ ] Clear comments for complex steps
- [ ] Health check defined (`HEALTHCHECK`)
- [ ] Proper ENTRYPOINT/CMD usage
- [ ] Build arguments for configuration (`ARG`)
- [ ] Labels for metadata (`LABEL`)

---

### 2. .dockerignore Configuration

Required entries:

```dockerignore
# Version control
.git
.gitignore

# Dependencies (will be installed in container)
node_modules
venv
__pycache__
*.pyc

# Build artifacts
dist
build
target
*.o
*.so

# IDE
.vscode
.idea
*.swp

# Environment
.env
.env.local
*.log

# Documentation
README.md
docs/
*.md

# Tests (unless needed in container)
tests/
*.test.js
*.spec.js
```

---

### 3. docker-compose.yml Best Practices

- [ ] Version specified (3.8+)
- [ ] Service names descriptive
- [ ] Environment variables from .env file
- [ ] Volumes for persistent data
- [ ] Networks defined for service isolation
- [ ] Health checks configured
- [ ] Resource limits set (memory, CPU)
- [ ] Restart policies defined
- [ ] Port mappings documented

**Example**:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: my-app
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    env_file:
      - .env
    ports:
      - "3000:3000"
    volumes:
      - ./data:/app/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

networks:
  app-network:
    driver: bridge
```

---

### 4. Security Hardening

#### Image Security

- [ ] Base image from trusted registry (Docker Hub official, gcr.io, etc.)
- [ ] No hardcoded secrets (use secrets management)
- [ ] Read-only root filesystem (where possible)
- [ ] Dropped unnecessary capabilities
- [ ] Security scanning in CI/CD

**Example Dockerfile Security**:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
WORKDIR /app
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs . .
USER nodejs
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js
CMD ["node", "server.js"]
```

#### Runtime Security

- [ ] Containers run as non-root
- [ ] No privileged mode (unless absolutely necessary)
- [ ] AppArmor/SELinux profiles applied
- [ ] Secrets via Docker secrets or env vars (not in image)

---

### 5. Stack-Specific Dockerfile Requirements

#### Node.js / Next.js

- [ ] Multi-stage build (dependencies → build → production)
- [ ] `npm ci` instead of `npm install`
- [ ] `NODE_ENV=production`
- [ ] Only production dependencies in final image

#### Python / Flask / FastAPI

- [ ] Virtual environment or pip install to user directory
- [ ] `requirements.txt` copied before source code
- [ ] `PYTHONUNBUFFERED=1` set
- [ ] Gunicorn or uWSGI for production

#### Java / Spring

- [ ] Multi-stage build (Maven/Gradle build → runtime)
- [ ] JRE instead of JDK in final image
- [ ] JAR/WAR copied from builder stage
- [ ] JVM memory settings configured

#### C/C++

- [ ] Multi-stage build (compile → runtime)
- [ ] Only runtime libraries in final image
- [ ] Compiled binaries from builder stage
- [ ] Minimal base image (alpine, distroless)

#### Flutter

- [ ] Web build artifacts only in final image
- [ ] Nginx or similar for serving
- [ ] Multi-stage build

---

### 6. Build & Test

- [ ] `docker build` succeeds without errors
- [ ] `docker build` completes in reasonable time (< 10 min)
- [ ] Image runs successfully (`docker run`)
- [ ] Health check passes
- [ ] No vulnerabilities in security scan

---

## Commands

### Build Image

```bash
docker build -t myapp:latest .
```

### Run Container

```bash
docker run -d -p 3000:3000 --name myapp myapp:latest
```

### Security Scan

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image myapp:latest
```

### Check Image Size

```bash
docker images myapp:latest
```

### Inspect Layers

```bash
docker history myapp:latest
```

### Test docker-compose

```bash
docker-compose up -d
docker-compose ps
docker-compose logs
docker-compose down
```

---

## Pass Criteria

✅ **PASS** if:

- Dockerfile follows best practices
- Non-root user configured
- Multi-stage build used (where applicable)
- .dockerignore present and complete
- docker-compose.yml valid and complete
- Security scan shows no HIGH/CRITICAL vulnerabilities
- Image size reasonable
- Health check defined and passing

❌ **FAIL** if:

- Running as root in production
- Secrets in image layers
- Using `latest` tag for base images
- No .dockerignore
- Security scan shows HIGH/CRITICAL vulnerabilities
- Image size excessive (> 2GB without justification)
- Build fails

---

## Exceptions

- **Root user**: Allowed only if documented and justified
- **Image size**: Large images allowed if necessary (ML models, etc.)
- **Latest tag**: Allowed in development, never in production

---

## Docker Checklist

```markdown
## Docker Implementation Checklist

### Dockerfile
- [ ] Multi-stage build (if applicable)
- [ ] Non-root user (USER directive)
- [ ] Specific version tags (no :latest)
- [ ] Health check defined
- [ ] Minimal base image
- [ ] Layer caching optimized
- [ ] No secrets in layers

### .dockerignore
- [ ] File exists
- [ ] Excludes .git, node_modules, venv
- [ ] Excludes build artifacts
- [ ] Excludes .env files

### docker-compose.yml
- [ ] Version 3.8+
- [ ] Environment variables from .env
- [ ] Volumes for persistent data
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Restart policies defined

### Security
- [ ] Security scan passed
- [ ] No HIGH/CRITICAL vulnerabilities
- [ ] Non-root user
- [ ] No hardcoded secrets

### Testing
- [ ] docker build succeeds
- [ ] docker run succeeds
- [ ] Health check passes
- [ ] Image size reasonable
```

---

## Tools

- **Trivy**: Container security scanning
- **Hadolint**: Dockerfile linter
- **Dive**: Analyze image layers
- **Docker Bench**: Security best practices checker

---

## Related Files

- `agent/07_templates/docker/` (Dockerfile templates per stack)
- `agent/13_examples/example_docker_setup.md`
- `agent/06_skills/skill_dockerize.md`
- Stack-specific gates (for stack-specific Docker requirements)

---

## References

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
