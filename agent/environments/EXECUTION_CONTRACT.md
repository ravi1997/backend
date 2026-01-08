# Execution Contract

To ensure safety in monorepos and production environments, the agent operates under a strict **Execution Contract**. This contract determines *what* the agent is allowed to do at any given moment.

## Execution Levels

The agent must resolve its **Execution Level** before suggesting or running any commands.

| Level | Description | Allowed Actions | Typical Context |
| :--- | :--- | :--- | :--- |
| **PLAN_ONLY** | **Read-Only / Documentation** | Write docs, generate scripts, read files. NO system commands. | Production, Unfamiliar Monorepo, Default fallback. |
| **SAFE_LOCAL** | **Safe Development** | Compile, Lint, Test, Non-destructive file edits. | Local Dev, Docker Dev (Scoped). |
| **ELEVATED** | **Destructive / Admin** | DB Migrations, Infrastructure changes, `rm -rf`, `git clean`. | Explicit User Approval, CI (some ops). |

---

## Level Resolution Logic

The execution level is determined by the intersection of the **Environment Mode** (from `ENVIRONMENT_MODES.md`) and the **Active Scope**.

1.  **Check Environment**:
    *   `PROD_READONLY` -> **PLAN_ONLY** (Force).
    *   `CI` -> **SAFE_LOCAL** (Default), **ELEVATED** (only if credentials/tokens present).
    *   `LOCAL_DEV` / `DOCKER_DEV` -> **SAFE_LOCAL** (Default).

2.  **Check Scope**:
    *   If `ACTIVE_SCOPE` is unset or `root` -> **PLAN_ONLY** (Safety strictness for root).
    *   If `ACTIVE_SCOPE` is a specific component -> **SAFE_LOCAL**.

3.  **Check for Elevation**:
    *   To escalate to **ELEVATED**, an **Approval Token** must be present or explicitly granted by the user for the specific task.
    *   **Token Path**: `.agent/elevated_access_token` (Ephemeral, task-specific).

---

## Guidelines for Agents

### When in PLAN_ONLY
-   **DO NOT** propose `run_command` tools.
-   **DO** propose `write_to_file` for documentation or scripts.
-   **Goal**: Create a "Dry Run" or "Implementation Plan" for the user to execute manually.

### When in SAFE_LOCAL
-   **DO** run build, test, lint commands.
-   **DO** edit code files within the `ACTIVE_SCOPE`.
-   **BLOCK** commands that affect the global system (e.g., `npm install -g`, `pip install` without venv).

### When in ELEVATED
-   **DO** perform requested admin tasks.
-   **LOG** every destructive action with a rollback plan.
