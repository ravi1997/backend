# Skill: Automated Project Analysis & AI Folder Setup

**Purpose:** Automatically analyze any project and fill in the AI folder configuration without user input

**When to use:** When copying the `agent/` folder into a new project for the first time

**Prerequisites:** 
- `agent/` folder has been copied to project root
- Agent has read access to project files

**Outputs:** Fully configured `01_PROJECT_CONTEXT.md` with all inferred values

---

## Overview

This skill enables the AI agent to:
1. Analyze any project (Python, Node.js, Java, Go, etc.)
2. Detect framework, structure, and configuration
3. Automatically fill `01_PROJECT_CONTEXT.md`
4. Validate the configuration
5. Report confidence level

**User does nothing** - agent does everything.

---

## Step 1: Project Detection

### 1.1 Detect Project Type

Run these checks in order:

```bash
# Check for Python project
if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] || [ -f "setup.py" ]; then
    PROJECT_TYPE="python"
fi

# Check for Node.js project
if [ -f "package.json" ]; then
    PROJECT_TYPE="nodejs"
fi

# Check for Java project
if [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
    PROJECT_TYPE="java"
fi

# Check for Go project
if [ -f "go.mod" ]; then
    PROJECT_TYPE="go"
fi

# Check for Ruby project
if [ -f "Gemfile" ]; then
    PROJECT_TYPE="ruby"
fi

# Check for PHP project
if [ -f "composer.json" ]; then
    PROJECT_TYPE="php"
fi

# Check for Flutter project
if [ -f "pubspec.yaml" ]; then
    PROJECT_TYPE="flutter"
fi

# Check for C++ project
if [ -f "CMakeLists.txt" ] || [ -f "Makefile" ] || [ -f "main.cpp" ]; then
    PROJECT_TYPE="cpp"
fi
```

**Output:** Set `PROJECT_TYPE` variable

---

## Step 2: Framework Detection

### 2.1 Python Frameworks

```bash
# Check requirements.txt or pyproject.toml
grep -i "flask" requirements.txt pyproject.toml 2>/dev/null && FRAMEWORK="Flask"
grep -i "fastapi" requirements.txt pyproject.toml 2>/dev/null && FRAMEWORK="FastAPI"
grep -i "django" requirements.txt pyproject.toml 2>/dev/null && FRAMEWORK="Django"
```

### 2.2 Node.js Frameworks

```bash
# Check package.json
grep -i "\"express\"" package.json && FRAMEWORK="Express"
grep -i "\"next\"" package.json && FRAMEWORK="Next.js"
grep -i "\"react\"" package.json && FRAMEWORK="React"
grep -i "\"vue\"" package.json && FRAMEWORK="Vue"
grep -i "\"nestjs\"" package.json && FRAMEWORK="NestJS"
```

### 2.3 Other Frameworks

```bash
# Java
grep -i "spring-boot" pom.xml && FRAMEWORK="Spring Boot"

# Go
grep -i "gin-gonic" go.mod && FRAMEWORK="Gin"
grep -i "fiber" go.mod && FRAMEWORK="Fiber"

# Ruby
grep -i "rails" Gemfile && FRAMEWORK="Rails"

# Flutter
if [ "$PROJECT_TYPE" = "flutter" ]; then
    FRAMEWORK="Flutter"
fi

# C++
if [ -f "CMakeLists.txt" ]; then
    BUILD_SYSTEM="cmake"
elif [ -f "Makefile" ]; then
    BUILD_SYSTEM="make"
fi
```

**Output:** Set `FRAMEWORK` variable

---

## Step 3: Structure Analysis

### 3.1 Find Application Root

```bash
# Python
if [ -f "app.py" ]; then APP_ROOT="."; fi
if [ -f "wsgi.py" ]; then APP_ROOT="."; fi
if [ -d "app/" ] && [ -f "app/__init__.py" ]; then APP_ROOT="."; PACKAGE="app"; fi
if [ -d "backend/" ]; then APP_ROOT="backend"; fi
if [ -d "server/" ]; then APP_ROOT="server"; fi

# Node.js
if [ -f "server.js" ]; then APP_ROOT="."; fi
if [ -f "index.js" ]; then APP_ROOT="."; fi
if [ -d "src/" ]; then APP_ROOT="src"; fi
```

### 3.2 Find Frontend Directory

