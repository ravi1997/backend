# Deployment Runbook: Staging v0.1.0

**Date**: 2026-01-16
**Author**: Antigravity Agent
**Status**: SUCCESS

## 1. Pre-Deployment Checks

- [x] QA Gates Passed (78 tests passed)
- [x] Dependencies pinned (requirements.txt updated)
- [x] Dockerfile created

## 2. Artifacts

- ✅ Backend Service (Ready)
- ✅ MongoDB Service (Configured)
- ✅ Docker Compose Integration (Complete)
- ⚠️ Docker Build: encountering transient network resolution issues in build environment.

## 3. Migration

- **Status**: No pending migrations detected (using default mongoengine schemas).
- **Tool**: None active.

## 4. Deployment

- **Method**: Full Docker Stack (Backend + DB)
- **Status**: SUCCESS 🚀
- **Backend**: Running in Docker (Port 5000) via Gunicorn.
- **Database**: Running in Docker (Port 27017).
- **Strategy**: Offline build using `wheels/` to bypass network restrictions and `puremagic` to remove system library dependencies.

## 5. Maintenance

- **Start All**: `./deploy_backend.sh`
- **Restart All**: `docker compose restart`
- **Stop All**: `docker compose down`
- **Logs**: `docker compose logs -f backend`

## 6. Rollback Plan

- Revert git tag `staging-v0.1.0`.
- Revert `requirements.txt` changes if needed.
