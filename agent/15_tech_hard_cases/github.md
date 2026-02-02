# GitHub Hard Cases & Failure Scenarios

## Overview

Real-world GitHub failure scenarios with symptoms, causes, diagnostics, fixes, and prevention. Use Issue-Key format `HC-GITHUB-XXX` and reference `Issue-Key: GITHUB-<hash>` when logging incidents. Suggested prompt: `prompts/hard_cases/github_hard_cases.txt`.

---

## AUTHENTICATION & ACCESS

### HC-GITHUB-001: gh CLI Not Logged In

**Symptom:**

```
$ gh repo view
error connecting to GitHub: authentication failed
```

**Likely Causes:**
- No `gh auth login` performed on this machine
- Cached credentials expired
- Using enterprise host without `--hostname`

**Fast Diagnosis:**
```bash
gh auth status || true
gh config list | grep host
```

**Fix Steps:**
1. Run `gh auth login` and select HTTPS; paste PAT with correct scopes.
2. For enterprise, add `--hostname <ghe-host>`.
3. Re-run `gh auth status` to confirm.

**Prevention:**
- Add `gh auth status` preflight in setup scripts.
- Cache PAT in keychain/credential manager.

---

### HC-GITHUB-002: Token Scopes Insufficient

**Symptom:**

```
HTTP 403: Resource not accessible by personal access token
```

**Likely Causes:**
- Missing `repo` or `workflow` scope
- PAT created as fine-grained without required permissions
- Using GITHUB_TOKEN where PAT required

**Fast Diagnosis:**
```bash
grep -E "GITHUB_TOKEN|PAT" -n .github/workflows/*.yml || true
gh auth status --show-token-scopes
```

**Fix Steps:**
1. Regenerate PAT with needed scopes (repo, workflow, admin:repo_hook if webhooks).
2. Update secrets store and rotate tokens in workflows.
3. Re-run failing action or API call.

**Prevention:**
- Document minimal scopes per workflow.
- Add CI check to verify required secrets exist with scopes noted in README.

---

### HC-GITHUB-003: SSO Required / Token Rejected

**Symptom:**

```
SSH: access denied or HTTP 403 with SSO required
```

**Likely Causes:**
- Enterprise SSO not authorized for the token
- User not linked to org SSO
- Token created before SSO enablement

**Fast Diagnosis:**
```bash
gh auth status --hostname <org-host>
```

**Fix Steps:**
1. Log into org SSO portal and authorize PAT.
2. Re-create PAT after SSO enablement.
3. For SSH, ensure `ssh -T git@github.com` succeeds after SSO approval.

**Prevention:**
- Add SSO authorization instructions to onboarding.
- Use org-managed fine-grained tokens with enforced SSO.

---

### HC-GITHUB-004: SSH Key Not Accepted

**Symptom:**

```
Permission denied (publickey).
fatal: Could not read from remote repository.
```

**Likely Causes:**
- Key not added to GitHub
- Wrong SSH config Host/Hostname entries
- Old SHA1 RSA key rejected

**Fast Diagnosis:**
```bash
ssh -T git@github.com -v | tail -n 20
cat ~/.ssh/config
```

**Fix Steps:**
1. Add new ed25519 key to GitHub and ssh-agent.
2. Ensure `Host github.com` uses correct `IdentityFile`.
3. Remove deprecated RSA-SHA1 keys.

**Prevention:**
- Use ed25519 keys, rotate annually.
- Verify SSH connectivity in CI build agents.

---

## CI/CD FAILURES

### HC-GITHUB-005: Actions Missing Secrets

**Symptom:**

```
Error: Process completed with exit code 1
Error: Secrets GCP_KEY missing
```

**Likely Causes:**
- Secret not defined for repo/environment
- PR from fork with secrets unavailable
- Wrong secret name in workflow

**Fast Diagnosis:**
```bash
rg "secrets\." .github/workflows
```

**Fix Steps:**
1. Define required secrets in repo or environment with correct names.
2. For forked PRs, guard secret usage and run reduced jobs.
3. Add input validation: fail early when secret missing.

**Prevention:**
- Add `required-secrets.md` and gate in CI.
- Use environment protection rules with reviewers.

---

### HC-GITHUB-006: Cache Poisoning or Misses

**Symptom:**

```
Cache not found for input keys: linux-node-modules-
Unexpected files from another branch restored
```

**Likely Causes:**
- Overly broad cache keys
- Missing restore-keys ordering
- Cache saved from untrusted forks

**Fast Diagnosis:**
```bash
rg "actions/cache" -n .github/workflows
grep -A3 cache-key .github/workflows/*.yml || true
```

**Fix Steps:**
1. Include lockfile hash and runner OS in key.
2. Disable cache save on forked PRs.
3. Add checksum validation after cache restore.

**Prevention:**
- Standardize cache key template per language.
- Periodically bust caches when lockfile changes.

---

### HC-GITHUB-007: Matrix Mismatch (Node/Python/Java)

**Symptom:**

