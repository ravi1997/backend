# Project Context (Fill Once)

**Purpose:** Configure project-specific settings for AI agent
**When to use:** Once per project, during initial setup
**Prerequisites:** AI folder copied to project
**Outputs:** Configured AUTO_CONTEXT for agent use

---

## CRITICAL: Use Auto-Setup First

**Recommended:** Let the agent auto-detect everything:

```
User: "Setup AI folder for this project"
```

Agent will:
1. Detect project type (Python/C++/Java/etc.)
2. Find build system (CMake/Maven/npm/etc.)
3. Identify framework (Flask/Spring/React/etc.)
4. Fill ALL fields automatically
5. Report confidence level

**Manual setup only if auto-detection fails.**

---

## AUTO_CONTEXT (Universal Schema)

Copy/paste and edit. **Leave unknowns blank** - agent will infer.

```yaml
# CORE (Required)
app_name: "form-backend"
project_type: "python"
PRIMARY_STACK: "python"
env: "dev"

# STRUCTURE
repo_root: "."
source_dir: "app/"
build_dir: ""
test_dir: "tests/"

# BUILD
build_system: "pip"
build_cmd: "pip install -r requirements.txt"
clean_cmd: "find . -type d -name __pycache__ -exec rm -rf {} +"

# PACKAGE MANAGER
package_manager: "pip"
install_cmd: "pip install -r requirements.txt"

# RUNTIME
runtime: "python"
entrypoint: "run:app"
run_cmd: "python run.py"

# WEB (if applicable)
framework: "flask"
server_type: "gunicorn"
listen_host: "0.0.0.0"
app_port: 5000
health_path: "/api/v1/health"

# DATABASE (if applicable)
db_kind: "mongo"
migration_tool: "none"

# DOCKER (if applicable)
uses_docker: false
compose_file: ""
compose_backend_service: ""

# DEPLOYMENT (if applicable)
deployment_type: "gunicorn"
systemd_unit: ""

# TESTING
test_cmd: "pytest"
lint_cmd: "ruff check ."

# SECURITY
has_phi_pii: true
```

See [`contracts/UNIVERSAL_PROJECT_SCHEMA.md`](contracts/UNIVERSAL_PROJECT_SCHEMA.md) for complete schema.

---

## Validation Checklist

Agent MUST verify:
- [ ] `app_name` is filled (REQUIRED)
- [ ] `project_type` is set (REQUIRED)
- [ ] `env` is correct (dev/staging/production)
- [ ] All blank fields processed by autofill
- [ ] Confidence level calculated
- [ ] If uncertain about env → defaulted to production

---

## See Also

- [`skills/project_auto_setup.md`](skills/project_auto_setup.md) - Auto-detection
- [`autofill/PATH_AND_SERVICE_INFERENCE.md`](autofill/PATH_AND_SERVICE_INFERENCE.md) - Inference rules
- [`examples/example_project_context.md`](examples/example_project_context.md) - Examples