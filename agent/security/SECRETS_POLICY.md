# Secrets Policy & Classification

This policy defines what constitutes a secret, how they are classified, and how they must be handled to prevent leaks.

## 1. Classification

| Level | Definition | Examples | Remediation |
| :--- | :--- | :--- | :--- |
| **CRITICAL** | Grants full access to production infrastructure or user data. | AWS Root keys, Prod DB Credentials, Private Keys (`.pem`, `.p12`, `.jks`), Payment Gateway Secrets. | Immediate Rotation, Incident Report (P1). |
| **HIGH** | Grants access to specific services or staging environments with write access. | Staging DB Credentials, Slack Bot Tokens (Write), GitHub Actions Tokens (Write). | Rotate within 24h. |
| **MEDIUM** | Read-only access to internal metadata or non-sensitive data. | Analytics Write Keys, Read-only API tokens. | Rotate within 7 days. |
| **LOW** | Internal IDs or tokens that are not directly exploitable but should be kept private. | Internal Service IDs, Debug Tokens. | Rotate on schedule. |

## 2. Forbidden Patterns (Deny List)

The following patterns **MUST NEVER** correspond to committed files or unmasked log output:

*   **Extensions**: `.pem`, `.p12`, `.jks`, `.key`, `.keystore`, `.ovpn`, `.ppk`, `.pfx`, `.p12`
*   **Filenames**: `secrets.*`, `*.secrets`, `credentials.*`, `id_rsa`, `id_dsa`
*   **Environment Files**: `.env`, `.env.local`, `.env.production` (Template files like `.env.example` are ALLOWED)
*   **Keywords** (Case Insensitive in code/logs):
    *   `BEGIN PRIVATE KEY`
    *   `BEGIN RSA PRIVATE KEY`
    *   `sk_live_` (Stripe)
    *   `ghp_` (GitHub)
    *   `xoxb-` (Slack)
    *   `AIza` (Google API)

## 3. Allowed Patterns (Allow List)

These are explicitly safe to commit:

*   `.env.example` (Must contain placeholders `FOO=`)
*   `pubspec.lock` (Flutter)
*   `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` (Node)
*   `poetry.lock` / `Pipfile.lock` (Python)
*   `gradle-wrapper.jar` (Java/Android - Binary but standard)

## 4. Handling Rules

### R1: No Raw Secrets in Logs
**Agents and Developers MUST NOT** print variables containing "token", "key", "password", or "secret" to standard output or logs.
*   **Bad**: `print(f"Connecting with {api_key}")`
*   **Good**: `print(f"Connecting with {mask(api_key)}")`

### R2: No Secrets in PR Descriptions
**Agents MUST** redact any secrets found in PR descriptions or comments. Use `[REDACTED]` placeholder.

### R3: Secret Configuration
Secrets **MUST** be loaded from environment variables or a secure vault (e.g., HashiCorp Vault, AWS Secrets Manager). Hardcoding is **FORBIDDEN**.

### R4: Android Keystores
Android signing configurations **MUST** use environment variables for `storePassword` and `keyPassword`. The `.jks` file **MUST** be in `.gitignore`.

## 5. Redaction Strategy

When displaying sensitive data in non-secure contexts (e.g., CLI output, non-audit logs):
1.  Show first 4 chars (if length > 8).
2.  Show last 4 chars (if length > 8).
3.  Replace middle with `***`.
4.  Example: `xoxb-***-1234`
