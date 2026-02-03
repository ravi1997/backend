# Docker Diagnostics Bundle

## Purpose

Automated diagnostic commands to run when Docker issues occur. These commands gather evidence for troubleshooting.

---

## DIAG-DOCKER-001: Build Failure Diagnostics

### When to Run

- Docker build fails
- Need to understand build context and layer issues

### Commands

```bash
#!/bin/bash
echo "=== Docker Build Diagnostics ==="
echo ""

echo "1. Docker Version:"
docker --version
docker compose --version

echo ""
echo "2. Build Context Size:"
du -sh .
find . -type f | wc -l

echo ""
echo "3. Dockerfile Validation:"
if [ -f Dockerfile ]; then
  echo "✓ Dockerfile exists"
  echo "First 20 lines:"
  head -20 Dockerfile
else
  echo "✗ Dockerfile not found"
fi

echo ""
echo "4. .dockerignore Check:"
if [ -f .dockerignore ]; then
  echo "✓ .dockerignore exists"
  cat .dockerignore
else
  echo "⚠ .dockerignore missing (build context may be huge)"
fi

echo ""
echo "5. Base Image Check:"
grep "^FROM" Dockerfile | while read line; do
  image=$(echo $line | awk '{print $2}')
  echo "Checking: $image"
  docker pull $image 2>&1 | grep -E "Downloaded|up to date|Error"
done

echo ""
echo "6. Build with Verbose Output:"
DOCKER_BUILDKIT=0 docker build --progress=plain --no-cache . 2>&1 | tee build-diagnostic.log
echo "Full build log saved to: build-diagnostic.log"

echo ""
echo "7. Disk Space:"
df -h | grep -E "Filesystem|/var/lib/docker|/$"

echo ""
echo "8. Docker System Info:"
docker system df
```

### Output Files

- `build-diagnostic.log`: Full build output
- `docker-diagnostics.txt`: Summary of findings

---

## DIAG-DOCKER-002: Container Runtime Diagnostics

### When to Run

- Container exits immediately
- Container crashes
- Permission or environment issues

### Commands

```bash
#!/bin/bash
CONTAINER_ID=$1

if [ -z "$CONTAINER_ID" ]; then
  echo "Usage: $0 <container-id-or-name>"
  exit 1
fi

echo "=== Container Runtime Diagnostics for: $CONTAINER_ID ==="
echo ""

echo "1. Container Status:"
docker ps -a | grep $CONTAINER_ID

echo ""
echo "2. Container Logs (last 100 lines):"
docker logs --tail 100 $CONTAINER_ID

echo ""
echo "3. Container Inspect (State):"
docker inspect $CONTAINER_ID | jq '.[0].State'

echo ""
echo "4. Container Inspect (Config):"
docker inspect $CONTAINER_ID | jq '.[0].Config | {Cmd, Entrypoint, Env, User, WorkingDir}'

echo ""
echo "5. Container Inspect (Mounts):"
docker inspect $CONTAINER_ID | jq '.[0].Mounts'

echo ""
echo "6. Container Inspect (Networks):"
docker inspect $CONTAINER_ID | jq '.[0].NetworkSettings.Networks'

echo ""
echo "7. Container Processes (if running):"
docker top $CONTAINER_ID 2>/dev/null || echo "Container not running"

echo ""
echo "8. Container Resource Usage:"
docker stats --no-stream $CONTAINER_ID 2>/dev/null || echo "Container not running"

echo ""
echo "9. Try Interactive Shell:"
echo "Attempting to get shell access..."
docker exec -it $CONTAINER_ID sh -c "echo 'Shell access OK'; id; pwd; ls -la" 2>/dev/null || \
docker exec -it $CONTAINER_ID bash -c "echo 'Shell access OK'; id; pwd; ls -la" 2>/dev/null || \
echo "Cannot access shell (container may be stopped)"

echo ""
echo "10. Check File Permissions in Container:"
docker exec $CONTAINER_ID sh -c "ls -la / && ls -la /app" 2>/dev/null || echo "Cannot check (container not running)"

echo ""
echo "11. Check Environment Variables:"
docker exec $CONTAINER_ID env 2>/dev/null || echo "Cannot check (container not running)"

echo ""
echo "12. Healthcheck Status:"
docker inspect $CONTAINER_ID | jq '.[0].State.Health // "No healthcheck defined"'
```

