# Example: Docker Setup

## Purpose

Demonstrates how to add Docker to a project following Agent OS standards.

## Agent OS Integration

- **Workflow**: `agent/04_workflows/02_repo_audit_and_baseline.md`
- **Skill**: `agent/06_skills/devops/skill_docker_baseline.md`
- **Gate**: `agent/05_gates/global/gate_global_docker.md`
- **Rules**: `agent/11_rules/docker_rules.md`

## Scenario

Adding Docker to a Python FastAPI project.

## Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY . .

FROM python:3.11-slim

RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --from=builder --chown=appuser:appuser /app /app

ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8000

HEALTHCHECK CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Step 2: Create .dockerignore

```dockerignore
.git
.env
__pycache__
*.pyc
.pytest_cache
venv
tests
README.md
```

## Step 3: Create docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app:ro
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/myapp
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres-data:
```

## Step 4: Test

```bash
# Build
docker build -t myapp .

# Run with compose
docker compose up

# Test API
curl http://localhost:8000/health

# View logs
docker compose logs -f api
```

## Step 5: Validate Against Gate

Check `agent/05_gates/global/gate_global_docker.md`:

- [x] Base image pinned (`python:3.11-slim`)
- [x] Multi-stage build
- [x] Non-root user (`appuser`)
- [x] No secrets in Dockerfile
- [x] .dockerignore present
- [x] Environment variables used
- [x] Healthcheck defined
- [x] Port exposed

## Complete Examples

See `prompts/examples_devops/docker_examples.md` for more stacks:

- Python (Flask/FastAPI)
- Node.js (Express)
- Next.js
- Flutter
- Java (Spring Boot)
- C++ (CMake)
