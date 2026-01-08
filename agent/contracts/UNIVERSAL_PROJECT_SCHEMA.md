# Contract: Universal Project Schema

**Purpose:** Define the universal schema that works for ANY project type

**Supported Project Types:**
- Python (Flask, FastAPI, Django, etc.)
- Node.js (Express, Next.js, React, Vue, etc.)
- Java (Spring Boot, Maven, Gradle)
- C/C++ (CMake, Makefile)
- Go (modules)
- Rust (Cargo)
- Flutter/Dart
- HTML/CSS/JavaScript (static sites)
- Mobile (Android, iOS)
- Any other language/framework

---

## Universal AUTO_CONTEXT Schema

```yaml
# ============================================
# CORE IDENTIFICATION (Required for all)
# ============================================
app_name: ""              # Application name
project_type: ""          # python|nodejs|java|cpp|go|rust|flutter|static|mobile|other
env: "dev"                # dev|staging|production

# ============================================
# PROJECT STRUCTURE (Language-agnostic)
# ============================================
repo_root: "."            # Repository root directory
source_dir: ""            # Main source code directory (src/, app/, lib/, etc.)
build_dir: ""             # Build output directory (dist/, build/, target/, etc.)
test_dir: ""              # Test directory (tests/, test/, __tests__/, etc.)

# ============================================
# BUILD SYSTEM (Auto-detected)
# ============================================
build_system: ""          # cmake|makefile|maven|gradle|cargo|npm|pip|uv|flutter|none
build_file: ""            # CMakeLists.txt|Makefile|pom.xml|build.gradle|Cargo.toml|package.json|pyproject.toml
build_cmd: ""             # Command to build project
clean_cmd: ""             # Command to clean build artifacts

# ============================================
# PACKAGE MANAGER (Auto-detected)
# ============================================
package_manager: ""       # pip|uv|npm|yarn|pnpm|maven|gradle|cargo|pub|none
package_file: ""          # requirements.txt|pyproject.toml|package.json|pom.xml|Cargo.toml|pubspec.yaml
install_cmd: ""           # Command to install dependencies

# ============================================
# RUNTIME/EXECUTION (Language-specific)
# ============================================
runtime: ""               # python|node|java|gcc|go|rustc|dart|browser
runtime_version: ""       # Version of runtime (e.g., "3.11", "18.x", "17")
entrypoint: ""            # Main entry file/class/function
run_cmd: ""               # Command to run the application

# ============================================
# WEB SERVER (If applicable)
# ============================================
framework: ""             # flask|fastapi|express|spring|none
server_type: ""           # gunicorn|uvicorn|node|tomcat|nginx|none
listen_host: "0.0.0.0"
app_port: 8000
health_path: "/healthz"

# ============================================
# FRONTEND (If applicable)
# ============================================
frontend_framework: ""    # react|vue|angular|flutter|none
frontend_dir: ""          # frontend/|client/|ui/|none
frontend_build_cmd: ""    # npm run build|flutter build|none
frontend_dev_cmd: ""      # npm run dev|flutter run|none

# ============================================
# DATABASE (If applicable)
# ============================================
db_kind: ""               # postgres|mysql|sqlite|mongo|none
db_url_env: "DATABASE_URL"
migration_tool: ""        # alembic|flyway|liquibase|sequelize|none

# ============================================
# CONTAINERIZATION (If applicable)
# ============================================
uses_docker: false        # true|false
compose_file: ""          # docker-compose.yml|docker-compose.yaml|none
dockerfile: ""            # Dockerfile|Dockerfile.prod|none
compose_backend_service: ""
compose_frontend_service: ""
compose_nginx_service: ""

# ============================================
# DEPLOYMENT (If applicable)
# ============================================
deployment_type: ""       # docker|systemd|kubernetes|serverless|manual|none
systemd_unit: ""          # myapp.service|none
systemd_user: ""          # www-data|ubuntu|none
systemd_workdir: ""       # /opt/myapp|none

# ============================================
# REVERSE PROXY (If applicable)
# ============================================
uses_proxy: false         # true|false
proxy_type: ""            # nginx|apache|caddy|none
nginx_port: 80
nginx_config: ""          # /etc/nginx/sites-available/myapp|none
nginx_access_log: ""
nginx_error_log: ""

# ============================================
# LOGGING (Universal)
# ============================================
log_location: ""          # file path|journald|stdout|none
log_level: "INFO"         # DEBUG|INFO|WARNING|ERROR

# ============================================
# TESTING (Universal)
# ============================================
test_framework: ""        # pytest|jest|junit|gtest|cargo-test|flutter-test|none
test_cmd: ""              # pytest|npm test|mvn test|cargo test|flutter test
coverage_cmd: ""          # pytest --cov|npm run coverage|none

# ============================================
# CODE QUALITY (Universal)
# ============================================
linter: ""                # ruff|eslint|checkstyle|clang-tidy|clippy|none
formatter: ""             # ruff|prettier|google-java-format|clang-format|rustfmt|none
lint_cmd: ""              # ruff check .|npm run lint|mvn checkstyle:check
format_cmd: ""            # ruff format .|npm run format|mvn formatter:format

# ============================================
# CI/CD (If applicable)
# ============================================
ci_platform: ""           # github-actions|gitlab-ci|jenkins|circle-ci|none
ci_config: ""             # .github/workflows/ci.yml|.gitlab-ci.yml|none

# ============================================
# DOMAIN/URLS (Environment-specific)
# ============================================
domain: ""                # localhost:8000|myapp.com
dev_url: ""
staging_url: ""
production_url: ""

# ============================================
# SECURITY (Universal)
# ============================================
has_phi_pii: true         # true|false (default true for safety)
secret_manager: ""        # env-file|vault|aws-secrets|none
env_file: ""              # .env|.env.local|none
```

