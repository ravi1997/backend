# Universal Release Policy

This document defines the Release Engineering standards for all projects managed by the AI Agent MD Pack.

## 1. Versioning Strategy
We adhere to [Semantic Versioning 2.0.0](https://semver.org/).

## 1.1 Release Topology
Our monorepo supports multiple release strategies (`SINGLE_VERSION`, `PER_COMPONENT`, `HYBRID`).
- **Definitive Rules**: See [RELEASE_TOPOLOGY.md](RELEASE_TOPOLOGY.md).
- **Component Status**: See [COMPONENT_RELEASE_MAP.md](COMPONENT_RELEASE_MAP.md).

**Format**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes.
- **MINOR**: Backward-compatible functionality.
- **PATCH**: Backward-compatible bug fixes.

### Prereleases
- Use hyphens: `1.0.1-alpha.1`, `2.0.0-rc.3`.
- Recommended flow: `alpha` -> `beta` -> `rc` -> `stable`.

## 2. Changelog Policy
Changelogs must be automatically generated to ensure accuracy and consistency.

### Conventional Commits
All commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
Structure: `<type>[optional scope]: <description>`

**Types**:
- `feat`: New feature (CORRELATES to MINOR version).
- `fix`: Bug fix (CORRELATES to PATCH version).
- `docs`: Documentation only.
- `chore`: Maintenance, dependencies.
- `refactor`: Code change that neither fixes a bug nor adds a feature.
- `ci`: Changes to CI configuration files and scripts.
- `test`: Adding missing tests or correcting existing tests.
- `BREAKING CHANGE`: Footer indicating a breaking change (CORRELATES to MAJOR version).

### Generation Method
- Use tools like `git-cliff`, `standard-version`, or `semantic-release` to parse git logs and generate `CHANGELOG.md`.

## 3. Release Checklist (Universal)
Every stack must fulfill these requirements before a stable release:

1.  **Tests Pass**: All unit, integration, and end-to-end tests must pass in CI.
2.  **Lint/Format**: Code must respect the project's style guide.
3.  **Artifact Verification**:
    -   Checksums (SHA256) generated.
    -   Smoke test performed on the built artifact (e.g., install and run `--version`).
    -   No sensitive secrets included (scan performed).
4.  **Documentation**: `README.md` and API docs updated.
5.  **Tagging**: Git tag created matching the version number (e.g., `v1.2.3`).

## 4. Rollback Policy
If a critical defect is found in Production:
1.  **Identify**: Confirm the issue and the bad version.
2.  **Revert**: Revert the commit(s) on `main` that caused the issue.
3.  **Patch**: If a fix is immediate, create a `hotfix` branch.
4.  **Redeploy**: Deploy the previous stable version (LKG - Last Known Good) immediately using existing CD workflows.
5.  **Post-Mortem**: Document root cause in `incident_logs/`.

## 5. Artifact Retention
- **Development/PR builds**: Retain for 7 days.
- **Release Candidates**: Retain for 30 days.
- **Stable Releases**: Retain indefinitely (or min. 1 year depending on storage policy).
