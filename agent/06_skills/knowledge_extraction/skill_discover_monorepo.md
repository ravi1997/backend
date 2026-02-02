# Skill: Monorepo & Polyglot Discovery

## Purpose

Identifying projects that contain multiple independent components or different languages in subdirectories.

## Procedure

1. **Recursive Root Scan**: Look for build markers (`package.json`, `pom.xml`, `requirements.txt`) in all directories up to depth 3.
2. **Component Mapping**:
   - If multiple markers found: Identify "Workspace" roots (e.g., `lerna.json`, `pnpm-workspace.yaml`, or just multiple folders).
   - Create a map of `Folder -> Stack -> Entrypoint`.
3. **Environment Isolation**:
   - Verify if each component has its own virtual environment or local `node_modules`.
   - Record the specific run commands for each subdirectory.
4. **State Update**: Write the topology to `agent/09_state/STACK_STATE.md` under a "Project Topology" section.

## Stop Condition

- Full map of all executable components in the repository is completed.
