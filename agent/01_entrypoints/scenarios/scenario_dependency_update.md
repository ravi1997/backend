# Scenario: Dependency Update & Maintenance

## Purpose

Safely upgrading external libraries while mitigating breaking changes and security risks.

## Inputs

- List of outdated packages or a security alert (CVE).

## Assessment Phase (Adopt `profile_security_auditor.md`)

1. **Changelog Review**: Use `read_url_content` (if URL available) or search the web to find "Breaking Changes" for the target version.
2. **Impact Map**: Grep the codebase for all imports and usages of the library to be updated.
3. **Draft Plan**: Create `plans/Security/DEP_UPGRADE_PLAN.md` listing potential breakages.

## Implementation Phase (Adopt `profile_implementer.md`)

1. **Isolated Update**: Use the package manager (npm, pip, mvn) to update ONLY the target package in a trial run.
2. **Build Test**: Run the primary build command.
3. **Migration**: If breaking changes were identified, rewrite the internal implementation to match the new API.

## Verification Phase (Adopt `profile_tester.md`)

1. **Targeted Testing**: Run all tests that utilize the updated library.
2. **Integration Pass**: Run the full project integration suite.

## Conclusion (Adopt `profile_rule_checker.md`)

1. **Lockfile Update**: Ensure the lockfile (`package-lock.json`, `poetry.lock`, etc.) is committed.
2. **State Update**: Log the new versions in `agent/09_state/STACK_STATE.md`.

## STOP Condition

- Build is stable and all tests pass with the new dependency versions.
