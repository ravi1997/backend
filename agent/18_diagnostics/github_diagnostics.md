# GitHub Diagnostics Bundle

Run when GitHub workflows/auth fail. Safe defaults, no secrets printed.

## Quick Checks
- Auth status: `gh auth status --show-token-scopes || true`
- SSH connectivity: `ssh -T git@github.com -v | tail -n 20`
- Rate limits: `gh api rate_limit`
- Branch protection: `gh api repos/{owner}/{repo}/branches/{branch}/protection`
- Secrets references: `rg "secrets\." .github/workflows`
- Matrix/runtime inspection: `rg "matrix" .github/workflows`
- Actions cache keys: `rg "actions/cache" .github/workflows`
- Disk usage (self-hosted): `df -h && docker system df || true`
- Release tags: `git tag -l | tail && git ls-remote --tags origin | tail`

## Triage Script (pseudo)
1. Collect workflow run URL and failing job logs via `gh run view <id> --log`.
2. Capture runner env summary (OS, disk, runtime versions).
3. Snapshot of `.github/workflows` relevant file with line numbers for quick review.
4. Produce checklist of missing secrets, matrix mismatches, branch protection anomalies.
