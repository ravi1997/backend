# Checklist: Nginx 502/504 Evidence Collection

**Purpose:** Collect diagnostic evidence for 502/504 gateway errors
**When to use:** Before attempting any fixes for Nginx upstream errors
**Prerequisites:** Access to server, logs, and service management
**Estimated time:** 5-10 minutes

---

## CRITICAL: Collect ALL Evidence Before Fixing

Do NOT skip any section. Incomplete evidence leads to wrong diagnosis.

---

## Section A: Nginx Configuration

### Commands to Run
```bash
# 1. Test nginx config
sudo nginx -t

# 2. Show relevant server block
sudo cat /etc/nginx/sites-available/myapp | grep -A 20 "server {"

# 3. Show upstream configuration
sudo cat /etc/nginx/sites-available/myapp | grep -A 10 "upstream"

# 4. Check timeout settings
sudo grep -r "timeout" /etc/nginx/sites-available/myapp
```

### Expected Information
- [ ] Nginx config is valid (nginx -t passes)
- [ ] Upstream address/port documented
- [ ] Proxy timeouts documented:
  - `proxy_connect_timeout`
  - `proxy_read_timeout`
  - `proxy_send_timeout`

### Red Flags
- ❌ nginx -t fails → Fix config first
- ❌ Upstream points to wrong port
- ❌ Very short timeouts (< 30s)

---

## Section B: Error Logs

### Commands to Run
```bash
# 1. Recent nginx errors (last 50 lines)
sudo tail -n 50 /var/log/nginx/error.log

# 2. Errors around specific time
sudo grep "502\|504" /var/log/nginx/error.log | tail -n 20

# 3. Access log for failing requests
sudo tail -n 100 /var/log/nginx/access.log | grep " 502 \| 504 "
```

### Expected Information
- [ ] Error message documented (exact text)
- [ ] Timestamp of errors
- [ ] Frequency (one-time vs continuous)
- [ ] Affected URLs/endpoints

### Common Error Patterns
- `connect() failed (111: Connection refused)` → Upstream not running
- `upstream timed out (110)` → Timeout issue
- `no live upstreams` → All backends down
- `recv() failed` → Connection broken mid-request

---

## Section C: Upstream Service Health

### For systemd Services
```bash
# 1. Service status
sudo systemctl status myapp.service

# 2. Recent logs
sudo journalctl -u myapp.service -n 200 --no-pager

# 3. Service is running?
ps aux | grep myapp
```

### For Docker Services
```bash
# 1. Container status
docker ps -a | grep myapp

# 2. Container logs
docker logs myapp --tail 200

# 3. Container restart count
docker inspect myapp | grep -i restart
```

### Expected Information
- [ ] Service state (active/inactive/failed)
- [ ] Process ID (if running)
- [ ] Recent log messages
- [ ] Any error messages or exceptions

### Red Flags
- ❌ Service is inactive/dead
- ❌ Service is restart looping
- ❌ Import errors in logs
- ❌ Port binding errors

---

## Section D: Application Server Details

### For Gunicorn
```bash
# 1. Check bind address
ps aux | grep gunicorn | grep -o "bind.*"

# 2. Check worker count
ps aux | grep gunicorn | wc -l

# 3. Check timeout setting
ps aux | grep gunicorn | grep -o "timeout.*"
```

### For uWSGI
```bash
# 1. Check socket
ps aux | grep uwsgi | grep -o "socket.*"

# 2. Check processes
ps aux | grep uwsgi
```

### Expected Information
- [ ] Bind address matches nginx upstream
  - Socket path: `/run/myapp.sock`
  - OR TCP: `127.0.0.1:8000`
- [ ] Workers are running (not just master)
- [ ] Timeout settings documented

### Red Flags
- ❌ Bind address mismatch (nginx → 8000, app → 8001)
- ❌ Socket file doesn't exist
- ❌ Socket has wrong permissions
- ❌ No workers running (only master process)
- ❌ Timeout too short for request duration

---

## Section E: Resource Checks

### Commands to Run
```bash
# 1. Memory status
free -h

# 2. Disk space
df -h

# 3. CPU and process list
top -b -n 1 | head -n 20

# 4. Check for OOM kills
sudo dmesg | grep -i "killed process"

# 5. Open file limits
ulimit -n
```

### Expected Information
- [ ] Available memory documented
- [ ] Disk space available (especially /tmp)
- [ ] CPU usage documented
- [ ] No recent OOM kills

### Red Flags
- ❌ Low memory (< 100MB available)
- ❌ Disk full (especially /)
- ❌ High CPU (> 90% sustained)
- ❌ OOM killer active
- ❌ Too many open files

---

## Section F: Network Connectivity

### Commands to Run
```bash
# 1. Test upstream connectivity
curl -I http://localhost:8000/healthz
# OR for socket
curl --unix-socket /run/myapp.sock http://localhost/healthz

# 2. Check port listening
sudo ss -tlnp | grep 8000
# OR
sudo netstat -tlnp | grep 8000

# 3. Check firewall
sudo iptables -L | grep 8000
```

### Expected Information
- [ ] Can connect to upstream directly
- [ ] Port is listening
- [ ] No firewall blocking

### Red Flags
- ❌ Cannot connect to upstream
- ❌ Port not listening
- ❌ Firewall blocking connection

---

## Section G: Recent Changes

### Questions to Answer
- [ ] What changed recently?
  - Code deployment?
  - Config change?
  - System update?
  - Traffic increase?
- [ ] When did the issue start?
- [ ] Is it affecting all requests or specific endpoints?
- [ ] Is it intermittent or constant?

---

## Section H: Common Root Causes Checklist

Based on evidence, check which applies:

- [ ] **Upstream not running** (systemctl shows inactive)
- [ ] **Import error** (Python module not found in logs)
- [ ] **Missing environment variable** (KeyError in logs)
- [ ] **Wrong socket path** (nginx → /run/app.sock, app → /tmp/app.sock)
- [ ] **Socket permission denied** (www-data can't access socket)
- [ ] **Port mismatch** (nginx → :8000, app → :8001)
- [ ] **Timeout too short** (request takes 60s, timeout is 30s)
- [ ] **Worker deadlock** (all workers busy, no new requests accepted)
- [ ] **OOM kill** (dmesg shows process killed)
- [ ] **Disk full** (can't write logs/temp files)

---

## Output Summary

After collecting all evidence, write a 10-line summary:

```
DIAGNOSIS SUMMARY
=================
Environment: [dev/staging/production]
Issue: [502 or 504]
Frequency: [constant/intermittent]
Affected: [all requests / specific endpoint]

Root Cause (most likely): [specific cause]
Evidence: [key evidence that points to this]

Recommended Fix: [specific action]
Risk Level: [low/medium/high]
```

---

## Validation

Before proceeding to fix:
- [ ] All sections A-H completed
- [ ] Root cause identified with confidence
- [ ] Evidence supports the diagnosis
- [ ] Fix is the smallest safe change

**If any checkbox is unchecked → Collect more evidence.**

---

## See Also

- [`../workflows/nginx_502_504.md`](../workflows/nginx_502_504.md) - Fix workflow
- [`../skills/nginx_gunicorn.md`](../skills/nginx_gunicorn.md) - Debugging guide
- [`../policy/PRODUCTION_POLICY.md`](../policy/PRODUCTION_POLICY.md) - Safety rules
