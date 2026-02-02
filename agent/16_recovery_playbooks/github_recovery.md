# GitHub Recovery Playbook

Purpose: actionable steps to recover from GitHub failures. Map errors to hard cases (`HC-GITHUB-XXX`).

## RECOVERY-GITHUB-001: Auth/Token Failures
- When: gh CLI login errors, 403, SSO required (HC-GITHUB-001/002/003/004).
- Steps:
  1. `gh auth status --show-token-scopes || true` and `ssh -T git@github.com -v | tail -n 20`.
  2. Re-login with `gh auth login` (add `--hostname` for enterprise); ensure ed25519 key loaded via `ssh-add -l`.
  3. Recreate PAT with `repo,workflow,read:org` scopes and authorize SSO; update secrets.
  4. Retry failing command; capture `~/.config/gh/hosts.yml` state for audit.
- Validate: `gh repo view` succeeds; `git ls-remote` works via SSH.

## RECOVERY-GITHUB-002: CI/CD Secrets & Matrix Failures
- When: missing secrets, cache issues, matrix/toolchain mismatch (HC-GITHUB-005/006/007/009/010/021).
- Steps:
  1. Inspect workflow: `rg "secrets\." .github/workflows` and `gh api rate_limit`.
  2. Confirm secrets exist and scopes correct; for forks, restrict secret usage and mark job to skip.
  3. Adjust cache keys to include lockfile hash; delete poisoned caches via Actions UI if needed.
  4. Pin tool versions (`node-version: 20.x`, `python-version: '3.11'`, `java-version: '17'`); rerun failed matrix leg.
  5. Free disk: `docker system prune -af`, delete temp artifacts; rerun job.
- Validate: rerun workflow; ensure all matrix legs pass and artifacts uploaded.

## RECOVERY-GITHUB-003: Branch Protection & PR Blocks
- When: merge conflicts, required checks failing, protected branch errors, wrong base (HC-GITHUB-011/012/013/014/022).
- Steps:
  1. Sync branch: `git fetch origin && git rebase origin/<base>` or merge.
  2. Verify branch protection via `gh api repos/{owner}/{repo}/branches/<base>/protection` and align workflow names.
  3. Fix failing checks or request environment approvals; avoid admin bypass except incidents.
  4. Update PR base if wrong; resolve conflicts and force-push.
- Validate: PR shows green checks, correct base, merge button enabled.

## RECOVERY-GITHUB-004: Issue Hygiene Problems
- When: duplicates, stale, missing repro (HC-GITHUB-015/016/017).
- Steps:
  1. Search similar issues: `gh issue list -S "<keyword>" --label bug`.
  2. Mark duplicates and close with reference; move key info to canonical issue.
  3. Request repro steps or minimal repo; set SLA and assignee.
  4. Reconfigure stale bot thresholds if over-closing.
- Validate: issue count reduced; active issues have owners and repro notes.

## RECOVERY-GITHUB-005: Release & Tagging Breakages
- When: tag mismatch, changelog failures, semver mistakes (HC-GITHUB-018/019/020).
- Steps:
  1. Compare local vs remote tags: `git tag -l`, `git ls-remote --tags origin`.
  2. Push missing tag or recreate release with `gh release create <tag> --notes "..."`.
  3. Fix changelog tooling permissions (`contents: write`); rerun release pipeline.
  4. If semver incorrect, deprecate bad release, publish corrected version, communicate impact.
- Validate: release page shows assets, changelog generated, semver aligns with changes.
