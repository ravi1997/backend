# Release Topology & Versioning Strategy

This document defines how versioning and releases are handled in this monorepo. The active topology determines whether components are versioned together or independently.

## Active Topology
**CURRENT_TOPOLOGY**: `PER_COMPONENT`  
*(Options: SINGLE_VERSION, PER_COMPONENT, HYBRID)*

---

## Topologies Defined

### 1. SINGLE_VERSION (Repo-Wide Versioning)
- **Concept**: The entire repository shares a single version number (e.g., `v1.2.3`).
- **Trigger**: Any release bumps the version for *all* deliverable artifacts.
- **Changelog**: One global changelog for the repo.
- **Best for**: Tightly coupled services, or when the repo represents a single product with distributed parts.

### 2. PER_COMPONENT (Independent Versioning)
- **Concept**: Each component (defined in `COMPONENT_REGISTRY.md` or similar) has its own `VERSION` file and changelog.
- **Trigger**: Releasing `component-a` bumps only `component-a`.
- **Changelog**: `components/foo/CHANGELOG.md`.
- **Coupling**: Loose. A change in `component-a` does not force a release of `component-b`.
- **Shared Libs**: If a shared library changes, **ALL** components depending on it must be evaluated for a bump or re-testing.

### 3. HYBRID (Core vs. Apps)
- **Concept**: Core platform libraries follow `SINGLE_VERSION`. Consumer apps follow `PER_COMPONENT`.
- **Trigger**: 
    - Releasing "Core" bumps the platform version.
    - Releasing an "App" bumps only that app.
- **Best For**: Platform engineering teams supporting multiple distinct products in one repo.

---

## Rules of Engagement

### The "Release Selection Gate"
Before any deployment pipeline starts, the Agent must:
1.  **Identify Candidates**: Which components have changed since their last release?
2.  **Check Topology**: Apply the rules above.
3.  **Confirm Selection**: Explicitly list the components to be released. 

### Shared Library Impact
**CRITICAL**: If a file in a shared path (e.g., `lib/shared`, `packages/common`) is modified:
- **SINGLE_VERSION**: Trivial. The whole repo version bumps.
- **PER_COMPONENT**: 
    - The Agent MUST identify all components depending on this shared path.
    - **Policy**: You must either:
        1.  Bump/Release ALL dependent components.
        2.  Explicitly mark a component as "Skipped" (requires rollback plan/risk acceptance).

### Release Candidates (RC)
- Topologies support "RC" flows (e.g., `v1.2.0-rc.1`).
- RCs can be built and published to artifact registry *without* deploying to production.
