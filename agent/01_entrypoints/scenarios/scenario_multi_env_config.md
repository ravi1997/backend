# Scenario: Multi-Environment Configuration Management

## Purpose

Managing different configurations for development, staging, and production environments without hardcoding values or leaking secrets.

## Inputs

- Need to deploy the same codebase to multiple environments with different settings.

## Design Phase (Adopt `profile_architect.md`)

1. **Environment Taxonomy**: Define all environments:
   - `local`: Developer machine.
   - `dev`: Shared development server.
   - `staging`: Pre-production testing.
   - `production`: Live system.
2. **Configuration Strategy**: Choose an approach:
   - **Environment Variables**: `.env` files (never committed).
   - **Config Files**: `config/dev.json`, `config/prod.json` (secrets externalized).
   - **Secret Manager**: AWS Secrets Manager, HashiCorp Vault, etc.
3. **Schema Definition**: Create `config/schema.json` defining all required config keys and their types.

## Implementation Phase (Adopt `profile_implementer.md`)

1. **Config Loader**: Write a configuration module that:
   - Reads from environment variables first.
   - Falls back to config files.
   - Validates against the schema.
   - Fails fast if required values are missing.
2. **Example Files**: Create `.env.example` and `config/example.json` with placeholder values.
3. **Gitignore**: Ensure `.env` and `config/*` (except examples) are in `.gitignore`.

## Security Phase (Adopt `profile_security_auditor.md`)

1. **Secret Audit**: Run `agent/06_skills/security/skill_scrub_secrets.md` to ensure no real secrets are committed.
2. **Access Control**: Document who has access to production secrets in `plans/Security/ACCESS_CONTROL.md`.
3. **Rotation Policy**: Define how often secrets should be rotated.

## Deployment Phase (Adopt `profile_release_manager.md`)

1. **Environment Verification**: Before each deployment, verify the config is correct for that environment.
2. **Smoke Tests**: Run basic health checks after deployment to ensure config is loaded correctly.

## STOP Condition

- All environments have correct, validated configurations.
- No secrets are in version control.
- Deployment process is documented.

## Related Files

- `agent/10_security/secrets_policy.md`
- `agent/10_security/data_classification.md`
