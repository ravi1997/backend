# CHECKLIST: Docker Runtime Evidence

**Purpose:** Systematically collect evidence for container failures or misbehavior.
**Source:** `checklists/DOCKER_RUNTIME_EVIDENCE.md`

## 1. Container Status
- [ ] Record container state (`docker ps -a`)
- [ ] Check exit code (`docker inspect <container> --format='{{.State.ExitCode}}'`)
- [ ] Check restart count/history

## 2. Logs & Output
- [ ] Capture recent logs (`docker logs --tail 100 <container>`)
- [ ] Check for logs/errors during startup
- [ ] Verify if logs are being sent to a driver (syslog, journald, json-file)

## 3. Environment & Config
- [ ] Inspect environment variables (`docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' <container>`)
- [ ] Verify volume mounts and permissions (`docker inspect -f '{{index .Mounts}}' <container>`)
- [ ] Check networks and IP assignments

## 4. Resource Usage
- [ ] Check CPU/Memory stats (`docker stats --no-stream`)
- [ ] Look for OOM (Out Of Memory) kills in `dmesg` or `docker inspect`
- [ ] Verify disk space for the Docker root dir (`docker info` / `df -h`)

## 5. Network Connectivity
- [ ] Test port accessibility from host
- [ ] Check inter-container connectivity (if in a bridge/overlay network)
- [ ] Verify DNS resolution inside the container

## 6. Metadata for Agent
- [ ] `FLOW:DOCKER_TRIAGE`
- [ ] `HOST_OS`: [linux/macos/windows]
- [ ] `ORCHESTRATOR`: [none/compose/swarm/k8s]
