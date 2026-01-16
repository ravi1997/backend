# Universal Docker Compose Template

This template includes configured services for a full-stack application. Uncomment the sections you need.

```yaml
version: '3.8'

services:
  # ==========================================
  # APP SERVICES (Select one or more)
  # ==========================================

  # --- Node.js / Web Backend ---
  # backend:
  #   build: .
  #   command: npm start
  #   ports:
  #     - "3000:3000"
  #   environment:
  #     - DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
  #   volumes:
  #     - .:/app
  #     - /app/node_modules
  #     # Shared Cache (Optional - See agent/docker/SHARED_CACHES.md)
  #     # - ${HOME}/.npm:/root/.npm
  #   depends_on:
  #     - db
  #   networks:
  #     - app_network

  # --- Python (Flask/FastAPI) ---
  # backend:
  #   build: .
  #   command: gunicorn --bind 0.0.0.0:8000 app:app
  #   ports:
  #     - "8000:8000"
  #   env_file: .env
  #   volumes:
  #     - .:/app
  #     # Shared Cache
  #     # - ${HOME}/.cache/pip:/root/.cache/pip
  #   depends_on:
  #     - db
  #   networks:
  #     - app_network

  # --- Golang ---
  # backend:
  #   build: .
  #   ports:
  #     - "8080:8080"
  #   volumes:
  #     - .:/app
  #     # Shared Mod Cache
  #     # - ${HOME}/go/pkg/mod:/go/pkg/mod
  #   networks:
  #     - app_network

  # --- Frontend (Static/SPA) served by Nginx ---
  # frontend:
  #   build: ./frontend
  #   ports:
  #     - "80:80"
  #   volumes:
  #     - ./frontend:/app
  #     - /app/node_modules
  #   networks:
  #     - app_network

  # ==========================================
  # INFRASTRUCTURE SERVICES
  # ==========================================

  # --- PostgreSQL ---
  # db:
  #   image: postgres:16-alpine
  #   restart: always
  #   environment:
  #     POSTGRES_USER: ${DB_USER:-postgres}
  #     POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
  #     POSTGRES_DB: ${DB_NAME:-app_db}
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   networks:
  #     - app_network

  # --- Redis ---
  # redis:
  #   image: redis:7-alpine
  #   restart: always
  #   ports:
  #     - "6379:6379"
  #   volumes:
  #     - redis_data:/data
  #   networks:
  #     - app_network

networks:
  app_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  # mongo_data:
```
