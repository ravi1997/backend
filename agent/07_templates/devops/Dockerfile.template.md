# Template: Dockerfile

## Purpose

This template provides a parameterized Dockerfile structure that can be adapted for different technology stacks.

## Parameters

- `{{BASE_IMAGE}}`: Base Docker image (e.g., `python:3.11-slim`, `node:20-alpine`)
- `{{WORKDIR}}`: Working directory in container (typically `/app`)
- `{{PACKAGE_FILES}}`: Dependency files to copy first (e.g., `requirements.txt`, `package.json`)
- `{{INSTALL_CMD}}`: Command to install dependencies (e.g., `pip install -r requirements.txt`, `npm ci`)
- `{{APP_USER}}`: Non-root user name (e.g., `appuser`, `node`)
- `{{APP_PORT}}`: Port to expose (e.g., `8000`, `3000`)
- `{{HEALTH_CHECK}}`: Health check command (optional)
- `{{START_CMD}}`: Command to start application

## Template

```dockerfile
# Multi-stage build for optimized image size
FROM {{BASE_IMAGE}} AS builder

# Set working directory
WORKDIR {{WORKDIR}}

# Copy dependency files first for better layer caching
COPY {{PACKAGE_FILES}} .

# Install dependencies
RUN {{INSTALL_CMD}}

# Copy application code
COPY . .

# Optional: Build step for compiled applications
# RUN {{BUILD_CMD}}

# Runtime stage
FROM {{BASE_IMAGE}}

# Create non-root user
RUN {{CREATE_USER_CMD}}

# Set working directory
WORKDIR {{WORKDIR}}

# Copy dependencies and application from builder
COPY --from=builder --chown={{APP_USER}}:{{APP_USER}} {{WORKDIR}} {{WORKDIR}}

# Expose application port
EXPOSE {{APP_PORT}}

# Add healthcheck (optional but recommended)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD {{HEALTH_CHECK}}

# Switch to non-root user
USER {{APP_USER}}

# Start application
CMD {{START_CMD}}
```

## Example: Python FastAPI

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.11-slim

RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /app /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Example: Node.js Express

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production

COPY . .

FROM node:20-alpine

RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /app /app

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

USER appuser

CMD ["node", "index.js"]
```

## Example: Next.js (Standalone)

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM node:20-alpine

RUN addgroup -g 1000 nodejs && \
    adduser -D -u 1000 -G nodejs nodejs

WORKDIR /app

COPY --from=builder --chown=nodejs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nodejs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nodejs:nodejs /app/public ./public

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

USER nodejs

CMD ["node", "server.js"]
```

## Notes

- Always use multi-stage builds to minimize final image size
- Pin base image versions for reproducibility
- Copy dependency files before source code for better caching
- Run as non-root user for security
- Include healthcheck for production deployments
- Use `.dockerignore` to exclude unnecessary files

## Related Files

- `agent/11_rules/docker_rules.md`
- `agent/06_skills/devops/skill_docker_baseline.md`
- `agent/05_gates/global/gate_global_docker.md`
