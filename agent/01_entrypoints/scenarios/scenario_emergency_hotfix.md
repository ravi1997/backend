# Scenario: Emergency Hotfix in Production

## Purpose

Rapidly deploying a critical fix to production while minimizing risk and maintaining audit trails.

## Inputs

- Critical production bug (data loss, security breach, service outage).
- Requirement for immediate fix (cannot wait for normal release cycle).

## Triage Phase (Adopt `profile_security_auditor.md`)

1. **Severity Assessment**: Classify the issue:
   - **P0 (Critical)**: Data loss, security breach, complete outage.
   - **P1 (High)**: Major feature broken, significant user impact.
   - **P2 (Medium)**: Minor feature broken, workaround exists.
2. **Impact Scope**: Determine how many users/systems are affected.
3. **Rollback Readiness**: Verify the ability to rollback if the hotfix fails.

## Development Phase (Adopt `profile_implementer.md`)

1. **Branch Strategy**: Create a hotfix branch from the production tag (not from main/dev).
2. **Minimal Change**: Implement the absolute smallest fix that resolves the issue.
3. **Local Verification**: Test the fix locally with production-like data.
4. **Peer Review**: Get emergency review from another developer (or User if solo).

## Testing Phase (Adopt `profile_tester.md`)

1. **Regression Focus**: Run tests for the affected module and critical paths.
2. **Staging Deploy**: Deploy to staging and verify the fix works.
3. **Smoke Tests**: Run basic health checks.

## Deployment Phase (Adopt `profile_release_manager.md`)

1. **Communication**: Notify stakeholders of the hotfix deployment.
2. **Monitoring**: Watch logs, metrics, and error rates closely during and after deployment.
3. **Verification**: Confirm the issue is resolved in production.

## Post-Mortem Phase (Adopt `profile_rule_checker.md`)

1. **Root Cause Analysis**: Document why the bug reached production in `plans/Security/INCIDENT_LOG.md`.
2. **Prevention**: Add checks to prevent this class of bug (tests, linting, gates).
3. **Backport**: Merge the hotfix back to main/dev branches.

## STOP Condition

- Production is stable, the issue is resolved, and the post-mortem is complete.

## Related Files

- `agent/10_security/vuln_response_playbook.md`
- `agent/04_workflows/10_release_process.md`
