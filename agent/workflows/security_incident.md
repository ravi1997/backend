# Meta-Workflow: Security Incident Response

**Purpose:** Handle security incidents and vulnerabilities.
**When to use:** Security issue detected (injection, breach, vulnerability).
**Prerequisites:** Logs, stack identified, P1-P4 assessment.
**Type:** Universal Meta-Workflow

---

## Workflow Contract

| Attribute | Details |
| :--- | :--- |
| **Inputs** | Incident report, Logs, `ACTIVE_SCOPE`, `PROJECT_FINGERPRINT` |
| **Outputs** | Contained incident, Patch |
| **Policy** | P1 incidents require immediate escalation. See `agent/security/SECRETS_POLICY.md` |
| **Stop Conditions** | False positive detected |

---

## Step 0: Context & Safety Setup

**Objective**: Secure the active scope and determine allowed actions (Execution Level).

### 1. Resolve Scope & Impact
Identify the component we are working on and valid impact.

```bash
# Set scope
export ACTIVE_SCOPE="${ACTIVE_SCOPE:-default}"

# Load scope rules
source agent/scripts/resolve_scope.sh "$ACTIVE_SCOPE"

# Check Component Graph for impact
source agent/workflows/monorepo_change_impact.md
```

### 2. Threat Model Checklist
Identify the threat model based on the stack:
- **Web/Python/Java (Backend):** SQL Injection, RCE, Deserialization.
- **Flutter/Mobile:** Insecure Storage, API Key Leakage, Jailbreak detection.
- **C++:** Buffer Overflow, Memory Corruption.
- **General:** Broken Auth, XSS (Frontend).

---

## Step 1: Contain (Universal)

1.  **Block:** IP ban.
2.  **Disable:** Turn off affected feature.
3.  **Rotate:** Change compromised keys (See `SECRETS_POLICY.md`).
4.  **Redact:** Remove raw secrets from logs/PRs immediately if found.

---

## Step 2: Investigate (Stack-Specific)

Refer to `agent/security/SECURITY_BASELINES.md` for tools and audit commands.

**Backend (SQLi):**
```bash
grep -i "union select" /var/log/nginx/access.log
```

**C++ (Segfault/Crash):**
Analyze core dump with `gdb`.

**Mobile:**
Check for unusual API traffic/patterns.

---

## Step 3: Fix & Patch (Universal)

1.  **Reproduce:** Create a test case (exploit).
2.  **Fix:** Patch the code.
    - If dependency issue: Follow **Remediation Playbook** in `SECURITY_BASELINES.md`.
3.  **Verify:** Run test case again (must fail).

---

## Step 4: Deploy & Monitor

1.  **Deploy:** Urgent hotfix.
2.  **Monitor:** Watch logs for attempts.

---

## Step 5: Post-Mortem & Rollback Plan

- **Rollback:** If hotfix causes regression, revert to previous commit and re-apply "Contain" steps (Disable feature) instead of patching.
- **Verify:** Ensure metrics return to normal.

---

## Completion Criteria

- ✅ Incident contained
- ✅ Vulnerability patched
- ✅ No new exploits observed
