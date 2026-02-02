# Deployment Guide

This document provides instructions for setting up and deploying the Form Management System Backend.

## 1. Prerequisites

- **Python**: 3.12 or higher.
- **Database**: MongoDB (v6.0+) and PostgreSQL (optional, for metadata).
- **Containerization**: Docker and Docker Compose (recommended).
- **External Services**:
  - Ollama (for AI features)
  - SMS Gateway (for OTP login)

---

## 2. Environment Configuration

Copy the example environment file and fill in the required values:

```bash
cp .env.example .env
```

### Core Configuration Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode (`development`, `production`, `testing`) | `development` |
| `SECRET_KEY` | Flask secret key for session signing | `your_secret_key` |
| `JWT_SECRET_KEY`| Secret key for JWT token generation | `your_jwt_secret` |
| `DATABASE_URI` | SQLAlchemy connection string (PostgreSQL) | `sqlite:///app.db` |

### MongoDB Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_DB` | Database name | `myflaskdb` |
| `MONGODB_HOST` | Database host | `localhost` |
| `MONGODB_PORT` | Database port | `27017` |
| `MONGODB_USER` | Username for auth | `None` |
| `MONGODB_PASS` | Password for auth | `None` |
| `MONGODB_AUTH_SOURCE` | Authentication database | `admin` |

### AI (Ollama) Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | AI provider type | `ollama` |
| `LLM_API_URL` | API endpoint for Ollama | `http://ollama:11434/v1` |
| `LLM_MODEL` | Model name to use | `llama3` |

---

## 3. Local Development Setup

1. **Create Virtual Environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:

   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:5000`.

---

## 4. Docker Deployment (Recommended)

The project includes a `docker-compose.yml` for easy orchestration.

### Using Makefile

The `Makefile` simplifies common commands:

- **Build and Start**: `make up`
- **Stop**: `make down`
- **View Logs**: `make logs`
- **Run Tests**: `make test`

### Manual Commands

```bash
docker-compose up --build -d
```

---

## 5. Security & Production Hardening

- **Logs**: Application logs are stored in `logs/app.log`. Ensure the directory is writable.
- **JWT Revocation**: The system uses a `TokenBlocklist` collection in MongoDB to handle logouts.
- **Production Config**: Set `FLASK_ENV=production` and update `MONGODB_SETTINGS` with proper credentials.
- **Reverse Proxy**: Use Nginx or Gunicorn in front of the Flask application for production.
