# Template: docker-compose.yml

## Purpose

This template provides a parameterized docker-compose configuration for local development with common service patterns.

## Parameters

- `{{APP_SERVICE_NAME}}`: Name of the main application service (e.g., `app`, `api`, `web`)
- `{{APP_PORT}}`: Application port mapping (e.g., `3000:3000`, `8000:8000`)
- `{{APP_ENV_VARS}}`: Application environment variables
- `{{DB_SERVICE}}`: Database service type (e.g., `postgres`, `mongodb`, `mysql`)
- `{{CACHE_SERVICE}}`: Cache service type (e.g., `redis`, `memcached`)
- `{{VOLUMES}}`: Volume definitions for data persistence

## Template

```yaml
version: '3.8'

services:
  {{APP_SERVICE_NAME}}:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "{{APP_PORT}}"
    volumes:
      # Mount source code for hot-reload in development
      - ./src:/app/src
      - ./public:/app/public
    environment:
      {{APP_ENV_VARS}}
    depends_on:
      {{DB_SERVICE}}:
        condition: service_healthy
      {{CACHE_SERVICE}}:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped

  {{DB_SERVICE}}:
    image: {{DB_IMAGE}}
    environment:
      {{DB_ENV_VARS}}
    volumes:
      - {{DB_VOLUME}}:/var/lib/{{DB_SERVICE}}/data
    healthcheck:
      test: {{DB_HEALTHCHECK}}
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network
    restart: unless-stopped

  {{CACHE_SERVICE}}:
    image: {{CACHE_IMAGE}}
    volumes:
      - {{CACHE_VOLUME}}:/data
    healthcheck:
      test: {{CACHE_HEALTHCHECK}}
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - app-network
    restart: unless-stopped

volumes:
  {{DB_VOLUME}}:
  {{CACHE_VOLUME}}:

networks:
  app-network:
    driver: bridge
```

## Example: Node.js + PostgreSQL + Redis

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
      - DB_NAME=${DB_NAME:-myapp}
      - DB_USER=${DB_USER:-postgres}
      - DB_PASSWORD=${DB_PASSWORD:-postgres}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=${DB_NAME:-myapp}
      - POSTGRES_USER=${DB_USER:-postgres}
      - POSTGRES_PASSWORD=${DB_PASSWORD:-postgres}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network
    restart: unless-stopped

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
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:

networks:
  app-network:
    driver: bridge
```

## Example: Python FastAPI + MongoDB

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "${APP_PORT:-8000}:8000"
    volumes:
      - ./app:/app/app
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - MONGODB_DB=${DB_NAME:-myapp}
    depends_on:
      mongo:
        condition: service_healthy
    networks:
      - app-network
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  mongo:
    image: mongo:7
    environment:
      - MONGO_INITDB_DATABASE=${DB_NAME:-myapp}
    volumes:
      - mongo-data:/data/db
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

volumes:
  mongo-data:

networks:
  app-network:
    driver: bridge
```

## Example: Next.js + PostgreSQL (Development)

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
      target: builder
    ports:
      - "3000:3000"
    volumes:
      - ./src:/app/src
      - ./app:/app/app
      - ./public:/app/public
      - /app/node_modules
      - /app/.next
    environment:
      - DATABASE_URL=postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-postgres}@postgres:5432/${DB_NAME:-myapp}
      - NEXTAUTH_URL=http://localhost:3000
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - app-network
    command: npm run dev

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=${DB_NAME:-myapp}
      - POSTGRES_USER=${DB_USER:-postgres}
      - POSTGRES_PASSWORD=${DB_PASSWORD:-postgres}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

volumes:
  postgres-data:

networks:
  app-network:
    driver: bridge
```

## Notes

- Use environment variables with defaults for flexibility
- Always include healthchecks for dependent services
- Use named volumes for data persistence
- Mount source code as volumes for hot-reload in development
- Use `depends_on` with `condition: service_healthy` for proper startup order
- Create separate `docker-compose.prod.yml` for production if needed

## Related Files

- `agent/11_rules/docker_rules.md`
- `agent/06_skills/devops/skill_compose_local_dev.md`
- `agent/07_templates/devops/.dockerignore.template.md`
