# Artifact: Runbook

**Purpose:** Document operational procedures for running services
**When to use:** For any repeatable operational task
**Audience:** Operations team, on-call engineers

---

## Runbook Template

```markdown
# Runbook: [Service/Task Name]

**Service:** [service name]  
**Owner:** [team/person]  
**Last Updated:** [date]  
**Frequency:** [daily/weekly/as-needed]

---

## Overview

**Purpose:** [What this runbook covers]  
**When to use:** [Specific situations]  
**Prerequisites:** [What you need before starting]

---

## Quick Reference

| Task | Command | Expected Time |
|------|---------|---------------|
| Start service | `systemctl start myapp` | 30s |
| Stop service | `systemctl stop myapp` | 10s |
| Check status | `systemctl status myapp` | 5s |
| View logs | `journalctl -u myapp -f` | - |
| Restart | `systemctl restart myapp` | 40s |

---

## Detailed Procedures

### Procedure 1: [Task Name]

**When:** [When to perform this]  
**Frequency:** [How often]  
**Duration:** [How long it takes]

#### Prerequisites
- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]

#### Steps
1. **[Step 1 name]**
   ```bash
   command here
   ```
   **Expected output:**
   ```
   expected output here
   ```

2. **[Step 2 name]**
   ```bash
   command here
   ```
   **Expected output:**
   ```
   expected output here
   ```

#### Verification
- [ ] [How to verify step 1]
- [ ] [How to verify step 2]

#### Rollback
If something goes wrong:
```bash
rollback command here
```

---

### Procedure 2: [Another Task]

[Same structure as above]

---

## Troubleshooting

### Issue: [Common Problem]

**Symptoms:** [What you see]  
**Cause:** [Why it happens]  
**Fix:**
```bash
fix command here
```

### Issue: [Another Problem]

[Same structure]

---

## Monitoring & Alerts

### Key Metrics
- **Metric 1:** [What to monitor]
  - Normal range: [X-Y]
  - Alert threshold: [Z]
  - Dashboard: [link]

- **Metric 2:** [What to monitor]
  - Normal range: [X-Y]
  - Alert threshold: [Z]
  - Dashboard: [link]

### Alert Responses

#### Alert: [Alert Name]
**Severity:** [P1/P2/P3/P4]  
**Meaning:** [What this alert means]  
**Action:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| Primary On-Call | [name] | [phone/slack] |
| Secondary On-Call | [name] | [phone/slack] |
| Team Lead | [name] | [phone/slack] |
| Manager | [name] | [phone/slack] |

---

## Related Documentation

- [Architecture Diagram](link)
- [API Documentation](link)
- [Deployment Guide](link)
- [Incident Response](link)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2024-01-01 | Initial version | [name] |
| 2024-01-15 | Added troubleshooting | [name] |
```

---

## Example: Web Service Runbook

```markdown
# Runbook: MyApp Web Service

**Service:** myapp-web  
**Owner:** Platform Team  
**Last Updated:** 2024-01-05  
**Frequency:** As needed

---

## Overview

**Purpose:** Operational procedures for myapp web service  
**When to use:** Service management, troubleshooting, deployments  
**Prerequisites:** SSH access, sudo privileges

---

## Quick Reference

| Task | Command | Expected Time |
|------|---------|---------------|
| Start | `sudo systemctl start myapp` | 30s |
| Stop | `sudo systemctl stop myapp` | 10s |
| Restart | `sudo systemctl restart myapp` | 40s |
| Status | `sudo systemctl status myapp` | 5s |
| Logs | `sudo journalctl -u myapp -f` | - |
| Deploy | `./deploy.sh production` | 5min |

---

## Detailed Procedures

### Deployment

**When:** New version release  
**Frequency:** Weekly  
**Duration:** 5-10 minutes

#### Prerequisites
- [ ] Code reviewed and merged
- [ ] Tests passing
- [ ] Staging deployment successful
- [ ] Backup created

#### Steps
1. **Pull latest code**
   ```bash
   cd /opt/myapp
   git pull origin main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

4. **Restart service**
   ```bash
   sudo systemctl restart myapp
   ```

5. **Verify**
   ```bash
   curl -I https://myapp.com/healthz
   # Expected: HTTP 200 OK
   ```

#### Rollback
```bash
git checkout <previous-tag>
pip install -r requirements.txt
alembic downgrade -1
sudo systemctl restart myapp
```

---

## Troubleshooting

### Issue: Service Won't Start

**Symptoms:** `systemctl status` shows failed  
**Cause:** Usually import error or missing dependency  
**Fix:**
```bash
# Check logs
sudo journalctl -u myapp -n 50

# Common fixes
pip install -r requirements.txt
sudo systemctl restart myapp
```

---

## Monitoring

### Key Metrics
- **Response Time:** Normal: <200ms, Alert: >1s
- **Error Rate:** Normal: <1%, Alert: >5%
- **CPU Usage:** Normal: <50%, Alert: >80%

---

## Emergency Contacts

| Role | Contact |
|------|---------|
| On-Call | #oncall-platform |
| Team Lead | @john-doe |
```

---

## See Also

- [`incident_report.md`](incident_report.md) - For incidents
- [`../workflows/deploy_and_migrate.md`](../workflows/deploy_and_migrate.md) - Deployment workflow
- [`../workflows/rollback_recovery.md`](../workflows/rollback_recovery.md) - Rollback procedures
