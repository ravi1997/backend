# POLICY: Docker & Container Usage

**Purpose:** Standardize Docker practices for security, performance, and maintainability.
**Source:** `agent/policy/DOCKER_POLICY.md`

## 1. Image Standards
- **Base Images:** Use minimal base images (e.g., `alpine`, `distroless`) where possible.
- **Tagging:** Never use `:latest` in production. Use semantic versions or git SHAs.
- **Multistage Builds:** Mandatory for all production-bound images to keep size small.

## 2. Security
- **Non-root user:** Containers MUST NOT run as `root`. Use `USER` instruction.
- **Secrets:** Never bake industry secrets (API keys, passwords) into images. Use env vars or secret managers.
- **Read-only Filesystem:** Set `--read-only` where possible.

## 3. Persistence & Data
- **Volumes:** Use named volumes for persistent data, never bind mounts to system-critical paths.
- **No data in images:** State MUST NOT be stored inside the container's writable layer.

## 4. Networking
- **Port mapping:** Only expose necessary ports. 
- **Internal Networks:** Use Docker user-defined networks for inter-container communication; avoid the default bridge.

## 5. Lifecycle Management
- **Healthchecks:** Production containers SHOULD have a `HEALTHCHECK` defined.
- **Logging:** Use the `json-file` or `syslog` driver with log rotation enabled.
- **Cleanup:** Unused volumes and dangling images should be pruned periodically.

## 6. Verification
Agents must verify compliance using `gates/DOCKER_GATE.md` (to be created) or manual inspection of `Dockerfile`.
