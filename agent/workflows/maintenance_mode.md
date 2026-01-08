# Workflow: Maintenance Mode

**Purpose:** Enable maintenance mode for scheduled downtime
**When to use:** Database maintenance, server updates, planned downtime
**Prerequisites:** Maintenance window scheduled, stakeholders notified
**Estimated time:** Variable (depends on maintenance task)
**Outputs:** Maintenance completed, service restored

---

## Prerequisites

- [ ] Maintenance window scheduled
- [ ] Stakeholders notified
- [ ] Backup created
- [ ] Maintenance tasks documented
- [ ] Rollback plan ready

---

## Step 1: Prepare

### Create Backup
```bash
# Database backup
pg_dump mydb > backup_maintenance_$(date +%Y%m%d_%H%M%S).sql

# Code backup
git tag maintenance-$(date +%Y%m%d-%H%M%S)
git push --tags
```

### Notify Users
```bash
# Update status page
# Send email notification
# Post on social media
```

---

## Step 2: Enable Maintenance Mode

### Option A: Nginx Maintenance Page
```bash
# Create maintenance page
cat > /var/www/maintenance.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Maintenance</title>
</head>
<body>
    <h1>Scheduled Maintenance</h1>
    <p>We'll be back soon!</p>
    <p>Expected completion: [TIME]</p>
</body>
</html>
EOF

# Update nginx config
sudo nano /etc/nginx/sites-available/myapp
# Add:
# location / {
#     return 503;
#     error_page 503 /maintenance.html;
# }

# Reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Option B: Application Maintenance Mode
```python
# Add to app config
MAINTENANCE_MODE = True

# In middleware
if app.config['MAINTENANCE_MODE']:
    return jsonify({"error": "Maintenance in progress"}), 503
```

---

## Step 3: Perform Maintenance

### Database Maintenance
```bash
# Stop application
sudo systemctl stop myapp

# Run maintenance tasks
# - Vacuum database
# - Rebuild indexes
# - Update statistics
# - Apply schema changes

# PostgreSQL example
psql mydb << EOF
VACUUM ANALYZE;
REINDEX DATABASE mydb;
EOF
```

### Server Updates
```bash
# Update packages
sudo apt update
sudo apt upgrade -y

# Reboot if needed
sudo reboot
```

---

## Step 4: Test Before Enabling

```bash
# Start application in test mode
# ... start app ...

# Run smoke tests
curl -I http://localhost:8000/healthz
# Expected: 200 OK

# Test critical functionality
# ... manual tests ...
```

---

## Step 5: Disable Maintenance Mode

### Nginx
```bash
# Remove maintenance mode from nginx config
sudo nano /etc/nginx/sites-available/myapp
# Remove maintenance location block

# Reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Application
```python
# Update config
MAINTENANCE_MODE = False

# Restart application
sudo systemctl restart myapp
```

---

## Step 6: Verify

```bash
# Application accessible?
curl -I https://myapp.com
# Expected: 200 OK

# All services running?
sudo systemctl status myapp
docker-compose ps

# No errors in logs?
sudo journalctl -u myapp -n 50 | grep -i error
```

---

## Step 7: Monitor

```bash
# Watch logs for 15-20 minutes
sudo journalctl -u myapp -f

# Monitor metrics
# - Error rates
# - Response times
# - User activity
```

---

## Completion Criteria

- ✅ Maintenance tasks completed
- ✅ Application restored
- ✅ Maintenance mode disabled
- ✅ All services running
- ✅ No errors in logs
- ✅ Users can access the application
- ✅ Monitored for 15-20 minutes

---

## Rollback Plan

If maintenance causes issues:

```bash
# 1. Re-enable maintenance mode
# ... enable maintenance page ...

# 2. Restore from backup
psql mydb < backup_maintenance_YYYYMMDD_HHMMSS.sql

# 3. Rollback code (if changed)
git checkout <previous-tag>

# 4. Restart services
sudo systemctl restart myapp

# 5. Verify
curl -I https://myapp.com/healthz
```

---

## Post-Maintenance

### Notify Users
```bash
# Update status page
# Send completion email
# Post on social media
```

### Document
```bash
# Create maintenance report
# - What was done
# - Any issues encountered
# - Duration
# - Next maintenance window
```

---

## Common Maintenance Tasks

### Database
- Vacuum and analyze
- Rebuild indexes
- Update statistics
- Archive old data
- Optimize queries

### Server
- OS updates
- Security patches
- Disk cleanup
- Log rotation
- Certificate renewal

### Application
- Dependency updates
- Cache clearing
- Session cleanup
- Data migration

---

## See Also

- [`../workflows/deploy_and_migrate.md`](deploy_and_migrate.md)
- [`../workflows/rollback_recovery.md`](rollback_recovery.md)
