# Entrypoint: Run Security Audit Only

## Purpose

Used to perform a deep security scan of the codebase.

## Inputs

- Access to all source code.

## Procedure

1. **Profile**: `profile_security_auditor.md`.
2. **Scanning**: Use `agent/06_skills/security/` tools (e.g., dependency checkers, secret scanners).
3. **Threat Modeling**: Update `plans/Security/THREAT_MODEL.md`.
4. **Reporting**: Create `plans/Security/AUDIT_REPORT.md` with findings and remediation steps.
5. **Enforcement**: Check against `agent/05_gates/global/gate_global_security.md`.

## Related Files

- `agent/10_security/security_baseline.md`
