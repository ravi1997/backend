# Standard Developer Base Images

This registry defines the approved base images for each technology stack to ensure consistency, security, and performance across all generated projects.

## Stack-Specific Base Images

> **Optimization Tip:** See [`SHARED_CACHES.md`](./SHARED_CACHES.md) to set up shared package caches (bind mounts) across projects.

### Python

- **Production (`slim`)**: `python:3.11-slim-bookworm`
  - *Use for:* Deployment, final Docker images. Small size, secure.
- **Development (`dev`)**: `python:3.11-bookworm`
  - *Use for:* Dev containers, CI pipelines. Includes build tools (gcc, make).

### Node.js / Web

- **Production (`alpine`)**: `node:20-alpine`
  - *Use for:* Final production builds. Extremely small.
- **Development (`dev`)**: `node:20-bookworm`
  - *Use for:* Dev environments. Better compatibility with native modules (gyp).

### Java

- **Runtime (JRE)**: `eclipse-temurin:17-jre-alpine`
  - *Use for:* Running JARs in production.
- **Build (JDK)**: `maven:3.9-eclipse-temurin-17` or `gradle:8.5-jdk17`
  - *Use for:* Compilation stages.

### Go (Golang)

- **Build**: `golang:1.22-alpine`
  - *Use for:* Compilation.
- **Runtime**: `gcr.io/distroless/static-debian12` or `scratch`
  - *Use for:* Final binary execution. Zero overhead.

### C++

- **Build/Run**: `ubuntu:22.04`
  - *Use for:* General C++ development. Use `ubuntu:22.04-slim` for runtime if possible.
- **Alpine C++**: `alpine:3.19` (with `build-base`)
  - *Use for:* Truly static binaries (requires musl libc care).

### Flutter

- **Build**: `ghcr.io/cirruslabs/flutter:stable`
  - *Use for:* CI/CD, building web/apk artifacts.

---

## Service Base Images

### Databases

- **PostgreSQL**: `postgres:16-alpine`
- **Redis**: `redis:7-alpine`
- **MongoDB**: `mongo:7.0-jammy` (Avoid alpine for Mongo in prod usually, jammy is safer)

### Web Servers

- **Nginx**: `nginx:1.25-alpine`
- **Apache**: `httpd:2.4-alpine`
