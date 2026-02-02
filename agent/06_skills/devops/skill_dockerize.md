# Skill: Dockerize Stack

**Role**: DevOps Engineer  
**Output**: `Dockerfile`, `docker-compose.yml`, `.dockerignore`  
**Complexity**: Medium

---

## Strategy

1. **Detect Stack**: Identify the primary language and framework.
2. **Select Template**: Use the appropriate stack template from `agent/07_templates/docker/`.
3. **Customize**: Adjust for specific entry points, ports, and dependencies.
4. **Optimize**: Ensure multi-stage builds and minimal base images.
5. **Orchestrate**: Create `docker-compose.yml` for local development.

---

## Stack-Specific Strategies

### Node.js / Next.js

- **Base**: `node:alpine` or `node:slim`.
- **Stages**: `deps` (ci) → `builder` (build) → `runner` (prod).
- **Optimization**: Copy `package*.json` first for caching.
- **Next.js config**: Ensure `standalone` output mode in Next.js.

### Python (Flask/FastAPI)

- **Base**: `python:slim` or `python:alpine` (careful with wheel support).
- **Stages**: `builder` (venv creation) → `runner` (copy venv).
- **Vars**: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`.

### Java (Spring Boot)

- **Base**: `eclipse-temurin:jre-alpine` (runtime), `maven` or `gradle` (builder).
- **Stages**: `builder` (mvn package) → `runner` (copy jar).
- **Optimization**: Use `mvn dependency:go-offline` to cache dependencies.

### C++

- **Base**: `alpine` or `distroless` (runtime) + build tools (builder).
- **Stages**: `builder` (cmake build) → `runner` (copy binary).
- **Libs**: Bundle dynamic libs or link statically.

### Flutter (Web)

- **Base**: `nginx:alpine` (runtime).
- **Stages**: `flutter` (build web) → `nginx` (serve /build/web).

---

## Step-by-Step Execution

1. **Read Request**: user asks to "dockerize" or "add docker".
2. **Scan**: Check for `package.json`, `requirements.txt`, etc.
3. **Generate Dockerfile**:
   - Load template.
   - Replace placeholders (`{{PORT}}`, `{{ENTRY_CMD}}`).
   - Write to `Dockerfile`.
4. **Generate .dockerignore**:
   - Write standard excludes (`node_modules`, `venv`, `.git`).
5. **Generate docker-compose.yml**:
   - Define service.
   - Map ports.
   - Map volume for hot-reload (dev mode).
6. **Verify**:
   - Run `docker build .` (dry run if possible).

---

## Outputs

- `Dockerfile` (optimized, multi-stage, secure)
- `.dockerignore` (comprehensive)
- `docker-compose.yml` (local dev ready)

---

## Security Defaults

- **User**: Create non-root user.
- **Secrets**: Do not COPY `.env`.

---

## Example Prompt Usage

"Dockerize this Next.js app."
-> Detected Next.js.
-> Writing Dockerfile (node:alpine, multi-stage).
-> Writing .dockerignore.
-> Writing docker-compose.yml (port 3000 mapped).
