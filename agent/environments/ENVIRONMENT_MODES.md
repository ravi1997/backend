# Environment Modes

The agent operates in one of four restricted modes. This prevents catastrophic accidents (e.g., wiping a production DB or deleting local work) by enforcing strict rules based on the detected environment.

## Modes

| Mode | Context | Write Access | Dangerous Commands | Approval Required |
| :--- | :--- | :--- | :--- | :--- |
| **LOCAL_DEV** | Developer's Laptop | Full (Project Dir) | Warn Only | Low |
| **DOCKER_DEV** | Inside Dev Container | Full (Mounts) | Warn Only | Low |
| **CI** | GitHub Actions / Jenkins | Artifacts Only | **BLOCKED** | N/A (Automated) |
| **PROD_READONLY**| Production Server | **BLOCKED** | **BLOCKED** | **ALWAYS** |

---

## 1. LOCAL_DEV
**Heuristic**: Default if no other mode is detected.
-   **Assumption**: User is present, can undo git changes.
-   **Behavior**:
    -   Can edit files freely in the `CWD`.
    -   Warns before recursive deletes (`rm -rf`) outside `tmp/` or `build/`.
    -   Can run `npm install`, `pip install`, `make`.

## 2. DOCKER_DEV
**Heuristic**: `/.dockerenv` exists OR `DOCKER_CONTAINER=true` env var.
-   **Assumption**: Disposable environment, but might mount local source.
-   **Behavior**:
    -   Treats `/app` or `WORK_DIR` as mutable.
    -   Treats system paths (`/usr`, `/etc`) as mutable (it's a container).
    -   **CAUTION**: If user says "I mounted my home dir", downgrade safety to PROD_READONLY to be safe.

## 3. CI
**Heuristic**: `CI=true`, `GITHUB_ACTIONS=true`, `TRAVIS=true`.
-   **Assumption**: Non-interactive, ephemeral, high speed.
-   **Behavior**:
    -   **READ ONLY** for source code (unless explicitly running a lint-fixer workflow).
    -   **WRITE ALLOWED** only for `./dist`, `./build`, `./coverage`, `tmp/`.
    -   **BLOCK**: DB migrations, network tunneling, `docker run` (unless Docker-in-Docker is verified).

## 4. PROD_READONLY
**Heuristic**: `NODE_ENV=production`, `FLASK_ENV=production`, `KUBERNETES_PORT` exists (in some cases), or explicit config file.
-   **Assumption**: High stakes. Downtime or data loss is unacceptable.
-   **Behavior**:
    -   **STRICT READ-ONLY**. No file edits.
    -   **Commands**: Only safe "getters" allowed (e.g., `kubectl get`, `docker ps`, `grep`).
    -   **Action**: If a change is needed, the agent must **GENERATE A SCRIPT** or **DIFF** and ask the user to apply it, or ask for explicit "Run this exact command" approval.
