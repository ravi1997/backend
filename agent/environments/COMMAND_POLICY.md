# Command Policy

This policy dictates which commands are allowed based on the resolved **Execution Level** and **Stack**.

**Reference**:
-   [Execution Contract](EXECUTION_CONTRACT.md)
-   [Stack Safety Matrix](STACK_SAFETY_MATRIX.md)

---

## Policy Enforcement Algorithm

Before suggesting a usage of `run_command`:

1.  **Resolve Level**: Determine if we are `PLAN_ONLY`, `SAFE_LOCAL`, or `ELEVATED`.
2.  **Check Scope**: Ensure `ACTIVE_SCOPE` is set and valid.
    *   **Rule**: `cd <component_path>` is **REQUIRED** before any stack command.
3.  **Check Matrix**: Consult `STACK_SAFETY_MATRIX.md` for specific command risks.

---

## Allow/Deny Rules

### 1. Level: PLAN_ONLY
*   **ALLOW**:
    *   `ls`, `find`, `cat`, `grep` (Read-only info gathering).
    *   `echo` (to file), `mkdir` (for docs).
*   **DENY**:
    *   **ALL** other commands.
    *   Compilers, linters, test runners, package managers.
*   **Action**: If a user asks to run a command, **REFUSE** and offer to write a shell script instead.

### 2. Level: SAFE_LOCAL
*   **ALLOW**:
    *   **Build/Test**: `mvn compile`, `npm test`, `cargo build`, `flutter analyze`.
    *   **Formatting**: `npm run prettier` (if scoped to component).
    *   **File Ops**: `touch`, `rm` (files inside component only).
*   **DENY** (Elevated Required):
    *   **Global Installs**: `npm i -g`, `pip install` (system).
    *   **Cleaners**: `mvn clean`, `flutter clean` (unless necessary for build repair), `docker system prune`.
    *   **Destructive**: `rm -rf` on non-temp directories.
    *   **Infrastructure**: `terraform apply`, `kubectl apply`, `fly deploy`.

### 3. Level: ELEVATED
*   **ALLOW**:
    *   **All SAFE_LOCAL commands**.
    *   **Destructive**: `git clean -fdx`, `rm -rf`, `docker system prune`.
    *   **Deployment**: `deploy`, `migrate`, `kubectl apply`.
*   **REQUIREMENT**:
    *   Must verify **Approval Token** or explicit user confirmation in the chat.
    *   Must **LOG** the command and its expected impact.

---

## Dry-Run Equivalents

Whenever possible, use a dry-run flag to verify safety before execution.

| Command | Dry-Run Equivalent |
| :--- | :--- |
| `npm install` | `npm install --dry-run` |
| `pip install` | `pip install --dry-run` |
| `make clean` | `make -n clean` |
| `git clean -fdx` | `git clean -nfdx` |
| `kubectl apply -f .` | `kubectl apply -f . --dry-run=client` |
| `docker system prune`| N/A (Ask user first) |

---

## Logging & Auditing

Every `run_command` suggestion must be accompanied by a structured log note in the thought process:

```markdown
[COMMAND PROPOSAL]
Command: `npm install`
Scope: `frontend`
Level: SAFE_LOCAL
Risk: Low (Local scope)
Rollback: `rm -rf node_modules`
```
