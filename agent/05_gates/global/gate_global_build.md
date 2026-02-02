# Gate: Global Build

## Purpose

Ensures that the project is in a "Deployable" state at all times.

## Explicit Pass/Fail Rubric

| Criterion | Methodology | Pass Threshold | Fail Trigger |
| --- | --- | --- | --- |
| **Clean Compilation** | `npm run build` / `cmake .. && make` | Success | Any compilation error |
| **Environment Parity** | `docker build .` (if Dockerfile exists) | Success | Build context failure |
| **Asset Integrity** | Check for missing images/CSS/static files | All assets load | 404 on required assets |
| **Schema Match** | `migration status` / `orm validate` | Up to date | Pending migrations |

## Verification Procedure

1. **Fresh Clone Test**: Attempt to build in a clean directory or container.
2. **Warning Audit**: Treat any "Warning" regarding missing chunks or deprecated paths as a failure during major releases.
3. **Entrypoint Check**: Verify `main` or `index` entrypoints function as expected.

## Related Files

- `agent/05_gates/global/gate_global_docker.md`
- `agent/11_rules/docker_rules.md`
