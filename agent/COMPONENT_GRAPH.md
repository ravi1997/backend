# Component Dependency Graph

> [!NOTE]
> This file maps dependencies between components. It is used by the Change Impact Engine to prevent accidental breakage.
> You can manually add edges here, or let the agent detect them.

## Component Registry

This section lists all detected components in the repository. Each component has a corresponding detailed definition in `agent/components/<id>.md`.

| Component ID | Path | Stack Summary | Confidence | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| `root` | `.` | `markdown`, `bash` | Manual | Repository Root |

## Manual Overrides
<!-- Add edges that the agent might miss, or explicit policy-based dependencies -->
- **common** -> **backend** (Example: changes in common should trigger backend tests)
- **proto** -> **frontend** (Example: proto changes affect frontend clients)

## Detected Edges
<!-- The agent will populate this section based on imports and build files -->
<!-- FORMAT: source_component -> target_component (confidence: high/medium/low) -->

## Shared Zones
<!-- Paths that are considered "shared" and affect multiple or all components -->
- `/libs`
- `/packages`
- `/common`
- `/proto`
- `/infra`