---

## DIAG-DOCKER-003: Network Diagnostics

### When to Run

- Services can't communicate
- DNS resolution failures
- Connection refused errors

### Commands

```bash
#!/bin/bash
echo "=== Docker Network Diagnostics ==="
echo ""

echo "1. List All Networks:"
docker network ls

echo ""
echo "2. Inspect Each Network:"
for network in $(docker network ls --format "{{.Name}}"); do
  echo "--- Network: $network ---"
  docker network inspect $network | jq '.[0] | {Name, Driver, Containers}'
done

echo ""
echo "3. Container Network Attachments:"
for container in $(docker ps --format "{{.Names}}"); do
  echo "--- Container: $container ---"
  docker inspect $container | jq '.[0].NetworkSettings.Networks | keys'
done

echo ""
echo "4. DNS Resolution Test (from each running container):"
for container in $(docker ps --format "{{.Names}}"); do
  echo "--- From container: $container ---"
  for target in $(docker ps --format "{{.Names}}"); do
    if [ "$container" != "$target" ]; then
      echo -n "  Resolving $target: "
      docker exec $container nslookup $target 2>&1 | grep -q "Address" && echo "✓ OK" || echo "✗ FAILED"
    fi
  done
done

echo ""
echo "5. Connectivity Test (ping):"
for container in $(docker ps --format "{{.Names}}"); do
  echo "--- From container: $container ---"
  for target in $(docker ps --format "{{.Names}}"); do
    if [ "$container" != "$target" ]; then
      echo -n "  Ping $target: "
      docker exec $container ping -c 1 -W 2 $target 2>&1 | grep -q "1 received" && echo "✓ OK" || echo "✗ FAILED"
    fi
  done
done

echo ""
echo "6. Port Connectivity Test:"
echo "Checking if services are listening on expected ports..."
for container in $(docker ps --format "{{.Names}}"); do
  echo "--- Container: $container ---"
  docker exec $container netstat -tlnp 2>/dev/null || docker exec $container ss -tlnp 2>/dev/null || echo "  Cannot check (netstat/ss not available)"
done

echo ""
echo "7. Host Connectivity Test:"
echo "Testing connection to host.docker.internal..."
for container in $(docker ps --format "{{.Names}}"); do
  echo -n "  From $container: "
  docker exec $container ping -c 1 -W 2 host.docker.internal 2>&1 | grep -q "1 received" && echo "✓ OK" || echo "✗ FAILED"
done

echo ""
echo "8. External Connectivity Test:"
for container in $(docker ps --format "{{.Names}}"); do
  echo -n "  From $container to 8.8.8.8: "
  docker exec $container ping -c 1 -W 2 8.8.8.8 2>&1 | grep -q "1 received" && echo "✓ OK" || echo "✗ FAILED"
done
```

---

## DIAG-DOCKER-004: Volume and Permission Diagnostics

### When to Run

- Permission denied errors
- Files not persisting
- Volume mount issues

### Commands

