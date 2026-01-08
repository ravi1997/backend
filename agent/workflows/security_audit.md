# Meta-Workflow: Security Audit & Hardening

**Purpose:** proactively scan the codebase for vulnerabilities, secrets, and security regressions.
**When to use:** On a schedule, before a major release, or when triggered by a CI event.
**Type:** Universal Meta-Workflow

---

## Workflow Contract

| Attribute | Details |
| :--- | :--- |
| **Inputs** | `ACTIVE_SCOPE`, `PROJECT_FINGERPRINT` |
| **Outputs** | Audit Report, Remediation Plan |
| **Policy** | Must follow `agent/security/SECURITY_BASELINES.md` and `SECRETS_POLICY.md` |
| **Stop Conditions** | Critical Vulnerability Found (stops release) |

---

## Step 0: Context & Safety Setup

**Objective**: Secure the active scope and determine allowed actions (Execution Level).

### 1. Resolve Scope
Identify the component we are working on.

```bash
# Set scope (must match a component in agent/components/)
export ACTIVE_SCOPE="${ACTIVE_SCOPE:-default}"

# Verify active scope
source agent/scripts/resolve_scope.sh "$ACTIVE_SCOPE"
```

### 2. Identify Impacted Components
If this audit is triggered by a change, determine which components are affected.

```bash
# (Optional) If running on a PR/Change
source agent/workflows/monorepo_change_impact.md
```

### 3. Stack Selection & Policy Check
- **Read Policy**: `agent/security/SECURITY_BASELINES.md`
- **Read Secrets Policy**: `agent/security/SECRETS_POLICY.md`

#### Stack Logic
- **C++:** `primary_language: cpp`
- **Java:** `primary_language: java`
- **Python:** `primary_language: python`
- **Flutter:** `platform: flutter`
- **Web:** `platform: web`

---

## Step 1: Secret Scanning (Universal)

**Objective**: Ensure no raw secrets are committed.

1.  **Scan Codebase**:
    *   Check for patterns defined in `SECRETS_POLICY.md` (Forbidden Patterns).
    *   Verify `.env` files are not committed (check `.gitignore`).
    *   Verify Keystores are not committed.

2.  **Verify Review**:
    *   Ensure no recent PR descriptions contain secrets.

---

## Step 2: Dependency Audit (Stack-Specific)

Execute the audit command for your detected stack as defined in `SECURITY_BASELINES.md`.

### Python
```bash
pip-audit --desc
```

### Node / Web
```bash
npm audit
# or
pnpm audit
```

### Java
```bash
./gradlew dependencyCheckAnalyze
```

### Flutter
```bash
flutter pub outdated
```

> [!IMPORTANT]
> If vulnerabilities are found, proceed to **Step 3: Remediation**.

---

## Step 3: Remediation & Fix

If issues are found, follow the **Remediation Playbook** in `SECURITY_BASELINES.md`.

1.  **Categorize**: Critical, High, Medium, Low.
2.  **Plan Fix**:
    *   Upgrade Dependency.
    *   Rotate Secret (if leaked).
    *   Apply Patch.
3.  **Execute Fix**: (Switch to `SAFE_LOCAL` or `ELEVATED` if needed).
4.  **Verify**: Re-run Step 2.

---

## Step 4: Verification & Rollback Preparation

1.  **Test Suite**: Run `make test` or stack equivalent to ensure the fix didn't break the app.
2.  **Rollback Plan**:
    *   If upgrading a dependency breaks the build, revert the `lock` file change.
    *   If a secret rotation fails, have the old key available for < 1h buffer (if provider allows) or ensure quick re-rotation.

---

## Completion Criteria

- ✅ No active secrets found in codebase.
- ✅ Dependency audit passes (or exemptions documented).
- ✅ Tests pass after any remediation.