```bash
# Check for frontend
if [ -d "frontend/" ]; then FRONTEND_DIR="frontend"; fi
if [ -d "client/" ]; then FRONTEND_DIR="client"; fi
if [ -d "ui/" ]; then FRONTEND_DIR="ui"; fi

# Check if it's a monorepo
if [ -f "frontend/package.json" ] || [ -f "client/package.json" ]; then
    HAS_FRONTEND="yes"
else
    FRONTEND_DIR="none"
fi
```

### 3.3 Detect Entry Point

```bash
# Python
if [ -f "wsgi.py" ]; then ENTRYPOINT="wsgi:app"; fi
if [ -f "app.py" ]; then ENTRYPOINT="app:app"; fi
if [ -f "$PACKAGE/wsgi.py" ]; then ENTRYPOINT="$PACKAGE.wsgi:app"; fi

# Node.js
if [ -f "server.js" ]; then ENTRYPOINT="server.js"; fi
if [ -f "index.js" ]; then ENTRYPOINT="index.js"; fi
if [ -f "src/index.js" ]; then ENTRYPOINT="src/index.js"; fi
```

**Output:** Set `APP_ROOT`, `FRONTEND_DIR`, `ENTRYPOINT`, `PACKAGE`

---

## Step 4: Infrastructure Detection

### 4.1 Docker Detection

```bash
# Check for Docker
if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
    HAS_DOCKER="yes"
    COMPOSE_FILE=$(ls docker-compose.y*ml 2>/dev/null | head -1)
    
    # Parse service names
    BACKEND_SERVICE=$(grep -A 5 "services:" $COMPOSE_FILE | grep -E "^\s+\w+:" | grep -v "nginx\|postgres\|redis" | head -1 | tr -d ' :')
    NGINX_SERVICE=$(grep -E "^\s+nginx:" $COMPOSE_FILE | tr -d ' :')
    
    # Get ports
    APP_PORT=$(grep -A 10 "$BACKEND_SERVICE:" $COMPOSE_FILE | grep "ports:" -A 1 | grep -oE "[0-9]+:[0-9]+" | cut -d: -f2)
fi
```

### 4.2 Systemd Detection

```bash
# Check for systemd service files
if [ -d "systemd/" ] || [ -d "deploy/" ]; then
    SERVICE_FILE=$(find systemd/ deploy/ -name "*.service" 2>/dev/null | head -1)
    if [ -n "$SERVICE_FILE" ]; then
        SYSTEMD_UNIT=$(basename "$SERVICE_FILE")
    fi
fi
```

### 4.3 Nginx Detection

```bash
# Check for nginx config
if [ -d "nginx/" ]; then
    NGINX_CONFIG=$(find nginx/ -name "*.conf" 2>/dev/null | head -1)
fi
```

**Output:** Set `HAS_DOCKER`, `COMPOSE_FILE`, `BACKEND_SERVICE`, `NGINX_SERVICE`, `APP_PORT`, `SYSTEMD_UNIT`

---

## Step 5: Database Detection

### 5.1 Detect Database Type

```bash
# Python
grep -i "psycopg2\|postgresql" requirements.txt && DB_KIND="postgres"
grep -i "mysql" requirements.txt && DB_KIND="mysql"
grep -i "sqlite" requirements.txt && DB_KIND="sqlite"
grep -i "pymongo" requirements.txt && DB_KIND="mongo"

# Node.js
grep -i "\"pg\"" package.json && DB_KIND="postgres"
grep -i "\"mysql\"" package.json && DB_KIND="mysql"
grep -i "\"mongodb\"" package.json && DB_KIND="mongo"

# Check docker-compose
if [ -f "$COMPOSE_FILE" ]; then
    grep -i "postgres:" $COMPOSE_FILE && DB_KIND="postgres"
    grep -i "mysql:" $COMPOSE_FILE && DB_KIND="mysql"
    grep -i "mongodb:" $COMPOSE_FILE && DB_KIND="mongo"
fi
```

### 5.2 Detect Migration Tool

```bash
# Python
grep -i "alembic" requirements.txt && MIGRATION_TOOL="alembic"
grep -i "flask-migrate" requirements.txt && MIGRATION_TOOL="flask-migrate"

# Node.js
grep -i "\"knex\"" package.json && MIGRATION_TOOL="knex"
grep -i "\"sequelize\"" package.json && MIGRATION_TOOL="sequelize"
grep -i "\"typeorm\"" package.json && MIGRATION_TOOL="typeorm"
```

