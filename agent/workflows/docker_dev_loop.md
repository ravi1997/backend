# Meta-Workflow: Docker Development Loop

**Purpose:** Debug Docker build and runtime issues across stacks.
**When to use:** Docker build fails, containers won't start, or development loop broken.
**Prerequisites:** Docker installed, stack identified.
**Type:** Universal Meta-Workflow

---

## Workflow Contract

| Attribute | Details |
| :--- | :--- |
| **Inputs** | `docker-compose.yml`, `PROJECT_FINGERPRINT` |
| **Outputs** | Working Docker environment |
| **Policy** | Containers must pass health checks |
| **Stop Conditions** | Docker daemon not running, disk full |

---

## Step 0: Context Detection

Identify stack to understand container expectations (e.g., JVM vs. Python runtime).

```bash
# Check fingerprint
cat agent/contracts/PROJECT_FINGERPRINT.md
```

### Stack Norms

- **Java:** Expect long startup times, high memory usage.
- **Python:** Expect fast reload, watch out for `__pycache__` mounts.
- **C++:** Expect compile steps in build stage.
- **Web:** Expect node_modules volume mounts.

### Decision Trace

> [!NOTE]
> Record the detected stack and specific container issues.

---

## Step 1: Diagnose (Universal)

1.  **Status:** `docker ps`
2.  **Logs:** `docker-compose logs`
3.  **Space:** `docker system df`

---

## Step 2: Stack-Specific Fixes

Depending on the stack detected in Step 0, apply specific fixes.

### Common Stack Issues

- **Java (Maven/Gradle):** Memory limit reached (OOM). Increase Docker memory.
- **Python (Pip):** Dependency conflict. Rebuild without cache.
- **Web (NPM):** Node versions mismatch. Check base image.

```bash
# General Rebuild (Safe)
docker-compose build --no-cache
```

---

## Step 3: Verify (Universal)

// turbo
```bash
# All containers running?
docker-compose ps

# Health endpoints?
curl http://localhost:8000/healthz (or equivalent)
```

---

## Completion Criteria

- ✅ All containers "Up"
- ✅ App responding
- ✅ No critical errors in logs
