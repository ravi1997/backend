# Example: Incident Workflow

This example shows a complete incident handling workflow from start to finish.

## Scenario

**User reports:** "The website is showing 502 Bad Gateway errors"

---

## Step 1: Agent Reads Router

Agent reads `00_INDEX.md` and identifies this as:
- **Type:** Incident / error / outage
- **Trigger keyword:** "502"
- **Route to:** `flows/INCIDENT_TRIAGE.md`

---

## Step 2: Fill Incident Form

Agent fills `forms/INCIDENT_MIN.md`:

```markdown
1) App/Service name: eye-donation-pledge
2) ENV (dev/staging/production/unknown): production
3) Symptom (one line): Users seeing 502 Bad Gateway
4) Exact error text (copy/paste 3–10 lines):
   nginx: [error] 1234#1234: *5678 connect() failed (111: Connection refused) 
   while connecting to upstream, client: 192.168.1.100
5) When it started (time): 2026-01-05 10:30 UTC
6) Last change before issue (deploy/config/db/code/unknown): deploy 30 minutes ago
7) Impact (users affected?): All users, complete outage
8) Links (logs/Sentry/Grafana/CI) if any: /var/log/nginx/error.log
```

---

## Step 3: Collect Evidence

Agent runs `checklists/NGINX_502_EVIDENCE.md`:

### Commands executed:
```bash
# Check nginx status
systemctl status nginx
# Output: active (running)

# Check upstream (gunicorn) status
systemctl status eye-donation
# Output: inactive (dead)

# Check recent logs
journalctl -u eye-donation -n 50
# Output: 
# Jan 05 10:28:45 gunicorn[12345]: ModuleNotFoundError: No module named 'flask_limiter'
# Jan 05 10:28:45 systemd[1]: eye-donation.service: Main process exited, code=exited, status=1/FAILURE

# Check nginx upstream config
grep upstream /etc/nginx/sites-enabled/eye-donation
# Output: upstream backend { server 127.0.0.1:8000; }

# Test upstream directly
curl -I http://127.0.0.1:8000
# Output: curl: (7) Failed to connect to 127.0.0.1 port 8000: Connection refused
```

---

## Step 4: Root Cause Analysis

**Finding:**
- Nginx is running ✅
- Gunicorn (upstream) is NOT running ❌
- Error: `ModuleNotFoundError: No module named 'flask_limiter'`
- Timing: Started after recent deployment

**Root Cause:**
New dependency `flask_limiter` was added to code but not installed in production environment.

---

## Step 5: Execute Fix Workflow

Agent follows `workflows/nginx_502_504.md`:

### Fix Steps:

1. **Install missing dependency:**
```bash
# SSH to production server
ssh production-server

# Activate virtual environment
cd /opt/eye-donation
source venv/bin/activate

# Install missing package
pip install flask-limiter

# Verify installation
pip list | grep flask-limiter
# Output: flask-limiter 3.5.0
```

2. **Restart service:**
```bash
sudo systemctl restart eye-donation

# Verify service is running
systemctl status eye-donation
# Output: active (running)

# Check logs for errors
journalctl -u eye-donation -n 20
# Output: No errors, application started successfully
```

3. **Verify fix:**
```bash
# Test upstream directly
curl -I http://127.0.0.1:8000/healthz
# Output: HTTP/1.1 200 OK

# Test through nginx
curl -I https://eyepledge.example.com/healthz
# Output: HTTP/2 200
```

---

## Step 6: Quality Gates

Agent runs `gates/QUALITY_GATES.md`:

- ✅ Service is running
- ✅ Health endpoint returns 200
- ✅ No errors in logs (last 5 minutes)
- ✅ Users can access website

---

## Step 7: Generate Artifact

Agent creates `artifacts/incident_report.md`:

```markdown
# Incident Report

## Summary
- What happened? Website returned 502 errors due to missing Python dependency
- Impact (users/services): All users, complete outage for 15 minutes
- Start time / detection time: 2026-01-05 10:30 UTC
- End time / mitigation time: 2026-01-05 10:45 UTC

## Symptoms
- Errors observed: 502 Bad Gateway from nginx
- Key log lines:
  - nginx: connect() failed (111: Connection refused)
  - gunicorn: ModuleNotFoundError: No module named 'flask_limiter'
  - systemd: eye-donation.service: Main process exited, status=1/FAILURE

## Root Cause
- Technical root cause: Missing dependency `flask-limiter` in production environment
- Contributing factors: 
  - Dependency added in code but not in requirements.txt
  - No automated dependency check in deployment pipeline

## Mitigation
- Actions taken: 
  1. Installed flask-limiter via pip
  2. Restarted gunicorn service
- What restored service: Installing missing dependency

## Corrective Actions
- Code/config changes: 
  - Added flask-limiter to requirements.txt
  - Verified all dependencies are documented
- Tests added:
  - Added import test to verify all dependencies load
- Monitoring improvements:
  - Added alert for service restart failures

## Prevention
- Runbook updates:
  - Added dependency verification step to deployment checklist
- Alerts and dashboards:
  - Alert when systemd service fails to start
  - Dashboard showing service health status
```

---

## Step 8: Follow-up Actions

Agent recommends:

1. **Update deployment workflow:**
   - Add `pip install -r requirements.txt` to deployment checklist
   - Add automated dependency verification

2. **Add monitoring:**
   - Alert on systemd service failures
   - Monitor upstream connection health

3. **Update documentation:**
   - Document dependency management process
   - Add to deployment runbook

---

## Total Time

- **Detection to fix:** 15 minutes
- **User impact:** 15 minutes downtime
- **Agent autonomy:** 90% (only needed deployment credentials from user)

---

## Key Takeaways

1. **Evidence first:** Collected logs before attempting fix
2. **Root cause:** Identified exact missing dependency
3. **Verification:** Tested fix at multiple levels (upstream, nginx, public)
4. **Documentation:** Generated complete incident report
5. **Prevention:** Recommended process improvements
