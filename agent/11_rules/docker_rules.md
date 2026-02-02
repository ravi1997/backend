# Rules: Docker & Containerization

**Stack**: Docker  
**Scope**: Dockerfile, docker-compose, Runtime

---

## 1. Dockerfile Standards

- **Tagging**: NEVER use `:latest` in production Dockerfiles or Compose. Pin version numbers (e.g., `node:18.17.0-alpine`).
- **User**: Container MUST NOT run as root. Create a user and switch to it with `USER`.
- **Base Images**: Use minimal images (Alpine, Slim, Distroless) where compatible to reduce attack surface.
- **Multi-Stage**: Use multi-stage builds to exclude build tools/artifacts from final runtime image.

## 2. Optimization

- **Layer Caching**: Order instructions from least changing to most changing.
  - 1. Install system dependencies
  - 1. Copy package lock files
  - 1. Install app dependencies
  - 1. Copy source code
- **Layer Count**: Combine `RUN` commands where logical to reduce layer count (e.g., `apt-get update && apt-get install && rm -rf ...`).
- **Clean Up**: Remove cache/temp files in the SAME RUN layer they were created.

## 3. Configuration & Secrets

- **Secrets**: NEVER bake secrets/keys into the image. Use `Secrets` mounts or Environment Variables at runtime.
- **Environment**: Use `.env` files for local dev variables.
- **Config**: Use `ENTRYPOINT` for the main executable and `CMD` for default args.

## 4. Docker Compose

- **Version**: Use modern Compose specification (version 3.8+).
- **Services**: Define clear service dependencies (`depends_on`).
- **Persistence**: Explicitly define volumes for persistent data.
- **Networking**: Use user-defined networks, not default bridge.

## 5. Security (Container)

- **Privileges**: Do NOT run containers with `--privileged`.
- **Capabilities**: Drop unnecessary Linux capabilities (`cap_drop`).
- **Read-Only**: Mount filesystem as read-only where possible.

---

## Enforcement Checklist

- [ ] No `latest` tags used
- [ ] Non-root `USER` defined in Dockerfile
- [ ] Multi-stage build pattern used
- [ ] No secrets in build layers
- [ ] .dockerignore file exists and is populated
