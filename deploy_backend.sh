#!/bin/bash
# Deployment Script: Full Docker Stack

echo "🚀 Starting Full Docker Stack..."

# 1. Start Services
echo "📦 Running docker-compose up..."
docker compose up -d --build

echo "✅ Deployment initiated via Docker Compose."
echo "🌍 URL: http://localhost:5000"
echo "📊 Monitoring: docker compose logs -f"
