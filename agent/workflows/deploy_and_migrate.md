# Meta-Workflow: Deploy and Migrate

**Purpose:** Deploy application and run migrations for any stack.
**When to use:** Deploying new version to staging or production.
**Prerequisites:** Build artifact, target environment key.
**Type:** Universal Meta-Workflow

---

## Workflow Contract

| Attribute | Details |
| :--- | :--- |
| **Inputs** | Build artifact, `PROJECT_FINGERPRINT` |
| **Outputs** | Deployed app, updated DB |
| **Policy** | Zero-downtime (preferred), Backup required |
| **Stop Conditions** | Migration test failed, Backup failed |

---

## Step 0: Context & Safety Setup

**Objective**: Secure the active scope and determine allowed actions (Execution Level).

### 1. Resolve Scope
Identify the component we are working on.

```bash
# Set scope (must match a component in agent/components/)
export ACTIVE_SCOPE="${ACTIVE_SCOPE:-default}"

# Verify component exists
if [ ! -f "agent/components/${ACTIVE_SCOPE}.md" ]; then
  echo "Error: Component ${ACTIVE_SCOPE} not found."
  # create it or ask user
fi
```

### 2. Resolve Execution Level
Determine `PLAN_ONLY`, `SAFE_LOCAL`, or `ELEVATED` based on `agent/environments/EXECUTION_CONTRACT.md`.

```bash
# Detect Environment Mode
source agent/scripts/detect_environment.sh

# Determine Level
if [ "$ENV_MODE" == "PROD_READONLY" ]; then
  export EXECUTION_LEVEL="PLAN_ONLY"
elif [ -f ".agent/elevated_access_token" ]; then
  export EXECUTION_LEVEL="ELEVATED"
else
  export EXECUTION_LEVEL="SAFE_LOCAL"
fi

echo "Active Scope: $ACTIVE_SCOPE"
echo "Execution Level: $EXECUTION_LEVEL"
```

### 3. Stack Selection & Policy Check
- **Read Policy**: `agent/environments/COMMAND_POLICY.md`

#### Stack Strategy
- **Java:** Deploy JAR/WAR. Migrations via Flyway/Liquibase.
- **Python:** Deploy Wheel/Source. Migrations via Alembic/Django.
- **C++:** Deploy Binary. Migrations via custom tool.
- **Web:** Deploy Static/Node. No DB (usually) or API-driven.

---

## Step 1: Pre-Deployment Checks (Universal)

### Role: Tester Checklist
- [ ] **QA Gates:** All `agent/quality/QA_GATES.md` checks are Green.
- [ ] **CI Status:** Green on `main` branch.
- [ ] **Staging:** Verified on Staging environment (if applicable).
- [ ] **Rollback:** Plan is documented and feasible.

1.  **Tests:** Verify CI passed.
2.  **QA Gates:** Confirm all gates in `agent/quality/QA_GATES.md` are green.
3.  **Backup:** Run `pg_dump` or equivalent.
4.  **Tag:** Create git tag.

---

## Step 2: Packaging (Stack-Specific)

**Python:**
```bash
python -m build
```

**Java:**
```bash
./mvnw package -DskipTests
```

**Container (Universal):**
```bash
docker build -t myapp:latest .
```

---

## Step 3: Migration (Stack-Specific)

Execute the migration tool identified in Step 0.

**Alembic (Python):**
```bash
alembic upgrade head
```

**Flyway (Java):**
```bash
./mvnw flyway:migrate
```

---

## Step 4: Deploy & Verify (Universal)

1.  **Restart:** `systemctl restart` or `docker-compose up -d`.
2.  **Health:** Check `/healthz`.
3.  **Logs:** Monitor for errors.

---

## Completion Criteria

- ✅ App running on new version
- ✅ Database migrated
- ✅ Health checks pass

## Rollback Plan

See `rollback_recovery.md`.
