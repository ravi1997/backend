# Security Baseline

## Purpose

Standard security requirements for all projects managed by this Agent.

## Base Rules

1. **Never commit `.env` or secrets**.
2. **Encrypt PII** at rest and in transit.
3. **Principle of Least Privilege**: Agent and App should only have access to necessary files/network.
4. **Sanitize Inputs**: All external data (API, CLI, DB) must be validated.
5. **Dependency Hygiene**: Only use maintained libraries.

## Enforcement

- Manual audit via `profile_security_auditor.md`.
- Automated scan via `agent/06_skills/security/`.
