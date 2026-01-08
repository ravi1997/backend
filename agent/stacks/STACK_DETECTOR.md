# Stack Detection Logic

This document defines how the agent determines the technology stack of a project.

## Detection Precedence

1.  **Manual Override**: Check `agent/01_PROJECT_CONTEXT.md` for a `PRIMARY_STACK` field. If present and not empty, use it.
2.  **Monorepo Detection**: Check for root-level identifiers of monorepos (e.g., `nx.json`, `lerna.json`, `pnpm-workspace.yaml`, `turbo.json`, `bazel` files).
3.  **Specific Stack Detection**: Iterate through all available fingerprint signatures in `agent/stacks/fingerprints/`.

## Confidence Scoring

Each fingerprint match contributes to a confidence score (0.0 to 1.0).

-   **High Confidence (1.0)**: Found a definitive build definition (e.g., `pom.xml`, `package.json`, `go.mod`, `Cargo.toml`).
-   **Medium Confidence (0.6)**: Found dependency lock files without build definitions (e.g., `yarn.lock` only).
-   **Low Confidence (0.3)**: Found source files only (e.g., `*.py`, `*.js`) without project metadata.

## Thresholds

-   **Minimum Confidence for Automation**: `0.8` (80%).
    -   If confidence < 0.8, the agent MUST ask the user for confirmation or fallback to a generic "Universal" mode.

## Conflict Resolution

If multiple stacks are detected with high confidence (e.g., Python `pyproject.toml` AND Node `package.json`):
1.  **Check for "Sidecar" patterns**: Is one clearly auxiliary? (e.g., a `package.json` inside a `python` repo might just be for pre-commit hooks).
2.  **Monorepo logic**: Treat as a polyglot project. Identify the "Primary" stack based on the root directory or sheer volume of code if possible, or label as "Mixed".
3.  **User Prompt**: When in doubt, explicitly list conflicting evidence and ask the user to clarify the PRIMARY vs SECONDARY stack in `PROJECT_FINGERPRINT.md`.
