# Skill: Dependency Audit & CVE Scanning

## Purpose

Identifying and patching third-party library vulnerabilities.

## Execution Procedure

1. **Scan**: Execute `npm audit`, `pip-audit`, or `safety check`.
2. **Filter**: Identify "High" and "Critical" issues.
3. **Remediate**: Attempt `npm audit fix` or manual version bump.
4. **Verification**: Re-run scan to confirm 0 critical findings.

## Output Contract

- **Vulnerability Report**: Logged in `agent/09_state/SECURITY_STATE.md`.
