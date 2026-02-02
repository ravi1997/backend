# Skill: Docker Compose Local Development

## Purpose

Create a `docker-compose.yml` configuration for local development that supports hot-reloading, service dependencies, and environment configuration.

## Inputs

- **Stack Type**: From `agent/09_state/STACK_STATE.md`
- **Services Needed**: Application + any dependencies (database, Redis, etc.)
- **Existing Dockerfile**: Path to Dockerfile (if exists)

## Outputs

- `docker-compose.yml` at project root
- `docker-compose.override.yml` for local dev (optional)
- `.env.example` with documented environment variables
- Updated `README.md` with compose usage

## Procedure

### Step 1: Define Application Service

1. Create main service with:
   - Build context pointing to Dockerfile
   - Port mapping for application
   - Volume mounts for hot-reload (bind mount source code)
   - Environment variables from `.env` file
   - Healthcheck configuration
   - Restart policy

### Step 2: Add Dependent Services

Based on stack requirements, add:

- **PostgreSQL**: If SQL database detected
- **MongoDB**: If NoSQL database detected
- **Redis**: If caching/sessions needed
- **Nginx**: If reverse proxy needed

For each service:

- Use official images with pinned versions
- Configure volumes for data persistence
- Set environment variables
- Define healthchecks
- Configure networks if needed

### Step 3: Configure Networks and Volumes

1. Define named volumes for persistent data
2. Create custom network if services need isolation
3. Ensure proper service dependencies with `depends_on`

### Step 4: Create Environment Template

Create `.env.example`:

```env
# Application
APP_PORT=3000
NODE_ENV=development

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=myapp
DB_USER=postgres
DB_PASSWORD=changeme

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

### Step 5: Validate and Test

1. Run `docker compose config` to validate syntax
2. Run `docker compose up --build` to start services
3. Verify application starts and connects to dependencies
4. Test hot-reload by modifying source file
5. Check logs with `docker compose logs -f`

### Step 6: Document

Add to `README.md`:

```markdown
## Local Development with Docker Compose

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

1. Start all services:

   ```bash
   docker compose up
   ```

2. View logs:

   ```bash
   docker compose logs -f [service-name]
   ```

3. Stop services:

   ```bash
   docker compose down
   ```

4. Reset volumes:

   ```bash
   docker compose down -v
   ```

```

## Failure Modes

### Services Won't Start

- **Cause**: Port conflicts, missing environment variables
- **Fix**: Check ports with `netstat`, verify `.env` file exists

### Hot Reload Not Working

- **Cause**: Volume mounts not configured correctly
- **Fix**: Ensure source code is mounted as volume, check file watcher limits

### Database Connection Fails

- **Cause**: Service not ready when app starts, wrong hostname
- **Fix**: Add `depends_on` with healthcheck, use service name as hostname

### Permission Issues with Volumes

- **Cause**: User ID mismatch between host and container
- **Fix**: Set user in compose file, adjust ownership in Dockerfile

## Examples

### Full-Stack Node.js + PostgreSQL + Redis

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "${APP_PORT:-3000}:3000"
    volumes:
      - ./src:/app/src
      - ./public:/app/public
    environment:
      - NODE_ENV=development
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - app-network

volumes:
  postgres-data:
  redis-data:

networks:
  app-network:
    driver: bridge
```

### Python FastAPI + MongoDB

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - MONGODB_DB=${DB_NAME}
    depends_on:
      - mongo
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  mongo:
    image: mongo:7
    environment:
      - MONGO_INITDB_DATABASE=${DB_NAME}
    volumes:
      - mongo-data:/data/db
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mongo-data:
```

## Related Files

- `agent/05_gates/global/gate_global_docker.md`
- `agent/06_skills/devops/skill_docker_baseline.md`
- `agent/07_templates/devops/docker-compose.template.yml.md`
