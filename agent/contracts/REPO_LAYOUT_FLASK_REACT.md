# Contract: Repo Layout (Flask API + React)

Recommended:
- `backend/` (Flask API)
- `frontend/` (Vite React)
- `nginx/` reverse proxy
- `docker-compose.yml` at root

Agent assumptions:
- backend runs on :8000 internally
- frontend built and served via nginx or separate dev server in dev
