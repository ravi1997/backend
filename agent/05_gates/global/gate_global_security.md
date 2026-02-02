# Gate: Global Security

## Purpose

Enforce a "Zero-Trust" security model across all repositories and tech stacks.

## Explicit Pass/Fail Rubric

| Criterion | Methodology | Pass Threshold | Fail Trigger |
| --- | --- | --- | --- |
| **Secrets Exposure** | `agent/06_skills/security/skill_scrub_secrets.md` | 0 Findings | Any hardcoded key/token |
| **Dependency Risks** | `npm audit` / `pip audit` / `mvn ossindex` | 0 High/Critical | Any High/Critical CVE |
| **Identity Hygiene** | Check `.gitignore` for `.env`, `*.key`, `*.pem` | 100% Ignored | Any key file in Git index |
| **Data Safety** | `grep -r "console.log(password)"` | No sensitive logs | Plaintext sensitive logging |
| **Policy Match** | Audit against `agent/10_security/secrets_policy.md` | 100% Compliant | Any policy violation |

## Verification Procedure

1. **Run Secret Scanner**: Use regex-based search for patterns like `sk-`, `AIza`, `AKIA`.
2. **Run Dependency Audit**: Use stack-specific audit tools.
3. **Review Changeset**: Manually inspect `diff` for sensitive logic exposure.
4. **Security Rubric**: Finalize score in `agent/12_checks/rubrics/security_rubric.md`.

## Sign-off Command
>
> Proceed only if `agent/12_checks/rubrics/security_rubric.md` score is 10/10.

## Failure Playbook

- **Leak Found**: Immediately stop and transition to `agent/10_security/vuln_response_playbook.md`.
- **CVE Found**: Force update dependencies or implement a code-level patch.

## Related Files

- `agent/10_security/security_baseline.md`
- `agent/11_rules/repo_hygiene_rules.md`
