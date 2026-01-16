# Snippet: Dockerfile for Python (Multi-stage)

```dockerfile

# Scope: General Python (Flask, FastAPI, Django)

# Metadata: multi-stage, non-root, slim

# CLARIFY: python_version (e.g. 3.11-slim)

# CLARIFY: app_entrypoint (e.g. "gunicorn", "-w", "4", "main:app")

# --- Build Stage ---

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies if needed (e.g., GCC, libpq-dev)

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Runtime Stage ---

FROM python:3.11-slim

WORKDIR /app

# Create a non-root user

RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder

COPY --from=builder /root/.local /home/appuser/.local
COPY . .

# Ensure the non-root user owns the app directory

RUN chown -R appuser:appuser /app

# Set environment variables

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user

USER appuser

# Expose port (default 8000, adjust as needed)

EXPOSE 8000

# Entrypoint

CMD ["python", "app.py"]

```
