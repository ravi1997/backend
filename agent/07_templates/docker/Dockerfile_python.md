# Dockerfile Template: Python (Flask/FastAPI)

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runner
FROM python:3.11-slim as runner

WORKDIR /app

# Create non-root user
RUN addgroup --system pygroup && adduser --system --group pyuser

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy application code
COPY . /app

# Switch to non-root user
USER pyuser

EXPOSE {{PORT}}

# Use Gunicorn/Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{{PORT}}"]
```
