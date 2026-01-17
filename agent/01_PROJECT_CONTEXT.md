# Project Context (Fill Once)

**Purpose:** Configure project-specific settings for AI agent.
**When to use:** Once per project, during initial setup.
**Outputs:** Configured AUTO_CONTEXT for agent use.

---

## 🚀 AUTO-SETUP (Recommended)

**"Setup AI folder for this project"**
The agent will:

1. Detect Language & Framework (Python, Node, Java, Go, etc.)
2. Find Build System (Maven, Gradle, CMake, NPM, etc.)
3. Identify Docker/Ports/Entrypoints.
4. Fill this file automatically.

---

## 📋 AUTO_CONTEXT (Universal Schema)

Copy/paste and edit. **Leave unknowns blank** - agent will infer.

```yaml

# ============================================

# 1. CORE IDENTITY

# ============================================

app_name: "backend"
project_type: "python"
env: "production"

# ============================================

# 2. STRUCTURE & BUILD

# ============================================

repo_root: "."            # usually "."
source_dir: "app"            # src/|app/|lib/|backend/
build_system: "python"          # cmake|gradle|maven|npm|poetry|cargo|go
package_manager: "pip"       # pip|npm|yarn|mvn|gradlew|go mod

# ============================================

# 3. RUNTIME & ENTRYPOINT

# ============================================

entrypoint: "run.py"            # main.py|index.js|App.java|main.go
run_cmd: "python run.py"               # "python app.py" | "npm start" | "./gradlew bootRun"
test_cmd: "pytest"              # "pytest" | "npm test" | "go test ./..."
app_port: 5000            # Internal port the app listens on

# ============================================

# 4. INFRASTRUCTURE (Docker/Deploy)

# ============================================

uses_docker: true        # true/false
compose_file: "docker-compose.yml"          # docker-compose.yml
compose_service_name: "linter"  # The main app service name in compose
deployment_type: "docker"       # docker|systemd|k8s|serverless

# ============================================

# 5. SECURITY

# ============================================

has_phi_pii: true         # Default true for safety (Redact logs)

```

See [`contracts/UNIVERSAL_PROJECT_SCHEMA.md`](contracts/UNIVERSAL_PROJECT_SCHEMA.md) for full details.

---

## ✅ Validation Checklist

Agent MUST verify:

- [ ] `app_name`, `project_type`, `env` are filled.
- [ ] `test_cmd` is valid for the stack.
- [ ] If `uses_docker: true`, `compose_file` is located.
