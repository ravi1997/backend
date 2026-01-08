# SKILL: Docker Hardening & Security

**Purpose:** Guide for agents to secure Docker environments.
**Source:** `skills/docker_hardening.md`

## 1. Secure Dockerfile Patterns
- **User instruction:** `RUN useradd -u 1001 myuser && USER myuser`.
- **Minimal packages:** Install only what is strictly necessary.
- **Scanning:** Use `docker scan` or `trivy` to find vulnerabilities.

## 2. Daemon Hardening
- **TLS:** Ensure the Docker daemon is only accessible via TLS.
- **Rootless mode:** Run the Docker daemon as a non-privileged user if possible.
- **User Remapping:** Use `userns-remap` to map container root to a non-privileged host user.

## 3. Runtime Security
- **No Privileged Containers:** Never use `--privileged` unless absolutely necessary.
- **Cap-drop:** Drop all capabilities and add back only what's needed: `--cap-drop=ALL --cap-add=NET_BIND_SERVICE`.
- **Resource Limits:** Always set `--memory` and `--cpus` to prevent DoS (Denial of Service) from a single container.

## 4. Secret Management
- **Mounting Secrets:** Use Docker Secrets or temporary volumes instead of environment variables for sensitive data.
- **File Permissions:** Ensure secrets mounted in `/run/secrets` have restrictive permissions.

## 5. Metadata for Agent
- `SKILL_TYPE`: SECURITY
- `FOCUS`: CONTAINERIZATION
- `TOOLS`: [trivy, hadolint, docker-bench-security]