```bash
#!/bin/bash
echo "=== Docker Volume & Permission Diagnostics ==="
echo ""

echo "1. List All Volumes:"
docker volume ls

echo ""
echo "2. Inspect Each Volume:"
for volume in $(docker volume ls --format "{{.Name}}"); do
  echo "--- Volume: $volume ---"
  docker volume inspect $volume
done

echo ""
echo "3. Container Mounts:"
for container in $(docker ps -a --format "{{.Names}}"); do
  echo "--- Container: $container ---"
  docker inspect $container | jq '.[0].Mounts[] | {Type, Source, Destination, Mode, RW}'
done

echo ""
echo "4. File Ownership in Containers:"
for container in $(docker ps --format "{{.Names}}"); do
  echo "--- Container: $container ---"
  echo "  User running as:"
  docker exec $container id
  echo "  /app ownership:"
  docker exec $container ls -la /app | head -20
done

echo ""
echo "5. Host Mount Point Ownership:"
echo "Checking ownership of common mount points..."
for dir in . ./data ./uploads ./logs ./node_modules ./venv; do
  if [ -d "$dir" ]; then
    echo "  $dir:"
    ls -la "$dir" | head -5
  fi
done

echo ""
echo "6. Volume Usage:"
for container in $(docker ps --format "{{.Names}}"); do
  echo "--- Container: $container ---"
  docker exec $container df -h 2>/dev/null || echo "  Cannot check (df not available)"
done

echo ""
echo "7. Write Test:"
for container in $(docker ps --format "{{.Names}}"); do
  echo -n "  $container write to /app: "
  docker exec $container sh -c "touch /app/write-test-$$; rm /app/write-test-$$" 2>&1 && echo "✓ OK" || echo "✗ FAILED (permission denied?)"
done
```

---

## DIAG-DOCKER-005: Image Analysis Diagnostics

### When to Run

- Image size too large
- Security scan needed
- Layer analysis required

### Commands

```bash
#!/bin/bash
IMAGE=$1

if [ -z "$IMAGE" ]; then
  echo "Usage: $0 <image-name>"
  exit 1
fi

echo "=== Image Analysis for: $IMAGE ==="
echo ""

echo "1. Image Size:"
docker images | grep $IMAGE

echo ""
echo "2. Image History (layer sizes):"
docker history $IMAGE --no-trunc --format "table {{.Size}}\t{{.CreatedBy}}" | head -30

echo ""
echo "3. Image Layers (sorted by size):"
docker history $IMAGE --no-trunc --format "{{.Size}}\t{{.CreatedBy}}" | sort -h | tail -20

echo ""
echo "4. Image Inspect:"
docker inspect $IMAGE | jq '.[0] | {Architecture, Os, Size, Config: {Cmd, Entrypoint, Env, User}}'

echo ""
echo "5. Security Scan (if available):"
if command -v trivy &> /dev/null; then
  echo "Running Trivy scan..."
  trivy image --severity HIGH,CRITICAL $IMAGE
elif command -v docker &> /dev/null && docker scan --help &> /dev/null; then
  echo "Running Docker scan..."
  docker scan $IMAGE
else
  echo "⚠ No security scanner available (install trivy or enable docker scan)"
fi

echo ""
echo "6. SBOM Generation (if syft available):"
if command -v syft &> /dev/null; then
  echo "Generating SBOM..."
  syft $IMAGE -o table
else
  echo "⚠ syft not available (install: https://github.com/anchore/syft)"
fi

echo ""
echo "7. Check for Secrets in Layers:"
echo "Searching for common secret patterns..."
docker save $IMAGE -o /tmp/image-$$.tar
tar -xf /tmp/image-$$.tar -C /tmp/image-$$
grep -r -i -E "(password|secret|api_key|token|private_key)" /tmp/image-$$ 2>/dev/null | head -20 || echo "No obvious secrets found"
rm -rf /tmp/image-$$ /tmp/image-$$.tar

echo ""
echo "8. Dive Analysis (if available):"
if command -v dive &> /dev/null; then
  echo "Run: dive $IMAGE"
  echo "(Interactive tool - run manually)"
else
  echo "⚠ dive not available (install: https://github.com/wagoodman/dive)"
fi
```

---

## DIAG-DOCKER-006: Compose Diagnostics

### When to Run

- docker compose issues
- Service dependency problems
- Configuration validation needed

### Commands

