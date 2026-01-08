# Toolchain & Runtime Pinning Policy

To prevent "works on my machine" issues and CI failures, this repository enforces strict toolchain pinning.

## 1. Pinning Strategy

### Per-Component Pinning
In a polyglot monorepo, different components may require different runtime versions.
*   **Do NOT** assume a global version of Node, Python, Java, etc.
*   **ALWAYS** respect the pin file located in the `ACTIVE_SCOPE`.

### Priority Order
When resolving the required version for a tool, the agent must check files in this order:

1.  **Component Root** (e.g., `backend/api/.python-version`)
2.  **Repo Root** (e.g., `./.tool-versions`)
3.  **Agent Defaults** (See `agent/stacks/packs/<stack>/CONVENTIONS.md`)

## 2. Standard Pin Files

The agent should look for and respect the following standard files:

| Stack | Primary Pin File | Secondary / Legacy |
| :--- | :--- | :--- |
| **Universal** | `.tool-versions` (asdf/mise) | - |
| **Node/Web** | `.nvmrc` | `package.json` ("engines") |
| **Python** | `.python-version` (pyenv) | `pyproject.toml` |
| **Java** | `.java-version` | `pom.xml` / `build.gradle` |
| **Ruby** | `.ruby-version` | `Gemfile` |
| **Go** | `go.mod` | - |
| **Flutter** | `pubspec.yaml` (sdk: '>=...') | `.fvm/fvm_config.json` |

## 3. Policy: Unpinned Runtimes

If no version is pinned:
1.  **DETECT**: Log that the runtime is "UNPINNED".
2.  **WARN**: Inform the user that the operation is relying on the environment's default version.
3.  **SUGGEST**: Propose creating a pin file (e.g., `write_to_file .nvmrc`).

> [!IMPORTANT]
> In **Production** or **CI** modes, unpinned runtimes for critical languages (Java, Python, Node) should generate a stricter warning or potentially require confirmation if significant variance is possible.

## 4. Default Safe Minimums

If forced to guess or suggest a version, use these safe minimums (as of 2025):

-   **Node.js**: `20.0.0` (LTS)
-   **Python**: `3.11.0`
-   **Java**: `17` (LTS)
-   **Go**: `1.21`
-   **Flutter**: `3.16.0`

## 5. Usage in Workflows

Agents must verify the toolchain match **before** running install or build commands.

```bash
# Example verification step
if [ -f ".nvmrc" ]; then
  required=$(cat .nvmrc)
  current=$(node -v)
  if [[ "$current" != *"$required"* ]]; then
     echo "Version mismatch: Required $required, found $current"
     exit 1
  fi
fi
```
