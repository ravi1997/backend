# Bug Fix Plan: ContainerConfig KeyError in docker compose v1

**Fix ID:** FIX-20260203-ContainerConfig
**Date:** 2026-02-03
**Status:** Planned
**Priority:** High

## Issue Description

The project experiences a `ContainerConfig` KeyError when using docker compose v1 (Python-based) to manage Docker containers. This error occurs when docker compose v1 attempts to access container image metadata, specifically the `ContainerConfig` key which may not be consistently available across different image versions or registry responses.

## Root Cause

- **docker compose v1 (Python-based)** has a known bug when accessing `ContainerConfig` key in container image metadata
- The Python implementation has issues parsing certain image metadata structures returned by Docker registries
- This affects the reliability of docker compose operations including build, up, down, logs, exec, and other commands

## Fix Plan

### Solution

Upgrade from docker compose v1 to docker compose v2 (Go-based) by using the `docker compose` command instead of `docker compose`.

docker compose v2 is a complete rewrite in Go that:

- Has better compatibility with modern Docker API responses
- Avoids the Python-based parsing issues
- Is the officially supported version by Docker

### Changes to be Made

#### Makefile Updates

Replace all `docker compose` commands with `docker compose` in [`Makefile`](../../Makefile):

| Line | Original | Changed To |
|------|----------|------------|
| 7 | `docker compose build` | `docker compose build` |
| 10 | `docker compose up -d` | `docker compose up -d` |
| 13 | `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d` | `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d` |
| 16 | `docker compose down` | `docker compose down` |
| 19 | `docker compose logs -f backend` | `docker compose logs -f backend` |
| 22 | `docker compose exec backend bash` | `docker compose exec backend bash` |
| 25 | `docker compose exec backend pytest` | `docker compose exec backend pytest` |
| 28 | `docker compose exec ollama ollama pull llama3` | `docker compose exec ollama ollama pull llama3` |
| 31 | `docker compose down -v` | `docker compose down -v` |

### Verification Steps

1. Verify docker compose v2 is installed: `docker compose version`
2. Test build: `make build`
3. Test up: `make up`
4. Test logs: `make logs`
5. Test exec: `make shell`
6. Test down: `make down`

## Rollback Plan

If issues occur with docker compose v2:

1. Revert Makefile changes to use `docker compose`
2. Consider installing docker compose v1 as a fallback: `pip install docker-compose==1.29.2`
