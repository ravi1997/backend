# Skill: Repo Health Check

## Purpose

Establishing a baseline of code quality, dependency safety, and documentation completeness.

## Input Contract

- **Repository Root**: Full path.

## Execution Procedure

1. **Metric Collection**:
    - **Dead Code**: Scan for unused functions/classes.
    - **Complexity**: Identify "Hotspots" (files with high cyclomatic complexity).
    - **Coverage**: Check `agent/09_state/TEST_STATE.md` for gaps.
2. **Standards Audit**:
    - Check against `agent/11_rules/repo_hygiene_rules.md`.
    - Verify `agent/AGENT_MANIFEST.md` exists and is versioned.
3. **Dependency Health**:
    - Run `agent/06_skills/security/skill_dependency_audit.md`.
4. **Documentation Audit**:
    - Check for missing `README.md`, `CHANGELOG.md`, or `CONTRIBUTING.md`.

## Output Contract

- **Health Report**: A summary of "Repo Debt" logged in `agent/09_state/PROJECT_STATE.md`.
- **Debt Backlog**: Critical issues added to `agent/09_state/BACKLOG_STATE.md`.
 Riverside

## Related Files

- `agent/12_checks/rubrics/quality_rubric.md`
