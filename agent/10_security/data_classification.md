# Data Classification

## Purpose

Categorizes project data to determine required security controls.

## Categories

1. **PUBLIC**: General info, documentation, public code.
2. **INTERNAL**: Project plans, roadmaps, architecture.
3. **CONFIDENTIAL**: API keys (masked), non-public algorithms, business logic.
4. **RESTRICTED**: Customer PII, passwords, private keys.

## Controls

- **RESTRICTED**: Must NEVER be stored in the repo. Use external Vault.
- **CONFIDENTIAL**: Encrypt at rest. Access restricted to authorized users.