**Output:** Set `DB_KIND`, `MIGRATION_TOOL`

---

## Step 6: Environment Detection

### 6.1 Detect Current Environment

```bash
# Check environment variables
if [ -f ".env" ]; then
    ENV=$(grep -i "^ENV=" .env | cut -d= -f2 | tr -d '"')
fi

# Check hostname patterns
HOSTNAME=$(hostname)
if echo "$HOSTNAME" | grep -iq "prod\|production"; then
    ENV="production"
elif echo "$HOSTNAME" | grep -iq "staging\|stg"; then
    ENV="staging"
else
    ENV="dev"
fi

# Check git branch (if in git repo)
if [ -d ".git" ]; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
        ENV="production"
    elif [ "$BRANCH" = "staging" ]; then
        ENV="staging"
    else
        ENV="dev"
    fi
fi
```

**Output:** Set `ENV`

---

## Step 7: Application Name Detection

### 7.1 Infer Application Name

```bash
# Priority order:
# 1. From package.json name
if [ -f "package.json" ]; then
    APP_NAME=$(grep -m 1 "\"name\":" package.json | cut -d'"' -f4)
fi

# 2. From pyproject.toml name
if [ -f "pyproject.toml" ]; then
    APP_NAME=$(grep -m 1 "^name = " pyproject.toml | cut -d'"' -f2)
fi

# 3. From directory name
if [ -z "$APP_NAME" ]; then
    APP_NAME=$(basename "$PWD")
fi

# Clean up name (remove special chars, lowercase)
APP_NAME=$(echo "$APP_NAME" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]-_')
```

**Output:** Set `APP_NAME`

---

## Step 8: Testing & Linting Detection

### 8.1 Detect Test Framework

```bash
# Python
grep -i "pytest" requirements.txt && TEST_CMD="pytest -q"
grep -i "unittest" requirements.txt && TEST_CMD="python -m unittest"

# Node.js
grep -i "\"jest\"" package.json && TEST_CMD="npm test"
grep -i "\"mocha\"" package.json && TEST_CMD="npm test"

# Java
if [ -f "pom.xml" ]; then TEST_CMD="./mvnw test"; fi
if [ -f "build.gradle" ]; then TEST_CMD="./gradlew test"; fi

# C++
if [ "$BUILD_SYSTEM" = "cmake" ]; then TEST_CMD="ctest --test-dir build"; fi

# Flutter
if [ "$PROJECT_TYPE" = "flutter" ]; then TEST_CMD="flutter test"; fi
```

### 8.2 Detect Linter/Formatter

```bash
# Python
grep -i "ruff" requirements.txt && LINT_CMD="ruff check . && ruff format ."
grep -i "black" requirements.txt && LINT_CMD="black . && flake8 ."

# Node.js
grep -i "\"eslint\"" package.json && LINT_CMD="npm run lint"
grep -i "\"prettier\"" package.json && LINT_CMD="npm run format"
```

**Output:** Set `TEST_CMD`, `LINT_CMD`

---

## Step 9: Generate Configuration

### 9.1 Fill AUTO_CONTEXT Block

Create the YAML configuration:

```yaml
app_name: "$APP_NAME"
env: "$ENV"
domain: "localhost:${APP_PORT:-8000}"
repo_root: "."
backend_dir: "$APP_ROOT"
frontend_dir: "$FRONTEND_DIR"
python_package: "$PACKAGE"
entrypoint: "$ENTRYPOINT"
listen_host: "0.0.0.0"
app_port: ${APP_PORT:-8000}
nginx_port: 80
health_path: "/healthz"

compose_file: "$COMPOSE_FILE"
compose_project: "$APP_NAME"
compose_backend_service: "$BACKEND_SERVICE"
compose_frontend_service: ""
compose_nginx_service: "$NGINX_SERVICE"

systemd_unit: "$SYSTEMD_UNIT"
systemd_user: "www-data"
systemd_workdir: "/opt/$APP_NAME"

nginx_access_log: "/var/log/nginx/access.log"
nginx_error_log: "/var/log/nginx/error.log"
app_log: "journald"

db_kind: "$DB_KIND"
db_url_env: "DATABASE_URL"
migration_tool: "$MIGRATION_TOOL"

test_cmd: "$TEST_CMD"
lint_cmd: "$LINT_CMD"
```

### 9.2 Write to 01_PROJECT_CONTEXT.md

Replace the AUTO_CONTEXT block in `agent/01_PROJECT_CONTEXT.md` with the generated values.

