# Secrets Policy

## Definition of a Secret

- API Keys
- Passwords
- Private Keys (.pem, .key)
- Authentication Tokens (JWT secrets)
- Database Connection Strings

## Detection Procedure

1. Run `grep -rE "key|password|secret|token" .`.
2. Exclude `agent/` and `.git/`.
3. If findings match "assigned value", flag as CRITICAL.

## Remediation Policy

- **Move to Environment Variables**.
- **Use .env.example** for placeholders.
- **Git Scrubbing**: If committed, use `bfgRepoCleaner` or `git filter-repo`.
