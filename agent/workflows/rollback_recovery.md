# Workflow: Rollback and Recovery

**Purpose:** Rollback a failed deployment and recover service
**When to use:** Deployment caused issues, need to revert to previous version
**Prerequisites:** Previous version available, backup exists
**Estimated time:** 10-20 minutes
**Outputs:** Service restored to previous working state

---

## Prerequisites

- [ ] Issue confirmed (deployment caused the problem)
- [ ] Previous version identified (git tag or commit)
- [ ] Backup available (if database changes)
- [ ] Stakeholders notified
- [ ] Production → `policy/PRODUCTION_POLICY.md`

---

## Step 1: Assess the Situation

### Determine Scope
- What broke?
- When did it break?
- What was the last working version?
- Were there database migrations?

### Decision: Rollback or Fix Forward?
- **Rollback if:** Issue is severe, fix will take time
- **Fix forward if:** Issue is minor, fix is quick

---

## Step 2: Rollback Code

### Git Rollback
```bash
# Find the last working version
git log --oneline -10

# Option A: Revert the merge commit
git revert -m 1 <merge-commit-hash>

# Option B: Checkout previous tag
git checkout <previous-tag>

# Create rollback branch
git checkout -b hotfix/rollback-deployment
git push origin hotfix/rollback-deployment
```

---

## Step 3: Rollback Database (if needed)

### Check for Migrations
```bash
# What migrations were applied?
alembic current

# What was the previous version?
alembic history | grep -B 5 "$(alembic current)"
```

### Rollback Migrations
```bash
# Rollback to previous version
alembic downgrade <previous-revision>

# Or rollback one step
alembic downgrade -1

# Verify
alembic current
```

### Restore from Backup (if needed)
```bash
# Stop application first
sudo systemctl stop myapp

# Restore database
psql mydb < backup_YYYYMMDD_HHMMSS.sql

# Verify restore
psql mydb -c "SELECT COUNT(*) FROM users;"
```

---

## Step 4: Redeploy Previous Version

### For Docker
```bash
# Pull rollback code
git pull origin hotfix/rollback-deployment

# Rebuild
docker-compose build

# Deploy
docker-compose down
docker-compose up -d

# Check status
docker-compose ps
```

### For systemd
```bash
# Pull rollback code
git pull origin hotfix/rollback-deployment

# Install dependencies (if needed)
pip install -r requirements.txt

# Restart service
sudo systemctl restart myapp

# Check status
sudo systemctl status myapp
```

---

## Step 5: Verify Rollback

### Health Checks
```bash
# Application running?
curl -I https://myapp.com/healthz
# Expected: 200 OK

# Database connected?
curl https://myapp.com/api/health
# Expected: {"status": "ok"}

# No errors in logs?
docker-compose logs --tail=50 | grep -i error
# or
sudo journalctl -u myapp -n 50 | grep -i error
# Expected: No critical errors
```

### Functional Tests
```bash
# Test critical functionality
# - User login
# - Key features
# - Data integrity
```

---

## Step 6: Monitor

```bash
# Watch logs for 10-15 minutes
docker-compose logs -f
# or
sudo journalctl -u myapp -f

# Monitor metrics
# - Error rates
# - Response times
# - Resource usage
```

---

## Completion Criteria

- ✅ Previous version deployed
- ✅ Database rolled back (if needed)
- ✅ Health checks passing
- ✅ No errors in logs
- ✅ Critical functionality working
- ✅ Monitored for 10-15 minutes
- ✅ Incident report created

**Do NOT mark complete until all criteria are met.**

---

## Post-Rollback Actions

### Document the Incident
```bash
# Create incident report
cp agent/artifacts/incident_report.md incidents/rollback-YYYYMMDD.md
# Fill in:
# - What failed
# - Why we rolled back
# - Impact
# - Next steps
```

### Plan the Fix
- What caused the issue?
- How to fix it properly?
- How to prevent it in the future?
- When to attempt deployment again?

---

## Required Artifacts

- **Always:** `artifacts/incident_report.md`
- **If major outage:** `artifacts/postmortem.md`

---

## Common Mistakes

❌ **Don't** rollback without notifying stakeholders
❌ **Don't** forget to rollback database migrations
❌ **Don't** skip verification steps
❌ **Don't** rush to redeploy without fixing the issue

---

## See Also

- [`../workflows/deploy_and_migrate.md`](deploy_and_migrate.md)
- [`../workflows/db_migrations.md`](db_migrations.md)
- [`../policy/PRODUCTION_POLICY.md`](../policy/PRODUCTION_POLICY.md)
