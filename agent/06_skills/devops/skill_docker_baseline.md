# Skill: Docker Baseline

## Purpose

Create a production-ready Dockerfile for a detected stack, following industry best practices for security, performance, and maintainability.

## Inputs

- **Stack Type**: Detected from `agent/09_state/STACK_STATE.md` (e.g., Python FastAPI, Node Express, Next.js)
- **Project Root**: Absolute path to project directory
- **Entry Point**: Main application file (e.g., `main.py`, `index.js`, `app.ts`)
- **Dependencies**: Package manager files (e.g., `requirements.txt`, `package.json`)

## Outputs

- `Dockerfile` at project root
- `.dockerignore` at project root
- Updated documentation in `README.md` with Docker usage instructions

## Procedure

### Step 1: Analyze Stack Requirements

1. Read the stack fingerprint from `agent/02_detection/stack_fingerprints/`
2. Identify the recommended base image for the stack
3. Determine the build command, runtime command, and default port
4. Check for any stack-specific requirements (e.g., system dependencies)

### Step 2: Create Multi-Stage Dockerfile

1. **Builder Stage**:
   - Use appropriate base image (e.g., `python:3.11-slim`, `node:20-alpine`)
   - Set working directory to `/app`
   - Copy dependency files first (for layer caching)
   - Install dependencies
   - Copy application code

2. **Runtime Stage**:
   - Use same or slimmer base image
   - Create non-root user (e.g., `appuser`)
   - Copy only necessary files from builder
   - Set proper ownership
   - Expose required ports
   - Add healthcheck if applicable
   - Set USER to non-root
   - Define CMD or ENTRYPOINT

### Step 3: Create .dockerignore

Include common exclusions:

- `.git/`
- `node_modules/` (for Node.js)
- `__pycache__/`, `*.pyc` (for Python)
- `.env`, `.env.*`
- `*.log`
- `README.md`, `docs/`
- `.vscode/`, `.idea/`
- `tests/`, `*.test.*`
- Build artifacts specific to stack

### Step 4: Validate

1. Run `docker build -t test-image .`
2. Check image size (should be reasonable for stack)
3. Run `docker run --rm test-image` to verify it starts
4. Check for security issues with `docker scan test-image` (if available)

### Step 5: Document

Add to `README.md`:

```markdown
## Docker

Build the image:
```bash
docker build -t <project-name> .
```

Run the container:

```bash
docker run -p <port>:<port> <project-name>
```

```

## Failure Modes

### Build Fails Due to Missing Dependencies

- **Cause**: System packages not installed in Dockerfile
- **Fix**: Add `RUN apt-get update && apt-get install -y <packages>` in builder stage

### Image Size Too Large

- **Cause**: Not using multi-stage build or including unnecessary files
- **Fix**: Implement multi-stage build, use Alpine base images, improve `.dockerignore`

### Permission Errors

- **Cause**: Files owned by root, non-root user can't access
- **Fix**: Use `COPY --chown=appuser:appuser` or `RUN chown` after copy

### Application Doesn't Start

- **Cause**: Incorrect CMD/ENTRYPOINT or missing environment variables
- **Fix**: Test command locally, ensure ENV vars are documented

## Examples

### Python FastAPI Example

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
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1
USER appuser
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Node.js Express Example

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

FROM node:20-alpine
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app /app
EXPOSE 3000
HEALTHCHECK CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1
USER appuser
CMD ["node", "index.js"]
```

## Related Files

- `agent/05_gates/global/gate_global_docker.md`
- `agent/11_rules/docker_rules.md`
- `agent/07_templates/devops/Dockerfile.template.md`
- Stack-specific fingerprints in `agent/02_detection/stack_fingerprints/`
