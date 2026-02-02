# Docker Compose Template: Dev Environment

```yaml
version: '3.8'

services:
  # Main Application
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: runner # Or 'dev' target if separate
    container_name: {{PROJECT_NAME}}-app
    ports:
      - "{{PORT}}:{{PORT}}"
    volumes:
      - ./:/app
      - /app/node_modules # Prevent host node_modules from overwriting container
    environment:
      - NODE_ENV=development
      - PORT={{PORT}}
      - DATABASE_URL=postgres://user:password@db:5432/{{PROJECT_NAME}}
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app_network
    # Command to enable hot-reload (e.g., nodemon or next dev)
    command: npm run dev

  # Database Service (Example: Postgres)
  db:
    image: postgres:15-alpine
    container_name: {{PROJECT_NAME}}-db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: {{PROJECT_NAME}}
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - app_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  app_network:
    driver: bridge

volumes:
  db_data:
```
