---
description: Setup Docker for a project using standard templates
---

# Workflow: Docker Setup

This workflow guides the process of containerizing an application using the standard snippets provided in this pack.

## 1. Context Analysis

- [ ] Identify the primary language/framework (Python, Node, Go, etc.).
- [ ] Identify the entrypoint (e.g., `app.py`, `index.js`, `main.go`).
- [ ] Check for existing `Dockerfile` or `docker-compose.yml`.

## 2. Snippet Selection

- Use the `view_file` tool to read the appropriate snippet from `agent/snippets/`:
  - Python: `agent/snippets/Dockerfile.python.md`
  - Node.js: `agent/snippets/Dockerfile.node.md`
  - Go: `agent/snippets/Dockerfile.go.md`

## 3. Implementation

- [ ] Create `.dockerignore` using content from `agent/snippets/dockerignore.md`.
- [ ] Create `Dockerfile` from the selected snippet.
  - **Customize**: Update specific version numbers (e.g., `python:3.9` vs `python:3.11`).
  - **Customize**: Update the `CMD` or `ENTRYPOINT` to match the project's start command.
  - **Customize**: Ensure all system dependencies are installed in the build stage.

## 4. Verification

// turbo

- Run `docker build -t test-build .` to verify the build process.
- If the build fails:
  - Consult `agent/checklists/DOCKER_BUILD_FAIL_EVIDENCE.md`.
  - Fix errors and retry.
- Run the container locally to verify runtime:
  - `docker run --rm -p <host_port>:<container_port> test-build`
  - Check if the application responds.

## 5. Composition (Optional)

- If a database or other services are needed, create a `docker-compose.yml`.
- Refer to `agent/snippets/docker-compose.flask+nginx.md` for structure, or generic compose skills.
- Ensure strict version pinning for services (e.g., `postgres:15-alpine` not `postgres:latest`).

## 6. Final Review

- Check against `agent/gates/DOCKER_GATE.md` to ensure compliance.
