# Command Safety (Denylist + safer alternatives)

Even in dev/staging, avoid catastrophic commands unless explicitly requested.

## Denylist patterns (block or require explicit confirmation)
- `rm -rf /` or `rm -rf /*`
- `mkfs*`, `dd if=`, raw disk writes (`/dev/sdX`)
- `shutdown`, `reboot` (on servers)
- `:(){ :|:& };:` (fork bomb)
- `docker system prune -a --volumes` (data loss)
- `truncate -s 0 /var/log/*` (destroys evidence)

## Safer alternatives
- Use targeted deletes: `rm -rf ./build ./dist`
- Use `docker image prune` (without volumes) first
- Use `journalctl --vacuum-time=7d` rather than deleting logs
- Use backups/exports before migrations or volume deletion

## Evidence preservation rule
Before any cleanup: store evidence (logs, configs, versions) in an incident artifact.