---

## Step 10: Validation & Confidence Scoring

### 10.1 Calculate Confidence Score

```python
confidence = 0
max_score = 100

# Critical fields (60 points)
if app_name: confidence += 10
if env: confidence += 10
if backend_dir: confidence += 10
if entrypoint: confidence += 10
if app_port: confidence += 10
if framework: confidence += 10

# Important fields (30 points)
if db_kind: confidence += 10
if test_cmd: confidence += 10
if lint_cmd: confidence += 10

# Nice-to-have (10 points)
if compose_file: confidence += 5
if systemd_unit: confidence += 5

confidence_percent = (confidence / max_score) * 100
```

### 10.2 Confidence Levels

- **90-100%:** HIGH - Proceed automatically
- **70-89%:** MEDIUM - Show user and ask for confirmation
- **<70%:** LOW - Ask user to fill manually

### 10.3 Report to User

```markdown
## Auto-Setup Complete

**Confidence:** [HIGH/MEDIUM/LOW] (XX%)

**Detected:**
- Project Type: [Python/Node.js/etc.]
- Framework: [Flask/Express/etc.]
- Database: [postgres/mysql/etc.]
- Environment: [dev/staging/production]

**Filled Fields:**
- ✅ app_name: "$APP_NAME"
- ✅ env: "$ENV"
- ✅ backend_dir: "$APP_ROOT"
- ✅ entrypoint: "$ENTRYPOINT"
- ✅ app_port: $APP_PORT
[... list all filled fields ...]

**Missing/Uncertain:**
- ⚠️ [field]: Could not detect, left blank
[... list uncertain fields ...]

**Next Steps:**
1. Review `agent/01_PROJECT_CONTEXT.md`
2. Fill any missing fields manually
3. Run: `agent/00_INDEX.md` to start using AI agent
```

---

## Step 11: Language-Specific Adaptations

### 11.1 Python Projects

Additional checks:
- Virtual environment location
- WSGI server (gunicorn/uvicorn)
- Async framework (asyncio/trio)

### 11.2 Node.js Projects

Additional checks:
- Package manager (npm/yarn/pnpm)
- Build tool (webpack/vite/rollup)
- TypeScript vs JavaScript

### 11.3 Java Projects

Additional checks:
- Build tool (Maven/Gradle)
- Application server (Tomcat/Jetty)
- Spring Boot profiles

### 11.4 Go Projects

Additional checks:
- Module name from go.mod
- Binary name
- Build tags

---

## Usage Example

### User Command

```
"Setup AI folder for this project"
```

### Agent Response

```markdown
Analyzing project...

✅ Detected Python Flask application
✅ Found docker-compose.yml with services
✅ Detected PostgreSQL database
✅ Found pytest and ruff

Auto-filling agent/01_PROJECT_CONTEXT.md...

**Confidence: HIGH (95%)**

Configuration complete! Here's what I found:
- App: eye-donation-pledge
- Framework: Flask 3.0
- Database: PostgreSQL
- Environment: dev
- Entry point: wsgi:app
- Port: 8000

Review agent/01_PROJECT_CONTEXT.md to verify.
Ready to use! Try: "fix this error: [paste error]"
```

---

## Error Handling

### If Detection Fails

```markdown
⚠️ **Auto-setup confidence: LOW (45%)**

I could only detect:
- Project type: Python
- Some dependencies

Please manually fill:
1. Open `agent/01_PROJECT_CONTEXT.md`
2. Fill the AUTO_CONTEXT block
3. See `agent/examples/example_project_context.md` for reference

Or provide more info:
- What framework are you using?
- What's your application entry point?
- What database are you using?
```

---

## Validation Checklist

Before marking auto-setup complete:

- [ ] `app_name` is set and valid
- [ ] `env` is detected correctly
- [ ] `backend_dir` points to actual code
- [ ] `entrypoint` exists and is correct
- [ ] If Docker: service names are correct
- [ ] If database: db_kind matches actual DB
- [ ] Confidence score calculated
- [ ] User notified of results

---

## See Also

- [`autofill/PATH_AND_SERVICE_INFERENCE.md`](../autofill/PATH_AND_SERVICE_INFERENCE.md) - Inference rules
- [`01_PROJECT_CONTEXT.md`](../01_PROJECT_CONTEXT.md) - Configuration template
- [`examples/example_project_context.md`](../examples/example_project_context.md) - Example
