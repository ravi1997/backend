FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Try to install from wheels if they exist, otherwise use requirements.txt
COPY wheels /wheels
RUN if [ -d "/wheels" ] && [ "$(ls -A /wheels)" ]; then \
        pip install --no-index --find-links=/wheels /wheels/*; \
    else \
        pip install -r requirements.txt; \
    fi

# Copy the rest of the application
COPY . .

EXPOSE 5000

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Default command (can be overridden in docker-compose)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "run:app"]
