# Workflow: Security Review

## Purpose

Systematic identification and mitigation of vulnerabilities, secrets leakage, and compliance risks.

## Required Inputs

- **Active Codebase**: Full repository access.
- **Dependency Manifests**: (e.g., `package-lock.json`, `requirements.txt`).

## Expected Outputs

- **Security Baseline**: Updated `agent/09_state/SECURITY_STATE.md`.
- **Vulnerability Log**: Recorded in `plans/Security/VULN_LOG.md`.
- **Remediation Plan**: Tasks added to Backlog if issues are found.

## Procedure (Adopt `agent/03_profiles/profile_security_auditor.md`)

1. **Token Risk Check**: Assess budget. Security audits often involve high context usage.
2. **Secret Scrubbing**: Run `agent/06_skills/security/skill_scrub_secrets.md`. Scrutinize logs and commit history.
3. **Dependency Audit**: Execute `agent/06_skills/security/skill_dependency_audit.md`. Identify "High" or "Critical" CVEs.
4. **Threat Modeling**: If new features were added, update `agent/10_security/threat_model_template.md` using `agent/06_skills/security/skill_threat_model.md`.
5. **Static Analysis**: Run stack-specific security gates (e.g., `agent/05_gates/by_stack/python/gate_python_security.md`).
6. **Policy Validation**: Check compliance with `agent/10_security/secrets_policy.md`.
7. **Hardening**: Apply mitigations from `agent/06_skills/security/skill_hardening.md`.
8. **Gate Validation**: MUST ensure 100% pass on `agent/05_gates/global/gate_global_security.md`.

## Failure Modes & Recovery

- **Critical Leak Found**: STOP ALL ACTIONS. Execute `agent/10_security/vuln_response_playbook.md` immediately.
- **Vulnerable Upstream**: If a dependency cannot be updated without breakage, route to `agent/01_entrypoints/scenarios/scenario_emergency_hotfix.md`.

## Required Gates

- `agent/05_gates/global/gate_global_security.md` (Must Pass).
- `agent/12_checks/rubrics/security_rubric.md` (Level 4+ Required).

## State Update

- Update `agent/09_state/SECURITY_STATE.md`:
  - Update `last_audit_date`.
  - Update `open_vulnerabilities`.

## Related Files

- `agent/10_security/security_baseline.md`
- `agent/09_state/SECURITY_STATE.md`
