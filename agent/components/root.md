# Component: Root

**Component ID**: `root`
**Path**: `.`
**Confidence**: `Manual`
**Description**: The root of the `ai-agent-md-pack` repository.

## Detected Stacks
- **markdown**: Documentation and agent configuration files.
- **bash**: Helper scripts (e.g., `setup-antigravity.sh`).

## Capabilities
| Category | Command | Description |
| :--- | :--- | :--- |
| **Build** | *None* | No build required for this repo. |
| **Test** | *None* | No automated tests currently configured for root. |
| **Run** | `./setup-antigravity.sh` | Runs the setup script. |
| **Lint** | *None* | Markdown linting is manual/IDE-based. |

## Dependencies
- *None*

## Deploy / Release
- **Type**: `library` / `configuration-pack`
- **Release**: Tagging a new version in git.

## Dependencies
- **depends_on**: []

## Paths
- **owned_paths**:
    - `agent/components/*.md` (Component Definitions)
    - `agent/workflows/*.md` (Workflow Definitions)
    - `*.sh` (Root scripts)
    - `*.md` (Root documentation)

- **shared_paths**:
    - `agent/workflows/_stack/*.md` (Shared stack workflows)

