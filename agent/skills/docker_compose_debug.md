# Skill: Docker Compose Debugging

**Purpose:** Debug Docker Compose issues
**When to use:** When docker-compose commands fail or containers won't start
**Prerequisites:** Docker and docker-compose installed
**Estimated time:** 15-30 minutes

---

## Common Issues and Fixes

### Issue 1: Service Won't Start

**Symptoms:** Container exits immediately or restarts continuously

**Diagnosis:**
```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs service-name

# Check exit code
docker inspect container-name | grep ExitCode
```

**Common Causes:**
- Missing environment variables
- Port conflicts
- Volume mount issues
- Command fails immediately

**Fixes:**
```bash
# Check env vars
docker-compose config

# Check ports
ss -tlnp | grep PORT

# Fix permissions
sudo chown -R $USER:$USER ./volumes
```

---

### Issue 2: Build Failures

**Symptoms:** `docker-compose build` fails

**Diagnosis:**
```bash
# Build with verbose output
docker-compose build --no-cache --progress=plain

# Check disk space
df -h
docker system df
```

**Common Causes:**
- Disk full
- Network timeout
- Invalid Dockerfile
- Missing files

**Fixes:**
```bash
# Clean up
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

---

### Issue 3: Network Issues

**Symptoms:** Services can't communicate

**Diagnosis:**
```bash
# List networks
docker network ls

# Inspect network
docker network inspect network-name

# Test connectivity
docker-compose exec service1 ping service2
```

**Fixes:**
```bash
# Recreate network
docker-compose down
docker-compose up -d
```

---

### Issue 4: Volume Issues

**Symptoms:** Data not persisting or permission errors

**Diagnosis:**
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect volume-name

# Check permissions
docker-compose exec service ls -la /mount/path
```

**Fixes:**
```bash
# Fix ownership
docker-compose exec service chown -R appuser:appuser /mount/path

# Or recreate volume
docker-compose down -v
docker-compose up -d
```

---

## Quick Troubleshooting Checklist

- [ ] Check logs: `docker-compose logs`
- [ ] Check status: `docker-compose ps`
- [ ] Check config: `docker-compose config`
- [ ] Check disk space: `df -h`
- [ ] Check networks: `docker network ls`
- [ ] Check volumes: `docker volume ls`
- [ ] Restart: `docker-compose restart`
- [ ] Rebuild: `docker-compose up -d --build`
- [ ] Clean start: `docker-compose down && docker-compose up -d`

---

## See Also

- [`../workflows/docker_dev_loop.md`](../workflows/docker_dev_loop.md)
- [`../checklists/DOCKER_BUILD_FAIL_EVIDENCE.md`](../checklists/DOCKER_BUILD_FAIL_EVIDENCE.md)
