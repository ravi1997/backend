# Workflow: Release Process

## Purpose

Finalize, package, and distribute the project while ensuring full traceability and rollback readiness.

## Required Inputs

- **Stable Branch**: Passing 100% of `agent/05_gates/global/gate_global_quality.md`.
- **Approved Backlog**: All release-bound tasks marked as "DONE".

## Expected Outputs

- **Release Tag**: Git tag in repository (e.g., `v1.2.3`).
- **Release Notes**: Finalized `agent/07_templates/release/RELEASE_NOTES.md`.
- **Artifacts**: Build binaries or Docker images tagged with the version.

## Procedure (Adopt `agent/03_profiles/profile_release_manager.md`)

1. **Token Risk Check**: Final budget check before artifacts are generated.
2. **Readiness Audit**: Complete the `agent/07_templates/release/GO_NO_GO_CHECKLIST.md`.
3. **Versioning**: Apply `agent/07_templates/release/VERSIONING_POLICY.md` to determine the next Version ID.
4. **Documentation Sync**:
    - Update `CHANGELOG.md` using `agent/06_skills/knowledge_extraction/skill_change_log.md`.
    - Finalize `agent/07_templates/release/RELEASE_NOTES.md`.
5. **Tagging**: Execute `agent/06_skills/devops/skill_release_tagging.md`.
6. **Artifact Generation**:
    - If Docker: Run `agent/06_skills/devops/skill_dockerize.md` in production mode.
    - If GitHub: Execute `agent/06_skills/devops/skill_github_release_flow.md`.
7. **Pipeline Monitoring**: Monitor the CI/CD pipeline for completion using `agent/06_skills/devops/skill_ci_pipeline.md`.
8. **Final State Update**: Update `agent/09_state/PROJECT_STATE.md` to "RELEASED" and `agent/09_state/RELEASE_STATE.md` with the new version link.

## Failure Modes & Recovery

- **Pipeline Failure**: If CI/CD fails mid-release, execute `agent/06_skills/devops/skill_release_tagging.md` rollback procedure.
- **Critical Post-Release Bug**: If a bug is found immediately, transition to `agent/01_entrypoints/scenarios/scenario_emergency_hotfix.md`.

## Required Gates

- `agent/05_gates/global/gate_global_release.md` (Must Pass).
- `agent/12_checks/checklists/release_checklist.md` (Must Pass).

## Related Files

- `agent/06_skills/devops/skill_release_tagging.md`
- `agent/09_state/RELEASE_STATE.md`
