# Workflow: systemd Service Failures

**Purpose:** Debug and fix systemd service failures
**When to use:** When a systemd service won't start, keeps restarting, or shows as failed
**Prerequisites:** SSH access, sudo privileges, service name
**Estimated time:** 10-20 minutes
**Outputs:** Running service, incident report (if production)

---

## Prerequisites

Before starting, verify:
- [ ] You have SSH access to the server
- [ ] You have sudo privileges
- [ ] You know the service name (check `01_PROJECT_CONTEXT.md`)
- [ ] Environment is detected (use `policy/ENV_DETECTION.md`)
- [ ] If production → follow `policy/PRODUCTION_POLICY.md`

**If any prerequisite is not met → STOP and resolve it first.**

---

## Step 1: Collect Evidence

Run the evidence checklist.

### Commands
```bash
# Check service status
sudo systemctl status myapp.service

# Check recent logs
sudo journalctl -u myapp.service -n 100 --no-pager

# Check service file
systemctl cat myapp.service
```

### Expected Information
- Service state (active/inactive/failed)
- Exit code and signal
- Recent log messages
- Service configuration

### If This Step Fails
- **Service not found?** → Check service name in `01_PROJECT_CONTEXT.md`
- **Permission denied?** → Use `sudo`
- **No logs?** → Service may have never started

---

## Step 2: Identify Failure Mode

Common failure patterns:

### A) Exit Code 203 (EXEC)
**Symptom:** `code=exited, status=203/EXEC`

**Root Cause:** Cannot execute the binary/script

**Diagnosis:**
```bash
# Check if file exists
ls -la /path/to/executable

# Check permissions
ls -la /path/to/executable
# Should be executable: -rwxr-xr-x
```

**Fix:**
```bash
# Make executable
sudo chmod +x /path/to/executable

# Or fix path in service file
sudo systemctl edit myapp.service
```

---

### B) Exit Code 1 (General Error)
**Symptom:** `code=exited, status=1`

**Root Cause:** Application error (import, config, dependency)

**Diagnosis:**
```bash
# Check application logs
sudo journalctl -u myapp.service -n 50

# Look for:
# - ImportError / ModuleNotFoundError
# - Configuration errors
# - Missing environment variables
# - Database connection errors
```

**Fix:** Address the specific error found in logs

---

### C) Exit Code 2 (Missing File)
**Symptom:** `code=exited, status=2`

**Root Cause:** Missing configuration file or dependency

**Diagnosis:**
```bash
# Check working directory
systemctl cat myapp.service | grep WorkingDirectory

# Check if files exist
ls -la /path/to/workdir
```

**Fix:** Create missing files or fix paths

---

### D) Restart Loop
**Symptom:** Service keeps restarting

**Root Cause:** Crashes immediately after start

**Diagnosis:**
```bash
# Watch logs in real-time
sudo journalctl -u myapp.service -f

# Check restart policy
systemctl cat myapp.service | grep Restart
```

**Fix:** Fix the crash cause, or adjust restart policy

---

### E) Permission Denied
**Symptom:** Permission errors in logs

**Root Cause:** Wrong user/group or file permissions

**Diagnosis:**
```bash
# Check service user
systemctl cat myapp.service | grep User

# Check file ownership
ls -la /path/to/app
```

**Fix:**
```bash
# Fix ownership
sudo chown -R myuser:mygroup /path/to/app

# Or change service user
sudo systemctl edit myapp.service
```

---

## Step 3: Apply the Fix

Based on the failure mode, apply the fix.

### For Dev/Staging
```bash
# 1. Make the fix (see above)

# 2. Reload systemd if service file changed
sudo systemctl daemon-reload

# 3. Restart service
sudo systemctl restart myapp.service

# 4. Check status
sudo systemctl status myapp.service
```

### For Production
Provide commands for user to run:
```markdown
I've identified the issue: [ISSUE]

Please run:
1. sudo systemctl daemon-reload
2. sudo systemctl restart myapp.service
3. sudo systemctl status myapp.service
```

---

## Step 4: Verify the Fix

Confirm service is running correctly.

### Verification Commands
```bash
# 1. Check service status
sudo systemctl status myapp.service
# Expected: active (running)

# 2. Check if process is running
ps aux | grep myapp
# Expected: Process found

# 3. Test application
curl -I http://localhost:8000/healthz
# Expected: HTTP 200 OK

# 4. Monitor logs
sudo journalctl -u myapp.service -f
# Expected: No errors, normal operation

# 5. Wait 2-3 minutes
# Expected: Service stays running
```

---

## Completion Criteria

This workflow is complete when:
- ✅ Service status shows `active (running)`
- ✅ No error messages in logs
- ✅ Application responds to health checks
- ✅ Service stays running for 2-3 minutes
- ✅ Incident report created (if production)

**Do NOT mark complete until all criteria are met.**

---

## Rollback Plan

If fix causes new issues:
```bash
# 1. Stop service
sudo systemctl stop myapp.service

# 2. Revert changes
# (restore backup of service file or code)

# 3. Reload and restart
sudo systemctl daemon-reload
sudo systemctl start myapp.service
```

---

## Common Mistakes to Avoid

❌ **Don't** restart without checking logs first
❌ **Don't** edit service files without `daemon-reload`
❌ **Don't** ignore permission errors
❌ **Don't** use `kill -9` - use `systemctl stop`

---

## See Also

- [`../checklists/SYSTEMD_FAIL_EVIDENCE.md`](../checklists/SYSTEMD_FAIL_EVIDENCE.md)
- [`../workflows/nginx_502_504.md`](nginx_502_504.md) - If related to web server
- [`../policy/PRODUCTION_POLICY.md`](../policy/PRODUCTION_POLICY.md)