---

## Field Descriptions

### Core Identification

| Field | Description | Examples |
|-------|-------------|----------|
| `app_name` | Application name | "my-app", "user-service" |
| `project_type` | Primary language/platform | python, nodejs, java, cpp, flutter |
| `env` | Current environment | dev, staging, production |

### Build System

| Field | Description | Examples |
|-------|-------------|----------|
| `build_system` | Build tool used | cmake, maven, npm, cargo |
| `build_cmd` | Command to build | "cmake --build build", "mvn package" |
| `clean_cmd` | Command to clean | "make clean", "mvn clean" |

### Package Manager

| Field | Description | Examples |
|-------|-------------|----------|
| `package_manager` | Dependency manager | pip, uv, npm, maven, cargo |
| `install_cmd` | Install dependencies | "pip install -r requirements.txt", "npm install" |

### Runtime

| Field | Description | Examples |
|-------|-------------|----------|
| `runtime` | Runtime environment | python, node, java, gcc |
| `entrypoint` | Main entry point | "main.py", "Main.java", "main.cpp" |
| `run_cmd` | Command to run app | "python main.py", "java -jar app.jar" |

---

## Language-Specific Examples

### Python (Flask)
```yaml
project_type: "python"
build_system: "pip"
package_manager: "pip"
runtime: "python"
framework: "flask"
entrypoint: "wsgi:app"
test_cmd: "pytest"
lint_cmd: "ruff check ."
```

### Python (UV-based)
```yaml
project_type: "python"
build_system: "uv"
package_manager: "uv"
runtime: "python"
install_cmd: "uv pip install -r requirements.txt"
run_cmd: "uv run python main.py"
```

### C++ (CMake)
```yaml
project_type: "cpp"
build_system: "cmake"
build_file: "CMakeLists.txt"
build_cmd: "cmake --build build"
runtime: "gcc"
entrypoint: "build/myapp"
test_cmd: "ctest"
```

### Java (Maven)
```yaml
project_type: "java"
build_system: "maven"
build_file: "pom.xml"
build_cmd: "mvn package"
runtime: "java"
entrypoint: "target/myapp.jar"
test_cmd: "mvn test"
```

### Flutter
```yaml
project_type: "flutter"
build_system: "flutter"
package_manager: "pub"
package_file: "pubspec.yaml"
build_cmd: "flutter build"
run_cmd: "flutter run"
test_cmd: "flutter test"
```

### Static HTML/CSS/JS
```yaml
project_type: "static"
build_system: "none"
runtime: "browser"
source_dir: "src"
build_dir: "dist"
frontend_framework: "none"
```

---

## Validation Rules

### Required Fields (All Projects)
- `app_name` - Must be set
- `project_type` - Must be set
- `env` - Must be dev|staging|production

### Conditional Requirements

**If `uses_docker == true`:**
- `compose_file` OR `dockerfile` must be set

**If `project_type == python`:**
- `package_manager` must be pip|uv|poetry|conda

**If `project_type == cpp`:**
- `build_system` must be cmake|makefile|meson

**If `project_type == java`:**
- `build_system` must be maven|gradle

**If web application:**
- `app_port` must be set
- `framework` should be set

---

## Auto-Detection Priority

1. **Project Type:** Detect from file extensions and config files
2. **Build System:** Detect from build config files
3. **Package Manager:** Detect from dependency files
4. **Framework:** Detect from dependencies
5. **Runtime:** Infer from project type

---

## See Also

- [`../skills/project_auto_setup.md`](../skills/project_auto_setup.md) - Auto-detection logic
- [`REPO_LAYOUT_*.md`](.) - Language-specific layouts
