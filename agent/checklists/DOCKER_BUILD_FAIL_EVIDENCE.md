# Checklist: Docker Build/Run Failure Evidence

**Purpose:** Collect diagnostic evidence for Docker build and runtime failures
**When to use:** When Docker build fails or containers won't start
**Prerequisites:** Docker access, docker-compose.yml
**Estimated time:** 5-10 minutes

---

## CRITICAL: Collect ALL Evidence Before Fixing

Do NOT skip any section. Incomplete evidence leads to wrong diagnosis.

---

## Section A: Build Failures

### Commands to Run
```bash
# 1. Full build output
docker-compose build 2>&1 | tee build.log
# OR
docker build -t myapp . 2>&1 | tee build.log

# 2. Last 50 lines of build output
tail -n 50 build.log

# 3. Check disk space
df -h

# 4. Check Docker disk usage
docker system df
```

### Expected Information
- [ ] Exact error message documented
- [ ] Which step failed (step number)
- [ ] Base image and tag
- [ ] Dockerfile section that failed

### Common Build Errors
- `no space left on device` → Disk full
- `failed to fetch` → Network issue
- `unable to find image` → Wrong base image
- `COPY failed` → File doesn't exist
- `RUN returned non-zero` → Command failed

---

## Section B: Dockerfile Analysis

### Commands to Run
```bash
# 1. Show Dockerfile
cat Dockerfile

# 2. Show docker-compose.yml
cat docker-compose.yml

# 3. Check if files exist
ls -la requirements.txt package.json
# (whatever is being COPY'd)
```

### Expected Information
- [ ] Base image documented (FROM line)
- [ ] Files being COPY'd exist
- [ ] Build context is correct
- [ ] No syntax errors

### Red Flags
- ❌ COPY file that doesn't exist
- ❌ RUN command with hardcoded paths
- ❌ Missing .dockerignore (copying too much)
- ❌ Using :latest tag (unstable)

---

## Section C: Runtime Failures

### Commands to Run
```bash
# 1. Container status
docker ps -a

# 2. Container logs
docker logs myapp --tail 200

# 3. Container inspect
docker inspect myapp | grep -A 10 "State"

# 4. Check exit code
docker inspect myapp | grep ExitCode
```

### Expected Information
- [ ] Container state (running/exited/restarting)
- [ ] Exit code (if exited)
- [ ] Error messages in logs
- [ ] Restart count

### Common Runtime Errors
- Exit code 1 → Application error
- Exit code 137 → OOM killed
- Exit code 139 → Segmentation fault
- Exit code 255 → Container error

---

## Section D: Port and Volume Issues

### Commands to Run
```bash
# 1. Check port conflicts
sudo ss -tlnp | grep 8000
# OR
sudo netstat -tlnp | grep 8000

# 2. Check volume mounts
docker inspect myapp | grep -A 20 "Mounts"

# 3. Check volume permissions
docker exec myapp ls -la /app

# 4. Check bind mounts exist
ls -la ./data ./logs
```

### Expected Information
- [ ] Ports are available (not in use)
- [ ] Volumes are mounted correctly
- [ ] Permissions are correct
- [ ] Bind mount paths exist on host

### Red Flags
- ❌ Port already in use
- ❌ Volume mount failed
- ❌ Permission denied in container
- ❌ Bind mount path doesn't exist

---

## Section E: Network Issues

### Commands to Run
```bash
# 1. Check networks
docker network ls

# 2. Inspect network
docker network inspect myapp_default

# 3. Test connectivity between containers
docker exec myapp ping db
docker exec myapp curl http://db:5432
```

### Expected Information
- [ ] Network exists
- [ ] Containers are on same network
- [ ] DNS resolution works
- [ ] Containers can communicate

### Red Flags
- ❌ Network doesn't exist
- ❌ Container not connected to network
- ❌ DNS not resolving
- ❌ Cannot reach other containers

---

## Section F: Environment and Secrets

### Commands to Run
```bash
# 1. Check environment variables
docker exec myapp env

# 2. Check .env file
cat .env

# 3. Check docker-compose env
docker-compose config | grep -A 10 "environment"
```

### Expected Information
- [ ] Required env vars are set
- [ ] .env file exists (if used)
- [ ] No secrets in logs
- [ ] Env vars match expected

### Red Flags
- ❌ Missing required env var
- ❌ .env file not found
- ❌ Secrets in docker-compose.yml
- ❌ Wrong env var values

---

## Section G: Resource Constraints

### Commands to Run
```bash
# 1. Check container resources
docker stats --no-stream myapp

# 2. Check Docker daemon resources
docker system info | grep -A 10 "Memory"

# 3. Check host resources
free -h
df -h
```

### Expected Information
- [ ] Container memory limit
- [ ] Container CPU limit
- [ ] Host has available resources
- [ ] No resource exhaustion

### Red Flags
- ❌ Container hitting memory limit
- ❌ Host out of memory
- ❌ Host disk full
- ❌ Too many containers running

---

## Section H: Recent Changes

### Questions to Answer
- [ ] What changed since last successful build?
  - Dockerfile modified?
  - Dependencies updated?
  - Base image changed?
  - docker-compose.yml modified?
- [ ] Did it ever work?
- [ ] Does it work on another machine?

---

## Section I: Common Root Causes Checklist

Based on evidence, check which applies:

- [ ] **Disk full** (no space left on device)
- [ ] **Network timeout** (can't fetch dependencies)
- [ ] **Missing file** (COPY file that doesn't exist)
- [ ] **Wrong base image** (image not found)
- [ ] **Port conflict** (port already in use)
- [ ] **Volume permission** (can't write to mounted volume)
- [ ] **Missing env var** (application crashes on start)
- [ ] **OOM** (container killed for using too much memory)
- [ ] **Network issue** (can't reach other containers)
- [ ] **Syntax error** (in Dockerfile or docker-compose.yml)

---

## Output Summary

After collecting all evidence, write a 10-line summary:

```
DIAGNOSIS SUMMARY
=================
Issue Type: [build failure / runtime failure]
Error: [exact error message]
Failed At: [build step X / container start / runtime]

Root Cause (most likely): [specific cause]
Evidence: [key evidence]

Recommended Fix: [specific action]
Estimated Time: [minutes]
Risk Level: [low/medium/high]
```

---

## Validation

Before proceeding to fix:
- [ ] All sections A-I completed
- [ ] Root cause identified
- [ ] Evidence supports diagnosis
- [ ] Fix is clear

**If any checkbox is unchecked → Collect more evidence.**

---

## See Also

- [`../workflows/docker_dev_loop.md`](../workflows/docker_dev_loop.md) - Fix workflow
- [`../skills/docker_compose_debug.md`](../skills/docker_compose_debug.md) - Debugging guide
