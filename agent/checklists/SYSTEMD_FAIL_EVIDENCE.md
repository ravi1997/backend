# Checklist: systemd Service Failure Evidence

**Purpose:** Collect diagnostic evidence for systemd service failures
**When to use:** When a systemd service won't start, keeps failing, or is restarting
**Prerequisites:** SSH access, sudo privileges, service name
**Estimated time:** 5-10 minutes

---

## CRITICAL: Collect ALL Evidence Before Fixing

Do NOT skip any section. Incomplete evidence leads to wrong diagnosis.

---

## Section A: Service Status

### Commands to Run
```bash
# 1. Current status
sudo systemctl status myapp.service

# 2. Service file location
systemctl cat myapp.service

# 3. Check if enabled
systemctl is-enabled myapp.service

# 4. Check dependencies
systemctl list-dependencies myapp.service
```

### Expected Information
- [ ] Service state (active/inactive/failed)
- [ ] Exit code and signal
- [ ] Service file path
- [ ] Whether service is enabled

### Common States
- `active (running)` → Service is working
- `inactive (dead)` → Service stopped
- `failed` → Service crashed
- `activating (auto-restart)` → Restart loop

---

## Section B: Service Logs

### Commands to Run
```bash
# 1. Recent logs (last 100 lines)
sudo journalctl -u myapp.service -n 100 --no-pager

# 2. Logs since last boot
sudo journalctl -u myapp.service -b

# 3. Follow logs in real-time
sudo journalctl -u myapp.service -f
# (Ctrl+C to stop)

# 4. Logs with timestamps
sudo journalctl -u myapp.service -n 50 --no-pager -o short-precise
```

### Expected Information
- [ ] Error messages documented
- [ ] Stack traces (if any)
- [ ] Exit codes
- [ ] Restart attempts

### Common Error Patterns
- `code=exited, status=203/EXEC` → Can't execute binary
- `code=exited, status=1` → Application error
- `code=exited, status=2` → Missing file
- `code=killed, signal=KILL` → OOM killed
- `Permission denied` → Permission issue

---

## Section C: Service Configuration

### Commands to Run
```bash
# 1. Show full service file
systemctl cat myapp.service

# 2. Check for overrides
systemctl cat myapp.service | grep -A 5 "drop-in"

# 3. Validate service file
systemd-analyze verify myapp.service
```

### Expected Information
- [ ] ExecStart command documented
- [ ] User/Group documented
- [ ] WorkingDirectory documented
- [ ] Environment variables documented
- [ ] Restart policy documented

### Red Flags
- ❌ ExecStart points to non-existent file
- ❌ WorkingDirectory doesn't exist
- ❌ User doesn't exist
- ❌ Missing required Environment variables

---

## Section D: Executable and Permissions

### Commands to Run
```bash
# 1. Check if executable exists
ls -la /path/to/executable

# 2. Check if executable
file /path/to/executable

# 3. Test execution manually
/path/to/executable --version
# OR
sudo -u serviceuser /path/to/executable --version

# 4. Check working directory
ls -la /path/to/workdir
```

### Expected Information
- [ ] Executable exists
- [ ] Executable has execute permission
- [ ] Working directory exists
- [ ] Service user can access files

### Red Flags
- ❌ File not found
- ❌ Not executable (-rw-r--r--)
- ❌ Wrong ownership
- ❌ Service user can't read/execute

---

## Section E: Dependencies and Environment

### Commands to Run
```bash
# 1. Check Python dependencies (if Python app)
sudo -u serviceuser python3 -c "import mymodule"

# 2. Check environment variables
systemctl show myapp.service | grep Environment

# 3. Check if ports are available
sudo ss -tlnp | grep 8000

# 4. Check database connectivity (if applicable)
sudo -u serviceuser psql -h localhost -U dbuser -c "SELECT 1"
```

### Expected Information
- [ ] All dependencies installed
- [ ] Environment variables set
- [ ] Required ports available
- [ ] External services reachable

### Red Flags
- ❌ ImportError / ModuleNotFoundError
- ❌ Missing environment variable
- ❌ Port already in use
- ❌ Can't connect to database

---

## Section F: Resource Checks

### Commands to Run
```bash
# 1. Check memory
free -h

# 2. Check disk space
df -h

# 3. Check for OOM kills
sudo dmesg | grep -i "killed process" | grep myapp

# 4. Check file descriptor limits
cat /proc/$(pgrep -f myapp)/limits | grep "open files"
```

### Expected Information
- [ ] Available memory
- [ ] Available disk space
- [ ] No recent OOM kills
- [ ] File descriptor limits

### Red Flags
- ❌ Low memory (< 100MB)
- ❌ Disk full
- ❌ OOM killer active
- ❌ Too many open files

---

## Section G: Recent Changes

### Questions to Answer
- [ ] What changed recently?
  - Code update?
  - Config change?
  - System update?
  - Service file modified?
- [ ] When did it last work?
- [ ] Did it ever work on this system?

---

## Section H: Common Root Causes Checklist

Based on evidence, check which applies:

- [ ] **Executable not found** (ExecStart path wrong)
- [ ] **Not executable** (missing +x permission)
- [ ] **Permission denied** (wrong user/group)
- [ ] **Missing dependency** (ImportError in logs)
- [ ] **Missing env var** (KeyError in logs)
- [ ] **Port in use** (bind: address already in use)
- [ ] **Working directory missing** (chdir failed)
- [ ] **Database unreachable** (connection refused)
- [ ] **OOM killed** (signal=KILL in dmesg)
- [ ] **Config error** (syntax error in app config)

---

## Output Summary

After collecting all evidence, write a 10-line summary:

```
DIAGNOSIS SUMMARY
=================
Service: myapp.service
State: [failed/inactive/restart-loop]
Exit Code: [code and signal]

Root Cause (most likely): [specific cause]
Evidence: [key evidence]

Recommended Fix: [specific action]
Estimated Time: [minutes]
Risk Level: [low/medium/high]
```

---

## Validation

Before proceeding to fix:
- [ ] All sections A-H completed
- [ ] Root cause identified
- [ ] Evidence supports diagnosis
- [ ] Fix is clear

**If any checkbox is unchecked → Collect more evidence.**

---

## See Also

- [`../workflows/systemd_failures.md`](../workflows/systemd_failures.md) - Fix workflow
- [`../policy/PRODUCTION_POLICY.md`](../policy/PRODUCTION_POLICY.md) - Safety rules
