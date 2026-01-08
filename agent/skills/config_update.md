# Skill: Configuration Update

**Purpose**: Safely update application configuration (env vars, config files).

## 1. Identify Source
-   **Environment Variables**: `.env`, `.env.local`, `docker-compose.yml`.
-   **Config Files**: `config.py`, `settings.json`, `application.properties`.

## 2. Safety Check
-   **Secrets**: Do NOT commit secrets to git. Ensure they are in `.env` only.
-   **Validation**: Does the app validate config on startup?
-   **Restart**: Note if a restart is required (e.g., systemd, docker).

## 3. Update Procedure
1.  **Backup**: `cp .env .env.bak`
2.  **Edit**: Use `write_to_file` or `sed` to update the value.
3.  **Verify**: Grep the file to confirm change.
4.  **Reload**: Restart service if needed.
