# Meta-Workflow: Feature Delivery

**Purpose:** End-to-end framework for delivering new features across any stack.
**When to use:** When implementing new functionality from spec to production.
**Prerequisites:** Feature spec, codebase access, stack identified.
**Type:** Universal Meta-Workflow

---

## Workflow Contract

| Attribute | Details |
| :--- | :--- |
| **Inputs** | Feature Spec, `PROJECT_FINGERPRINT` |
| **Outputs** | Working feature, tests, PR, documentation |
| **Policy** | Must follow `../02_CONVENTIONS.md` |
| **Stop Conditions** | Missing spec, unknown stack, missing env |

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

# Switch to component directory (if applicable)
# cd components/${ACTIVE_SCOPE} 
```

### 2. Resolve Execution Level
Determine `PLAN_ONLY`, `SAFE_LOCAL`, or `ELEVATED` based on `agent/environments/EXECUTION_CONTRACT.md`.

```bash
# Detect Environment Mode
source agent/scripts/detect_environment.sh

# Determine Level
# Rule: PROD -> PLAN_ONLY. CI -> SAFE_LOCAL. DEV -> SAFE_LOCAL. 
#       To get ELEVATED, check for token: .agent/elevated_access_token

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
- **Read Matrix**: `agent/environments/STACK_SAFETY_MATRIX.md`

#### Stack Logic
- **C++:** `primary_language: cpp` → `_stack/cpp_feature_delivery.md`
- **Java:** `primary_language: java` → `_stack/java_feature_delivery.md`
- **Python:** `primary_language: python` → `_stack/python_feature_delivery.md`
- **Flutter:** `platform: flutter` → `_stack/flutter_feature_delivery.md`
- **Web:** `platform: web` → `_stack/web_feature_delivery.md`

---

## Step 1: Understand & Design (Universal)

### Role: Planner Checklist
- [ ] **Scope:** Is the feature clearly defined?
- [ ] **Acceptance Criteria:** Are they testable?
- [ ] **Risks:** Are there security or perf risks?
- [ ] **Dependencies:** Are all blockers resolved?

1.  **Understand Spec:** Fill out `agent/forms/FEATURE_MIN.md`.
2.  **Design:** Plan file changes, DB schema, API updates.
3.  **Plan:** Create an implementation plan with small steps.

---

## Step 2: Implementation & Testing (Stack-Specific)

Execute the subflow for your detected stack.

### Context: [INSERT STACK NAME]

**Refer to Subflow:**
[`_stack/[stack]_feature_delivery.md`](_stack/)

**Key Actions:**
1.  **Build:** Run build commands from subflow.
2.  **Test:** Run test commands from subflow.
3.  **Lint:** Run lint commands from subflow.

> [!IMPORTANT]
> If a step fails in the subflow, **STOP** and fix it before returning here.

---

## Step 3: QA Gates Enforcement (Universal)

**Reference:** `agent/quality/QA_GATES.md`

### Gate 1: Build & lint
- [ ] Build passes with NO warnings (Strict Mode).
- [ ] Linter is clean.

### Gate 2: Tests
- [ ] Unit tests pass (100%).
- [ ] Integration tests pass (if env available).
- [ ] *If env missing:* Added "Reproducible Setup" to PR.

### Gate 3: Security
- [ ] Dependency scan (e.g., `npm audit`) passes.
- [ ] No secrets in code.

---

## Step 4: Verify (Universal)

1.  **Manual Test:** Verify feature works as expected.
2.  **Review:** Self-review against `02_CONVENTIONS.md`.
3.  **Docs:** Update relevant documentation.

---

## Step 5: Package & Release (Universal)

### Role: Reviewer Checklist
Before merging, the Reviewer must confirm:
- [ ] **PR Size:** Is it reviewable? (Atomic commits).
- [ ] **Risks:** identified?
- [ ] **Evidence:** Screenshots/Logs attached?
- [ ] **Backwards Comp:** No breaking changes without major bump.

1.  **PR Summary:** Generate `artifacts/pr_summary.md`.
2.  **Create PR:** Submit for code review.
3.  **Merge:** Squash and merge after approval.
4.  **Release:** Follow `deploy_and_migrate.md`.

---

## Completion Criteria

- ✅ Planner: Spec & Plan defined.
- ✅ Developer: Implementation complete.
- ✅ Tester: QA Gates passed.
- ✅ Reviewer: PR approved.

## Rollback Plan

If issues arise:
1. Revert merge commit.
2. Deploy previous version (see `deploy_and_migrate.md`).