```
Runtime not found: node16
java-version '8' not available for this OS
```

**Likely Causes:**
- Unsupported runtime version on runner image
- Matrix includes OS/arch combos not supported
- Toolcache missing version

**Fast Diagnosis:**
```bash
grep -n "matrix" -n .github/workflows/*.yml
```

**Fix Steps:**
1. Use supported versions (e.g., `node-version: 20.x`).
2. Add `fail-fast: false` and note failing dimension.
3. Install missing runtime via actions/setup-*.

**Prevention:**
- Keep matrix aligned with LTS runtimes.
- Reuse centralized workflow templates with validated matrices.

---

### HC-GITHUB-008: Flaky CI Tests

**Symptom:**

```
Random test failures; rerun passes
```

**Likely Causes:**
- Race conditions/timeouts
- External service dependencies
- Not enough resources on runners

**Fast Diagnosis:**
```bash
# Identify flake rate
gh run view <run-id> --log --job <job>
```

**Fix Steps:**
1. Add retries with backoff for network calls.
2. Mark flaky tests and quarantine; stabilize before merge.
3. Use deterministic seeds and freeze time in tests.

**Prevention:**
- Track flake rate in CI metrics.
- Gate merges on flake budget or quarantine list being empty.

---

### HC-GITHUB-009: Artifacts Not Uploaded

**Symptom:**

```
No artifacts found for the workflow run
```

**Likely Causes:**
- Paths do not match output location
- `if:` condition prevented upload
- Artifacts exceed size limit

**Fast Diagnosis:**
```bash
grep -n "upload-artifact" -n .github/workflows/*.yml
```

**Fix Steps:**
1. Confirm artifact paths exist at runtime.
2. Remove overly strict `if:` filters or add `always()`.
3. Split artifacts to stay under size limits.

**Prevention:**
- Add step to list files before upload.
- Document artifact expectations per workflow.

---

### HC-GITHUB-010: Runner Disk Full

**Symptom:**

```
No space left on device
```

**Likely Causes:**
- Large caches/artifacts
- Docker images not pruned
- Build artifacts not cleaned between jobs

**Fast Diagnosis:**
```bash
du -sh .
docker system df
```

**Fix Steps:**
1. Add cleanup steps: `docker system prune -af`, delete node_modules when done.
2. Use `actions/cache` selectively with size awareness.
3. Switch to larger runner or self-hosted runner with more disk.

**Prevention:**
- Add disk usage gate in CI.
- Periodic cache cleanup workflow.

---

## BRANCHING & PR ISSUES

### HC-GITHUB-011: Merge Conflicts on PR

**Symptom:**

```
This branch has conflicts that must be resolved
```

**Likely Causes:**
- Base branch diverged
- Generated files committed causing frequent conflicts

**Fast Diagnosis:**
```bash
git fetch origin && git merge-base --is-ancestor HEAD origin/main || echo "needs rebase"
```

**Fix Steps:**
1. Rebase or merge latest base branch into feature branch.
2. Regenerate artifacts post-rebase.
3. Force-push updated branch.

**Prevention:**
- Keep PRs small; rebase frequently.
- Avoid committing generated files when possible.

---

### HC-GITHUB-012: Failing Required Checks Blocking Merge

**Symptom:**

```
Merging is blocked; failing or missing required status check
```

**Likely Causes:**
- Required check renamed/removed
- New branch protection rule missing new workflow
- Flaky check failing

**Fast Diagnosis:**
```bash
gh api repos/{owner}/{repo}/branches/{branch}/protection | jq '.required_status_checks'
```

**Fix Steps:**
1. Update branch protection to include correct checks.
2. Rerun failing checks after fixing causes.
3. Temporarily allow admin bypass only with approval.

**Prevention:**
- Version branch protection via Terraform/Codified configs.
- Keep workflow names stable; avoid renames.

---

### HC-GITHUB-013: Protected Branch Blocks Pushes

**Symptom:**

```
remote: error: GH006: Protected branch update failed
```

**Likely Causes:**
- Direct pushes disabled
- Missing approvals for required reviewers
- Missing signed commits requirement

**Fast Diagnosis:**
```bash
gh api repos/{owner}/{repo}/branches/main/protection | jq '.restrictions'
```

**Fix Steps:**
1. Open PR instead of pushing directly.
2. Collect required approvals and satisfy status checks.
3. Sign commits if required: `git config commit.gpgsign true`.

**Prevention:**
- Document branch protection rules in CONTRIBUTING.md.
- Enforce PR-based workflows.

---

### HC-GITHUB-014: Wrong Base Branch Selected

**Symptom:**

```
PR accidentally targets production branch
```

**Likely Causes:**
- Fork default branch differs
- GitHub UI defaulted to main/master

**Fast Diagnosis:**
```bash
gh pr view --json baseRefName
```

**Fix Steps:**
1. Use GitHub UI to edit base branch.
2. Rebase on correct base and resolve conflicts.

**Prevention:**
- Use repository setting to default to `develop` when applicable.
- Add CI guard to fail when PR base is not allowed.

