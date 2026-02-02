# Skill: Secrets Handling & Environment Safety

## Purpose

Ensuring that sensitive credentials never enter the version control system.

## Execution Procedure

1. **Grep**: Search for `API_KEY`, `PASSWORD`, `SECRET`, `TOKEN`.
2. **Pattern Match**: Identify SSH keys (`.pem`, `.key`) and `.env` files.
3. **Gitignore Validation**: Ensure these patterns are blocked.
4. **Remediation**: Use `git rm --cached` if a secret was accidentally tracked.

## Output Contract

- **Safety Report**: Signal "GREEN" if no secrets are tracked.