```bash
#!/bin/bash
echo "=== Docker Compose Diagnostics ==="
echo ""

echo "1. Compose Version:"
docker compose --version

echo ""
echo "2. Compose File Validation:"
docker compose config --quiet && echo "✓ Compose file is valid" || echo "✗ Compose file has errors"

echo ""
echo "3. Rendered Compose Configuration:"
docker compose config

echo ""
echo "4. Service Status:"
docker compose ps

echo ""
echo "5. Service Logs (last 50 lines each):"
for service in $(docker compose config --services); do
  echo "--- Service: $service ---"
  docker compose logs --tail 50 $service
done

echo ""
echo "6. Service Dependencies:"
docker compose config | grep -A 5 "depends_on:"

echo ""
echo "7. Service Healthchecks:"
docker compose config | grep -A 10 "healthcheck:"

echo ""
echo "8. Service Networks:"
docker compose config | grep -A 5 "networks:"

echo ""
echo "9. Service Volumes:"
docker compose config | grep -A 5 "volumes:"

echo ""
echo "10. Environment Variables:"
echo "Checking .env file..."
if [ -f .env ]; then
  echo "✓ .env exists"
  echo "Variables defined:"
  grep -v "^#" .env | grep -v "^$" | cut -d= -f1
else
  echo "⚠ .env file not found"
fi

echo ""
echo "11. Service Health Status:"
for container in $(docker compose ps -q); do
  name=$(docker inspect $container | jq -r '.[0].Name')
  health=$(docker inspect $container | jq -r '.[0].State.Health.Status // "no healthcheck"')
  echo "  $name: $health"
done
```

---

## DIAG-DOCKER-007: Performance Diagnostics

### When to Run

- Slow builds
- High resource usage
- Performance issues

### Commands

```bash
#!/bin/bash
echo "=== Docker Performance Diagnostics ==="
echo ""

echo "1. Docker System Info:"
docker system info

echo ""
echo "2. Disk Usage:"
docker system df -v

echo ""
echo "3. Running Container Stats:"
docker stats --no-stream

echo ""
echo "4. Build Cache Analysis:"
echo "Checking build cache usage..."
docker builder du

echo ""
echo "5. Image Layer Cache Test:"
echo "Building with cache..."
time docker build -t cache-test . 2>&1 | grep -E "CACHED|RUN|COPY"

echo ""
echo "6. Prune Recommendations:"
echo "Unused containers:"
docker ps -a --filter "status=exited" --format "{{.Names}}" | wc -l
echo "Dangling images:"
docker images -f "dangling=true" -q | wc -l
echo "Unused volumes:"
docker volume ls -f "dangling=true" -q | wc -l

echo ""
echo "7. Host System Resources:"
echo "CPU:"
top -bn1 | grep "Cpu(s)" | head -1
echo "Memory:"
free -h
echo "Disk:"
df -h | grep -E "Filesystem|/$"

echo ""
echo "8. Docker Daemon Logs (last 50 lines):"
sudo journalctl -u docker -n 50 --no-pager 2>/dev/null || echo "Cannot access daemon logs (need sudo)"
```

---

## DIAG-DOCKER-008: Security Diagnostics

### When to Run

- Security audit needed
- Compliance check
- Before production deployment

### Commands

