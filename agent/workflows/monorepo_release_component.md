# Monorepo: Component Release

**Purpose**: Manage the release lifecycle of individual components or the entire repository.
**When to use**: When preparing to deploy or publish a specific part of the monorepo.
**Prerequisites**: CI passed (`monorepo_ci_matrix.md`), Clean git state.
**Type**: Monorepo Workflow

---

## Workflow Contract

| Attribute | Details |
| :--- | :--- |
| **Inputs** | Component ID(s), Release Type, Topology Selection |
| **Outputs** | Tagged Commit, Published Artifacts, CHANGELOG, `COMPONENT_RELEASE_MAP.md` update |
| **Policy** | Controlled by `agent/release/RELEASE_TOPOLOGY.md` |
| **Stop Conditions** | Dirty Git State, CI Failure, Shared Lib Impact Violation |

---

## Step 1: Release Selection Gate

**CRITICAL**: You must first determine WHAT content is legally eligible for release based on the active topology.

1.  **Read Topology**: Check `agent/release/RELEASE_TOPOLOGY.md`.
2.  **Read Map**: Check `agent/release/COMPONENT_RELEASE_MAP.md`.
3.  **Analyze Impact**:
    - Run `git diff` against the last release tag.
    - If *Shared Libraries* have changed:
        - **SINGLE_VERSION**: All parts must release.
        - **PER_COMPONENT**: You MUST identify all dependents.
            - **Decision**: Either bump all dependents OR explicitly mark them as 'no-op' with a recorded reason.
            - *Fail safely if this decision is ambiguous.*

---

## Step 2: Verification Verify

Ensure the code to be released is stable.

1.  **Check CI Status**: Confirm the latest commit has passed `monorepo_ci_matrix.md` for these components.
2.  **Dry Run**: Run a local build/package command to ensure artifacts generated correctly.
3.  **Release Candidate (Optional)**:
    - If `ReleaseType == RC`:
    - Generate version `x.y.z-rc.N`.
    - Publish to artifact registry.
    - **STOP**. Do not deploy to production.

---

## Step 3: Determine Version Numbering

**Strategy A: Independent Versioning (PER_COMPONENT)**
- Each component tracks its own version (e.g., `auth` is v1.2.0, `ui` is v2.0.1).
- **Tag Format**: `[component-name]-v[version]` (e.g., `auth-service-v1.2.0`).

**Strategy B: Unified Versioning (SINGLE_VERSION)**
- All components share the same repository version.
- **Tag Format**: `v[version]` (e.g., `v1.5.0`).
- *Note: This causes "churn" where unchanged components get version bumps.*

---

## Step 4: Prepare Release

For each targeted component:

### 4.1 Update Manifests
Update the source of truth for the version:
- **Node**: `npm version [type] --no-git-tag-version` in component dir.
- **Python**: Bump `__version__` or `pyproject.toml`.
- **Java**: `mvn versions:set -DnewVersion=...`

### 4.2 Update Changelog
- Append entry to `agent/components/[id]/CHANGELOG.md` (if exists) or root `CHANGELOG.md`.
- Include: Date, Version, Summary of commits since last tag.

### 4.3 Update Component Map
- Update `agent/release/COMPONENT_RELEASE_MAP.md` with:
    - New Version
    - Release Date
    - Dependencies Checked

---

## Step 5: Commit & Tag

1. **Commit**:
    ```bash
    git add agent/components/[id]/package.json agent/release/COMPONENT_RELEASE_MAP.md [other-manifests]
    git commit -m "chore(release): [id] v[new-version]"
    ```
2. **Tag**:
    ```bash
    git tag [id]-v[new-version]
    ```
3. **Push**:
    ```bash
    git push origin main --tags
    ```

---

## Step 6: Publish / Deploy

Trigger the deployment or publish step.

- **Library**: `npm publish`, `mvn deploy`, `twine upload`.
- **Service**: Trigger container build & deploy pipeline (refer to `deploy_and_migrate.md`).
- **App**: Upload to store or invalidation CDN.

---

## Completion Criteria

- ✅ Manifests updated with new version.
- ✅ `COMPONENT_RELEASE_MAP.md` is current.
- ✅ Git tags exist.
- ✅ Artifacts published / Deployment triggered.
