# Known Issue: ContainerConfig KeyError in docker compose v1

**Issue ID:** KI-20260203-ContainerConfig-KeyError
**Date Reported:** 2026-02-03
**Status:** Resolved
**Affected Version:** docker compose v1 (Python-based)

## Error Symptoms

When running docker compose commands (build, up, down, logs, exec, etc.), the following error may occur:

```
KeyError: 'ContainerConfig'
```

This error manifests when docker compose v1 attempts to access container image metadata from Docker registries or the local Docker daemon. The error typically occurs during:

- Building images with `docker compose build`
- Starting services with `docker compose up`
- Pulling images with `docker compose pull`
- Any command that requires parsing image metadata

## Root Cause

docker compose v1 is written in Python and uses a specific parsing mechanism to access container image metadata. The `ContainerConfig` key is not consistently present across:

- Different Docker image versions
- Images pushed to different registries
- Images built with different Docker versions

The Python implementation does not handle missing or renamed metadata keys gracefully, resulting in a `KeyError` exception.

## Fix Applied

**Solution:** Migrated from docker compose v1 (`docker compose` command) to docker compose v2 (`docker compose` command).

docker compose v2 is a complete rewrite in Go that:

- Has improved compatibility with modern Docker API responses
- Handles missing metadata keys gracefully
- Is the officially supported version by Docker

### Changes Made

Updated [`Makefile`](../../Makefile) to replace all `docker compose` commands with `docker compose`:

| Command | Before | After |
|---------|--------|-------|
| build | `docker compose build` | `docker compose build` |
| up | `docker compose up -d` | `docker compose up -d` |
| up-dev | `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d` | `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d` |
| down | `docker compose down` | `docker compose down` |
| logs | `docker compose logs -f backend` | `docker compose logs -f backend` |
| shell | `docker compose exec backend bash` | `docker compose exec backend bash` |
| test | `docker compose exec backend pytest` | `docker compose exec backend pytest` |
| pull-models | `docker compose exec ollama ollama pull llama3` | `docker compose exec ollama ollama pull llama3` |
| clean | `docker compose down -v` | `docker compose down -v` |

### Plan Reference

See [`plans/BugFixes/FIX-20260203-ContainerConfig.md`](../../plans/BugFixes/FIX-20260203-ContainerConfig.md) for detailed fix plan and verification steps.

## Alternative Workarounds

If docker compose v2 is not available or causes issues:

### Option 1: Install docker compose v2 via Docker Desktop

1. Install Docker Desktop (includes docker compose v2)
2. Or install Docker Compose v2 standalone: `mkdir -p ~/.docker/cli-plugins && curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose`

### Option 2: Pin to specific docker compose v1 version (Temporary)

```bash
pip install docker-compose==1.29.2
```

Note: This is a temporary workaround and does not resolve the underlying issue.

### Option 3: Rebuild affected images

Sometimes the issue is caused by corrupted image metadata. Rebuilding the image may help:

```bash
docker compose build --no-cache
```

## Verification

Verify the fix is working:

```bash
# Check docker compose version
docker compose version

# Run a test command
make build
```

## Related Links

- [Docker Compose v2 Release Notes](https://docs.docker.com/compose/release-notes/)
- [Docker Compose GitHub Repository](https://github.com/docker/compose)
- [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)
