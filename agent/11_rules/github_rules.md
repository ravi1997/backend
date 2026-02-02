# Rules: GitHub & Version Control

**Stack**: Git / GitHub  
**Scope**: Branching, Commits, PRs, Workflow

---

## 1. Branching Strategy

- **Trunk**: `main` (or `master`) is the Source of Truth. It MUST always be deployable.
- **Feature Branches**: `feat/description-123` or `feature/short-desc`.
- **Bug Fixes**: `fix/issue-123-desc`.
- **Hotfixes**: `hotfix/urgent-desc`.
- **Releases**: `release/v1.0.0` (optional).

## 2. Commit Standards

- **Conventional Commits**: Use the conventional commit format:
  - `feat: add user login`
  - `fix: resolve crash on startup`
  - `docs: update readme`
  - `chore: update dependencies`
- **Granularity**: Commits should be atomic (one logical change).
- **History**: Do not rewrite history (force push) on shared branches (main/develop).

## 3. Pull Requests (PRs)

- **Size**: Keep PRs small (< 400 lines changed preferred). Large PRs should be split.
- **Description**: PRs MUST have a description explaining "Why" and "What".
- **Linking**: PRs MUST link to the Issue they address (e.g., "Closes #123").
- **Review**: All PRs MUST have at least 1 approval before merge.
- **CI**: All CI checks MUST pass before merge.

## 4. Workflows & Actions

- **Triggers**: CI should run on `pull_request` and `push` to main.
- **Secrets**: Use GitHub Secrets for credentials. NEVER hardcode in YAML.
- **Pinning**: GitHub Actions steps should be pinned to specific SHAs or tags.

## 5. Repository Hygiene

- **Ignored Files**: `.gitignore` MUST block binaries, secrets, node_modules, and OS files.
- **Readme**: `README.md` MUST explain how to Run, Build, and Test locally.
- **License**: `LICENSE` file MUST be present.

---

## Enforcement Checklist

- [ ] Conventional commits used
- [ ] CI pipeline exists
- [ ] Branch protection active on main
- [ ] .gitignore prevents junk files
- [ ] PR templates configured
