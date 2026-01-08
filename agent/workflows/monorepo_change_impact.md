# Monorepo: Change Impact Analysis

**Purpose**: Accurately identify which components are affected by a set of file changes.
**When to use**: Before running CI pipelines, planning releases, or validating PRs.
**Prerequisites**: `git`, `agent/COMPONENT_GRAPH.md` populated.
**Type**: Monorepo Workflow

---

## Workflow Contract

| Attribute | Details |
| :--- | :--- |
| **Inputs** | Changed Files List (Git diff) |
| **Outputs** | List of Affected Components |
| **Policy** | Conservative Mapping (If unsure, assume Global) |
| **Stop Conditions** | Git error, Corrupt Components Registry |

---

## Step 0: Refresh Registry

Ensure the component registry is up-to-date to avoid missing new components.

```bash
# Optional: run detection if files were added recently
# bash agent/scripts/detect_components.sh
cat agent/COMPONENT_GRAPH.md
```

---

## Step 1: Identify Changed Files

Capture the list of files modified in the scope of interest.

**For Pull Requests:**
```bash
git diff --name-only origin/main...HEAD > changed_files.txt
```

**For Local Work:**
```bash
git diff --name-only > changed_files.txt
# Include staged files
git diff --name-only --cached >> changed_files.txt
```

---

## Step 2: Component Mapping

**Objective**: Map each file in `changed_files.txt` to a Component ID from `agent/COMPONENT_GRAPH.md`.

**Algorithm**:
1. Load Map: Read `path` for each component in `agent/COMPONENT_GRAPH.md`.
2. Iterate: For each file `f`:
   - Find component `c` where `f` starts with `c.path`.
   - Select the match with the **longest** path (most specific).
   - If no match, assign to `root` (Global Impact).
3. Deduplicate: Produce a unique list of Component IDs.

**Example Scenarios**:
- File: `services/auth/src/User.ts` -> Component: `services/auth`
- File: `packages/ui-lib/Button.tsx` -> Component: `packages/ui-lib`
- File: `README.md` -> Component: `root`

---

## Step 3: Dependency Expansion (Optional)

**Objective**: Identify downstream consumers that must also be tested.

1. **Direct Changes**: List from Step 2.
2. **Dependents**:
   - For each directly changed component, find who imports/consumes it.
   - *Note: This requires a dependency graph (e.g., `agent/COMPONENT_GRAPH.md` or package manager tools like `nx graph` or `lerna ls`).*
3. **Total Scope**: Direct Changes + Dependents.

---

## Step 4: Generate Output

Export the list for use in CI or Release workflows.

**Format (JSON Example):**
```json
{
  "scope": "partial",
  "components": ["services/auth", "packages/ui-lib"],
  "includes_root": false
}
```

**Format (Env Var Example):**
```bash
export AFFECTED_COMPONENTS="services/auth packages/ui-lib"
```

---

## Completion Criteria

- ✅ List of changed files is complete.
- ✅ Every file is mapped to a Component or Root.
- ✅ Impact list is ready for consumption by `monorepo_ci_matrix.md` or `monorepo_release_component.md`.
