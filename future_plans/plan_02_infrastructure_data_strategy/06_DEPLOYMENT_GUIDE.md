# Deployment Guide
## Plan 2: Infrastructure & Data Strategy

**Version:** 1.0  
**Date:** 2026-01-09  
**Target Environment:** CPU-Only Production Server

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Application Deployment](#application-deployment)
4. [Configuration](#configuration)
5. [Starting Services](#starting-services)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedure](#rollback-procedure)
9. [Maintenance](#maintenance)

---

## Prerequisites

### Hardware Requirements
- **CPU:** 8+ cores (16+ recommended)
- **RAM:** 16GB minimum (32GB+ recommended)
- **Disk:** 100GB+ SSD
- **Network:** Static IP address, domain name configured

### Software Requirements
- **Operating System:** Ubuntu 22.04 LTS or Debian 12
- **Docker:** Version 24.0 or later
- **Docker Compose:** Version 2.0 or later
- **Git:** Latest version
- **SSL Certificate:** Valid SSL certificate for HTTPS

### Access Requirements
- Root or sudo access to the server
- SSH access configured
- DNS records pointing to server IP
- Firewall access to configure ports

---

## Server Setup

### 1. Initial Server Configuration

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    ufw \
    fail2ban

# Set up firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Configure fail2ban for SSH protection
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 2. Install Docker

```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group
sudo usermod -aG docker $USER

# Enable Docker to start on boot
sudo systemctl enable docker
sudo systemctl start docker

# Verify installation
docker --version
docker compose version
```

### 3. Configure Docker

```bash
# Create Docker daemon configuration
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF

# Restart Docker to apply changes
sudo systemctl restart docker
```

### 4. Create Application Directory Structure

```bash
# Create application directory
sudo mkdir -p /opt/form-management
sudo chown -R $USER:$USER /opt/form-management
cd /opt/form-management

# Create subdirectories
mkdir -p {data,logs,backups,config,ssl}

# Set proper permissions
chmod 755 data logs backups config
chmod 700 ssl
```

---

## Application Deployment

### 1. Clone Repository

```bash
cd /opt/form-management

# Clone the repository
git clone https://github.com/your-org/form-management-system.git .

# Or if using a specific branch/tag
git clone -b plan-02 https://github.com/your-org/form-management-system.git .

# Verify clone
ls -la
```

### 2. Install SSL Certificates

#### Option A: Using Let's Encrypt (Recommended for Production)

```bash
# Install certbot
sudo apt install -y certbot

# Obtain certificates
sudo certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive

# Copy certificates to application directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/form-management/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/form-management/ssl/
sudo chown $USER:$USER /opt/form-management/ssl/*.pem

# Set up auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

#### Option B: Using Existing Certificates

```bash
# Copy your certificate files to ssl directory
cp /path/to/your/fullchain.pem /opt/form-management/ssl/
cp /path/to/your/privkey.pem /opt/form-management/ssl/

# Set proper permissions
chmod 600 /opt/form-management/ssl/*.pem
```

---

## Configuration

### 1. Environment Variables

```bash
# Create .env file from template
cp .env.example .env

# Edit .env file
nano .env
```

**Required environment variables:**

```bash
# Application
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-strong-random-key>
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
MONGODB_URL=mongodb://mongodb:27017/form_management
MONGODB_DATABASE=form_management

# Cache and Queue
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# API Configuration
API_VERSION=v1
API_PREFIX=/api/v1
CORS_ORIGINS=https://your-domain.com

# Email (if applicable)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=<your-smtp-password>
SMTP_FROM=noreply@your-domain.com

# AI Configuration
AI_MODEL_PATH=/models
AI_MODEL_NAME=mistral-7b-instruct-q4_k_m.gguf
AI_MAX_TOKENS=512
AI_TEMPERATURE=0.7
AI_TIMEOUT=300

# Resource Limits
GUNICORN_WORKERS=auto
CELERY_WORKER_HIGH_CONCURRENCY=4
CELERY_WORKER_DEFAULT_CONCURRENCY=4
CELERY_WORKER_AI_CONCURRENCY=1

# Monitoring
PROMETHEUS_ENABLED=True
PROMETHEUS_PORT=9090
```

**Generate secret key:**

```bash
# Generate a strong secret key
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 2. Docker Compose Configuration Review

```bash
# Review docker-compose.yml
cat docker-compose.yml

# Review docker-compose.prod.yml (if exists)
cat docker-compose.prod.yml
```

**Important configurations to verify:**

```yaml
# Resource limits
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 4G
    reservations:
      cpus: '2.0'
      memory: 2G

# Restart policy
restart: unless-stopped

# Health checks
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 3. Download AI Models (if using AI features)

```bash
# Create models directory
mkdir -p /opt/form-management/models

# Download quantized model (example: Mistral 7B)
cd /opt/form-management/models

# Using wget or curl
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Or using huggingface-cli
pip install huggingface-hub
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF mistral-7b-instruct-v0.2.Q4_K_M.gguf --local-dir .

# Verify downloaded
ls -lh
```

---

## Starting Services

### 1. Build Docker Images

```bash
cd /opt/form-management

# Build all images
docker compose build

# Or build with no cache (clean build)
docker compose build --no-cache

# Verify images built
docker images | grep form-management
```

### 2. Initialize Database

```bash
# Start only database services
docker compose up -d mongodb redis

# Wait for databases to be ready
sleep 10

# Run database migrations (if applicable)
docker compose run --rm api python manage.py migrate

# Create initial superuser (if applicable)
docker compose run --rm api python manage.py createsuperuser
```

### 3. Start All Services

```bash
# Start all services in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Check service status
docker compose ps
```

**Expected output:**

```
NAME                    IMAGE                      STATUS              PORTS
form-api                form-management-api        Up 30 seconds       0.0.0.0:8000->8000/tcp
form-nginx              nginx:alpine               Up 30 seconds       0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
form-worker-high        form-management-worker     Up 30 seconds       
form-worker-default     form-management-worker     Up 30 seconds       
form-worker-ai          form-management-worker     Up 30 seconds       
form-mongodb            mongo:5.0                  Up 1 minute         27017/tcp
form-redis              redis:7-alpine             Up 1 minute         6379/tcp
```

### 4. Verify Services are Running

```bash
# Check all containers are running
docker compose ps

# Check health status
docker compose ps --format json | jq '.[] | {name: .Name, health: .Health}'

# Check logs for errors
docker compose logs --tail=50

# Check individual service
docker compose logs api --tail=20
```

---

## Verification

### 1. Health Checks

```bash
# API health check
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "2026-01-09T12:00:00Z"}

# Detailed health check
curl http://localhost:8000/health/detailed

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "cache": "connected",
#   "queue": "connected",
#   "workers": {
#     "high-priority": "running",
#     "default": "running",
#     "ai": "running"
#   }
# }
```

### 2. Test API Endpoints

```bash
# Test API root
curl http://localhost:8000/api/v1/

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# Test form creation (with token)
TOKEN="your-jwt-token-here"
curl -X POST http://localhost:8000/api/v1/forms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Form", "fields": []}'
```

### 3. Test HTTPS

```bash
# Test HTTPS endpoint
curl https://your-domain.com/health

# Check SSL certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Test with SSL Labs (from browser)
# https://www.ssllabs.com/ssltest/analyze.html?d=your-domain.com
```

### 4. Test Task Queue

```bash
# Queue a test task
curl -X POST http://localhost:8000/api/v1/tasks/test \
  -H "Authorization: Bearer $TOKEN"

# Check task status
curl http://localhost:8000/api/v1/tasks/{task-id} \
  -H "Authorization: Bearer $TOKEN"

# Monitor Celery workers
docker compose exec worker-high celery -A app.celery inspect active
```

### 5. Test AI Inference (if enabled)

```bash
# Test AI endpoint
curl -X POST http://localhost:8000/api/v1/ai/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test prompt for AI analysis"}'

# Expected response:
# {
#   "task_id": "ai-task-123",
#   "status": "PENDING",
#   "message": "AI analysis queued"
# }

# Check task status (after some time)
curl http://localhost:8000/api/v1/tasks/ai-task-123 \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Monitor Resource Usage

```bash
# Check Docker stats
docker stats

# Check specific container
docker stats form-api

# Check disk usage
df -h

# Check memory usage
free -h

# Check CPU usage
top -bn1 | head -20
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Container fails to start

**Diagnosis:**
```bash
# Check container logs
docker compose logs <service-name>

# Check container status
docker compose ps

# Inspect container
docker inspect <container-name>
```

**Solutions:**
- Check environment variables in `.env`
- Verify resource limits aren't too restrictive
- Check port conflicts: `sudo netstat -tulpn | grep LISTEN`
- Ensure dependencies (db, redis) are running first

#### Issue: Database connection failed

**Diagnosis:**
```bash
# Test MongoDB connection
docker compose exec mongodb mongosh --eval "db.runCommand({ ping: 1 })"

# Check MongoDB logs
docker compose logs mongodb

# Test connection from API container
docker compose exec api nc -zv mongodb 27017
```

**Solutions:**
- Verify MongoDB is running: `docker compose ps mongodb`
- Check MONGODB_URL environment variable
- Ensure containers are on same network
- Check MongoDB authentication settings

#### Issue: High memory usage / OOM kills

**Diagnosis:**
```bash
# Check memory usage
docker stats

# Check kernel logs for OOM killer
sudo dmesg | grep -i "killed process"

# Check container resource limits
docker compose config | grep -A 5 "resources"
```

**Solutions:**
- Increase memory limits in docker-compose.yml
- Reduce worker concurrency
- Use smaller AI models
- Add swap space (not recommended for production)
- Implement proper pagination

#### Issue: AI inference too slow

**Diagnosis:**
```bash
# Check AI worker logs
docker compose logs worker-ai

# Check CPU usage during inference
docker stats worker-ai

# Check model size
ls -lh models/
```

**Solutions:**
- Use smaller quantized model (e.g., Q4 instead of Q8)
- Increase CPU allocation to AI worker
- Reduce max_tokens
- Implement request batching
- Add caching for similar prompts

#### Issue: Nginx 502 Bad Gateway

**Diagnosis:**
```bash
# Check nginx logs
docker compose logs nginx

# Check nginx configuration
docker compose exec nginx nginx -t

# Check API is running
curl http://localhost:8000/health

# Check upstream connection
docker compose exec nginx nc -zv api 8000
```

**Solutions:**
- Verify API container is running
- Check Gunicorn is listening on correct port
- Increase upstream timeout in nginx config
- Check network connectivity between nginx and api

#### Issue: SSL certificate errors

**Diagnosis:**
```bash
# Check certificate files
ls -l /opt/form-management/ssl/

# Verify certificate validity
openssl x509 -in /opt/form-management/ssl/fullchain.pem -text -noout

# Check nginx SSL configuration
docker compose exec nginx cat /etc/nginx/conf.d/default.conf | grep ssl
```

**Solutions:**
- Verify certificate files exist and are readable
- Check certificate hasn't expired
- Ensure certificate matches domain
- Verify certificate chain is complete
- Check file permissions (should be 600)

### Logging

#### View all logs:
```bash
docker compose logs
```

#### View specific service logs:
```bash
docker compose logs api
docker compose logs worker-ai
docker compose logs mongodb
```

#### Follow logs in real-time:
```bash
docker compose logs -f
```

#### View last N lines:
```bash
docker compose logs --tail=100
```

#### Save logs to file:
```bash
docker compose logs > logs/deployment-$(date +%Y%m%d-%H%M%S).log
```

---

## Rollback Procedure

### Automatic Rollback

If deployment fails, you can quickly rollback:

```bash
# Stop current deployment
docker compose down

# Restore previous version from Git
git log --oneline  # Find previous commit
git checkout <previous-commit-hash>

# Or restore from backup
tar -xzf backups/backup-YYYYMMDD.tar.gz -C /opt/form-management

# Rebuild and restart
docker compose build
docker compose up -d

# Verify rollback
curl http://localhost:8000/health
```

### Manual Rollback Steps

1. **Stop services:**
   ```bash
   docker compose down
   ```

2. **Restore database backup (if needed):**
   ```bash
   # Stop current database
   docker compose down mongodb
   
   # Restore backup
   mongorestore --uri="mongodb://localhost:27017" \
     --archive=backups/mongodb-backup-YYYYMMDD.archive \
     --gzip
   
   # Restart database
   docker compose up -d mongodb
   ```

3. **Restore application code:**
   ```bash
   git checkout <previous-stable-tag>
   # Or manually restore files from backup
   ```

4. **Restore configuration:**
   ```bash
   cp backups/.env.backup .env
   ```

5. **Restart services:**
   ```bash
   docker compose up -d
   ```

6. **Verify:**
   ```bash
   docker compose ps
   curl http://localhost:8000/health
   ```

---

## Maintenance

### Daily Tasks

```bash
# Check service health
docker compose ps

# Check disk space
df -h

# Quick log review
docker compose logs --tail=100 | grep -i error
```

### Weekly Tasks

```bash
# Review logs
docker compose logs --since 7d > logs/weekly-$(date +%Y%m%d).log

# Check for updates
docker compose pull

# Backup database
./scripts/backup-database.sh

# Clean up old logs
find logs/ -name "*.log" -mtime +7 -delete

# Clean up Docker
docker system prune -f
```

### Backup Script

Create `/opt/form-management/scripts/backup-database.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/form-management/backups"
DATE=$(date +%Y%m%d-%H%M%S)

# Backup MongoDB
docker compose exec -T mongodb mongodump \
  --archive=/tmp/mongodb-backup.archive \
  --gzip

docker compose cp mongodb:/tmp/mongodb-backup.archive \
  $BACKUP_DIR/mongodb-backup-$DATE.archive

# Backup Redis (optional, for cached data)
docker compose exec -T redis redis-cli SAVE
docker compose cp redis:/data/dump.rdb \
  $BACKUP_DIR/redis-backup-$DATE.rdb

# Backup configuration
cp .env $BACKUP_DIR/.env.backup-$DATE

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "*.archive" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make it executable:
```bash
chmod +x /opt/form-management/scripts/backup-database.sh
```

### Automated Backups with Cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/form-management/scripts/backup-database.sh >> /opt/form-management/logs/backup.log 2>&1
```

### Monitoring

Access Prometheus metrics:
```bash
curl http://localhost:9090/metrics
```

Access Grafana (if installed):
```
http://your-domain.com:3000
```

---

## Next Steps

After successful deployment:

1. **Set up monitoring alerts** (see Monitoring Guide)
2. **Configure backups** (automated daily backups)
3. **Set up log aggregation** (optional, for centralized logging)
4. **Configure CDN** (optional, for static assets)
5. **Load testing** (verify performance under load)
6. **Security audit** (penetration testing)
7. **Document custom configurations**
8. **Train operations team**

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review logs: `docker compose logs`
- Consult documentation: `/docs`
- Contact DevOps team: devops@your-organization.com

---

**Document Status:** Ready for Production  
**Last Updated:** 2026-01-09  
**Maintained By:** DevOps Team