---

## ISSUE HYGIENE

### HC-GITHUB-015: Duplicate Issues

**Symptom:**

```
Multiple issues describe same bug; triage confusion
```

**Likely Causes:**
- No search before filing
- Inconsistent labels

**Fast Diagnosis:**
```bash
gh issue list -S "same keyword" --label bug
```

**Fix Steps:**
1. Close duplicates referencing canonical issue.
2. Move relevant info/comments to canonical issue.

**Prevention:**
- Add issue template requiring search confirmation.
- Use automation to suggest similar issues.

---

### HC-GITHUB-016: Stale Issues/PRs

**Symptom:**

```
Issues open for months with no updates
```

**Likely Causes:**
- No SLA or ownership
- Automated stale bot misconfigured

**Fast Diagnosis:**
```bash
gh issue list -s open --limit 200 --json number,updatedAt | jq '.[] | select(.updatedAt < "2023-01-01")'
```

**Fix Steps:**
1. Assign owners and due dates.
2. Close with explanation or re-triage.
3. Tune stale bot thresholds.

**Prevention:**
- Weekly triage ritual with owners.
- Dashboards for stale items.

---

### HC-GITHUB-017: Missing Reproduction Details

**Symptom:**

```
Bug cannot be reproduced; issue lacks steps/logs
```

**Likely Causes:**
- Issue template ignored
- No minimal repro provided

**Fast Diagnosis:**
```bash
gh issue view <num> --json body
```

**Fix Steps:**
1. Comment requesting minimal repro with environment info.
2. Convert to discussion if not actionable.

**Prevention:**
- Enforce issue templates with required fields.
- Provide repro scaffolds and sandboxes.

---

## RELEASE & TAGGING

### HC-GITHUB-018: Tag Mismatch / Missing Release

**Symptom:**

```
CI build fails: tag v1.2.0 not found
Release page missing assets for tag
```

**Likely Causes:**
- Tag pushed locally but not pushed upstream
- Release created without tag
- Tag signed requirement failing

**Fast Diagnosis:**
```bash
git tag -l | tail
git ls-remote --tags origin | tail
```

**Fix Steps:**
1. Push tag: `git push origin v1.2.0`.
2. Create release from tag via GitHub UI or `gh release create`.
3. Sign tag if policy requires: `git tag -s`.

**Prevention:**
- Automate tagging via CI after successful build.
- Enforce signed tags via branch protection.

---

### HC-GITHUB-019: Changelog Generation Broken

**Symptom:**

```
release action fails: cannot generate changelog
```

**Likely Causes:**
- Conventional commit parser errors
- Missing GITHUB_TOKEN permissions for releases
- Tooling not installed

**Fast Diagnosis:**
```bash
gh release view || true
```

**Fix Steps:**
1. Ensure `contents: write` permission for workflow.
2. Install changelog tooling (git-cliff, conventional-changelog).
3. Validate commit messages conform to spec.

**Prevention:**
- Use commit linting in CI.
- Keep release tooling version-pinned.

---

### HC-GITHUB-020: Semantic Versioning Mistakes

**Symptom:**

```
Minor release contains breaking change; users complain
```

**Likely Causes:**
- Improper semver bump
- PR labels not mapped to release type
- Missing CHANGELOG review

**Fast Diagnosis:**
```bash
gh release view --json tagName,body
```

**Fix Steps:**
1. Re-release with corrected version and notes.
2. Deprecate incorrect release; add warning.
3. Add labels-to-version mapping in release workflow.

**Prevention:**
- Enforce release checklist with semver gate.
- Require reviewer approval for release notes.

---

### HC-GITHUB-021: Actions Exceeding Rate Limits

**Symptom:**

```
API rate limit exceeded for installation
```

**Likely Causes:**
- Too many concurrent jobs hitting API
- Missing REST throttling/backoff

**Fast Diagnosis:**
```bash
gh api rate_limit
```

**Fix Steps:**
1. Add retries with backoff to scripts.
2. Cache API responses when possible.
3. Spread workflows or use GitHub Enterprise with higher limits.

**Prevention:**
- Centralize API access with rate limiter.
- Monitor rate-limit usage via metrics.

---

### HC-GITHUB-022: Environments Block Deployment

**Symptom:**

```
waiting for reviewers for environment production
```

**Likely Causes:**
- Missing reviewers assigned
- Protection rules require manual approval
- Secrets scoped to environment not accessible

**Fast Diagnosis:**
```bash
gh api repos/{owner}/{repo}/environments
```

**Fix Steps:**
1. Assign reviewers or temporarily relax rules for incident response.
2. Ensure secrets exist in the targeted environment.
3. Re-run deployment with correct environment name.

**Prevention:**
- Document environment approvals and required reviewers.
- Use scheduled deployment windows to ensure availability.

---

## Issue-Key and Prompt Mapping

- Example Issue-Key: `Issue-Key: GITHUB-9f3e2b`
- Use prompt: `prompts/hard_cases/github_hard_cases.txt`
