# Workflow: Repo Audit and Baseline

## Purpose

Verify the health of an existing project before making changes.

## Inputs

- Existing project files.

## Procedure

1. **Token Risk Check**: Assess budget per `agent/00_system/12_token_budget_and_model_switching.md`. If scanning a large repo, enable continuity snapshots.
2. **Adopt Profile**: `profile_tester.md`.
3. **Build Test**: Attempt to build the project.
4. **Test Run**: Execute existing tests.
5. **Code Quality**: Run linters if available.
6. **Docker Validation**: If Dockerfile exists, run `docker build` to verify it works. If docker-compose.yml exists, run `docker compose config` to validate syntax.
7. **CI/CD Check**: If `.github/workflows/` exists, validate workflow syntax using `actionlint` or manual review. Check if workflows are up-to-date with current build/test commands.
8. **Container Security Scan**: If Docker is present, check for pinned base images, non-root user, and absence of secrets in Dockerfile.
9. **Git Snapshot**: Record current HEAD hash in `PROJECT_STATE.md`.
10. **Report Card**: Create `plans/Architecture/BASELINE_REPORT.md` noting existing bugs/debt, Docker status, and CI/CD status.

## STOP Condition

- Baseline report is saved.

## Required Gates

- **Build Pass**: Build must succeed (or documented as broken).
- **Audit Complete**: `BASELINE_REPORT.md` exists.

## State Update

- Update `agent/09_state/PROJECT_STATE.md`:
  - Set `last_audit_date` to current date.
  - Set `known_issues_count` based on findings.

## Related Files

- `agent/02_detection/detect_repo_health.md`