```bash
#!/bin/bash
IMAGE=$1

if [ -z "$IMAGE" ]; then
  echo "Usage: $0 <image-name>"
  exit 1
fi

echo "=== Docker Security Diagnostics for: $IMAGE ==="
echo ""

echo "1. Check for Root User:"
user=$(docker inspect $IMAGE | jq -r '.[0].Config.User')
if [ -z "$user" ] || [ "$user" = "null" ]; then
  echo "⚠ WARNING: Image runs as root (no USER directive)"
else
  echo "✓ Image runs as user: $user"
fi

echo ""
echo "2. Check for :latest Tags:"
docker history $IMAGE --no-trunc | grep -i "FROM.*:latest" && echo "⚠ WARNING: Uses :latest tag" || echo "✓ No :latest tags found"

echo ""
echo "3. Vulnerability Scan:"
if command -v trivy &> /dev/null; then
  trivy image --severity HIGH,CRITICAL --format table $IMAGE
else
  echo "⚠ trivy not installed"
fi

echo ""
echo "4. Check for Secrets in Environment:"
docker inspect $IMAGE | jq '.[0].Config.Env[]' | grep -i -E "(password|secret|key|token)" && echo "⚠ WARNING: Possible secrets in ENV" || echo "✓ No obvious secrets in ENV"

echo ""
echo "5. Check for Exposed Ports:"
docker inspect $IMAGE | jq '.[0].Config.ExposedPorts'

echo ""
echo "6. Capabilities Check (running container):"
for container in $(docker ps --filter "ancestor=$IMAGE" --format "{{.Names}}"); do
  echo "Container: $container"
  docker inspect $container | jq '.[0].HostConfig.CapAdd // "default"'
  docker inspect $container | jq '.[0].HostConfig.Privileged'
done

echo ""
echo "7. Volume Mounts (check for sensitive paths):"
for container in $(docker ps --filter "ancestor=$IMAGE" --format "{{.Names}}"); do
  echo "Container: $container"
  docker inspect $container | jq '.[0].Mounts[] | select(.Source | contains("/etc") or contains("/var/run")) | {Source, Destination}'
done

echo ""
echo "8. Network Mode:"
for container in $(docker ps --filter "ancestor=$IMAGE" --format "{{.Names}}"); do
  echo "Container: $container"
  docker inspect $container | jq '.[0].HostConfig.NetworkMode'
done
```

---

## Quick Diagnostic Scripts

### Save these as executable scripts for fast diagnostics

**`docker-debug-build.sh`**

```bash
#!/bin/bash
# Quick build diagnostics
docker build --progress=plain --no-cache . 2>&1 | tee build-debug.log
echo "Build log saved to: build-debug.log"
```

**`docker-debug-container.sh`**

```bash
#!/bin/bash
# Quick container diagnostics
CONTAINER=${1:-$(docker ps -lq)}
docker logs $CONTAINER
docker inspect $CONTAINER | jq '.[0].State'
docker exec $CONTAINER env
```

**`docker-debug-network.sh`**

```bash
#!/bin/bash
# Quick network diagnostics
docker network ls
for c in $(docker ps --format "{{.Names}}"); do
  echo "=== $c ==="
  docker exec $c ping -c 1 -W 2 $(docker ps --format "{{.Names}}" | grep -v $c | head -1) 2>&1 | grep -E "1 received|failed"
done
```

**`docker-cleanup.sh`**

```bash
#!/bin/bash
# Safe cleanup
echo "Removing stopped containers..."
docker container prune -f
echo "Removing dangling images..."
docker image prune -f
echo "Removing unused volumes..."
docker volume prune -f
echo "Removing unused networks..."
docker network prune -f
docker system df
```

## Extended Cases (Add-On)

- Build context size: `docker buildx build --progress=plain . 2>&1 | head -n5` to see context size; `du -sh .` and inspect `.dockerignore`.
- BuildKit/secret support: `echo $DOCKER_BUILDKIT`; `cat /etc/docker/daemon.json 2>/dev/null | grep buildkit`; rerun with `DOCKER_BUILDKIT=1` if needed.
- Rootless vs rootful: `ps -ef | grep dockerd-rootless`; check mount permissions with `stat -c "%u:%g" <path>`; prefer named volumes on rootless.
- Filesystem/inode health: `df -h` and `df -i`; `docker system df -v` to spot cache bloat.
- Compose substitution: `docker compose config` to catch unresolved `${VAR}`; add `--env-file` when testing.
- Multi-arch manifests: `docker buildx imagetools inspect <image:tag>` to confirm per-arch digests.

## Related Files

- Hard Cases: `agent/15_tech_hard_cases/docker.md`
- Recovery: `agent/16_recovery_playbooks/docker_recovery.md`
- Caveats: `agent/17_caveats/docker_caveats.md`
