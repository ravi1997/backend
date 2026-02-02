# GitHub Caveats & Footguns

Use Issue-Key format `Issue-Key: GITHUB-<hash>` in incident logs. Apply these guardrails.

## Issue-Key Standard & Dedupe Rules
- Enforce Issue-Key in PR/issue templates: `Issue-Key: GITHUB-<shortid>`.
- During triage, dedupe by matching Issue-Key or stack trace; merge duplicates and close with reference.
- For Actions incidents, store Issue-Key in workflow run summary and incident report.

## Authentication Pitfalls
- SSO enforcement silently blocks PATs; always authorize tokens after creation.
- Fine-grained PATs default to least privilege—verify `contents:read/write` and `actions:read/write` explicitly.
- SSH keys using RSA-SHA1 may be rejected; prefer ed25519.

## CI/CD Footguns
- Cache keys too broad cause poison/misses—include OS + lockfile hash.
- Forked PRs cannot access repo secrets; guard secret use with conditions and fallbacks.
- Workflow renames break required-check gating; keep identifiers stable or update protection rules in lockstep.
- Self-hosted runners leak secrets if not isolated; gate with labels and allow-list.

## Branching & PR Caveats
- Protected branches block direct pushes; always open PRs and ensure commit signing matches policy.
- Required reviewers rules apply per environment; deployments hang if reviewers unavailable—maintain rotation.
- Base-branch drift causes noisy conflicts; mandate frequent rebases for long-lived branches.

## Issue Management Caveats
- Missing repro details stall fixes—issue templates must require environment, steps, expected/actual behavior.
- Stale bots can close active work; tune labels (`keep-open`) and grace periods.
- Labels drive automation (release notes, triage); keep label taxonomy documented and enforced.

## Release Caveats
- Tags without releases break artifact downloads; automate release creation from CI only.
- Semver mistakes propagate quickly; require release PR + review of CHANGELOG and diff.
- Actions using `GITHUB_TOKEN` lack cross-repo perms; use PAT for multi-repo publishing with least scope.
