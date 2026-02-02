# Quick Copy Blocks (Mobile-Friendly)

## Entrypoints (Main Workflows)

### 🆕 New Project

```
Use: prompts/by_entrypoint/new_project.txt
Goal: Start from scratch
Input: Project idea
Output: SRS + Architecture + Backlog
```

### 📂 Existing Project

```
Use: prompts/by_entrypoint/existing_project.txt
Goal: Work on existing code
Input: Task description
Output: Completed task + updated state
```

### 📝 SRS Only

```
Use: prompts/by_entrypoint/srs_only.txt
Goal: Documentation only
Input: Project idea
Output: Professional SRS
```

### 📋 Plan Only

```
Use: prompts/by_entrypoint/plan_only.txt
Goal: Roadmap from SRS
Input: Existing SRS
Output: Architecture + Backlog
```

### 💻 Implement Only

```
Use: prompts/by_entrypoint/implement_only.txt
Goal: Code features
Input: Approved backlog
Output: Working code + tests
```

### 🧪 Test Only

```
Use: prompts/by_entrypoint/test_only.txt
Goal: Validate quality
Input: Existing code
Output: Test results + coverage
```

### 🔒 Security Audit Only

```
Use: prompts/by_entrypoint/security_audit_only.txt
Goal: Security review
Input: Codebase
Output: Audit report + vulnerabilities
```

### 👀 PR Review Only

```
Use: prompts/by_entrypoint/pr_review_only.txt
Goal: Code review
Input: Diff/branch
Output: Review feedback
```

### 🚀 Release Only

```
Use: prompts/by_entrypoint/release_only.txt
Goal: Finalize release
Input: Stable branch
Output: Release notes + tag
```

---

## Scenarios (Specific Problems)

### 🐛 Bug Fix

```
Use: prompts/by_scenario/bug_fix.txt
When: Known bug
Risk: Medium
Output: Fix + tests + no regressions
```

### 🚨 Emergency Hotfix

```
Use: prompts/by_scenario/emergency_hotfix.txt
When: Production down
Risk: CRITICAL
Output: Immediate fix + post-mortem
```

### ♻️ Refactor

```
Use: prompts/by_scenario/refactor.txt
When: Code is messy
Risk: Low
Output: Cleaner code + same behavior
```

### 📦 Dependency Update

```
Use: prompts/by_scenario/dependency_update.txt
When: Update libraries
Risk: Medium
Output: Updated deps + tests pass
```

### ⚡ Performance Issue

```
Use: prompts/by_scenario/performance_investigation.txt
When: Slow code
Risk: Medium
Output: Optimized code + metrics
```

### 🗄️ Data Migration

```
Use: prompts/by_scenario/data_migration.txt
When: Schema change
Risk: HIGH
Output: Migration + backup + rollback plan
```

### 🏛️ Legacy Integration

```
Use: prompts/by_scenario/legacy_integration.txt
When: Old code
Risk: High
Output: Encapsulated legacy + tests
```

### 🎲 Flaky Test

```
Use: prompts/by_scenario/flaky_test.txt
When: Random test failures
Risk: Medium
Output: Stable test + 100% pass rate
```

### 🔄 Circular Dependency

```
Use: prompts/by_scenario/circular_dependency.txt
When: Import cycle
Risk: Medium
Output: Broken cycles + CI check
```

### 🌐 API Failure

```
Use: prompts/by_scenario/api_failure.txt
When: External API down
Risk: High
Output: Fallback + mocks + circuit breaker
```

### ⚖️ Conflict Resolution

```
Use: prompts/by_scenario/conflict_resolution.txt
When: Contradictory requirements
Risk: Medium
Output: Resolved conflict + updated SRS
```

### ❓ Ambiguous Input

```
Use: prompts/by_scenario/ambiguous_input.txt
When: Vague request
Risk: Low
Output: Clarified requirements
```

### 🌍 Multi-Env Config

```
Use: prompts/by_scenario/multi_env_config.txt
When: Dev/staging/prod
Risk: Medium
Output: Config system + no secrets leaked
```

---

## Quick Decision

```
New project?          → new_project.txt
Existing + unclear?   → existing_project.txt
Bug?                  → bug_fix.txt
Emergency?            → emergency_hotfix.txt
Slow?                 → performance_investigation.txt
Update libs?          → dependency_update.txt
Messy code?           → refactor.txt
DB change?            → data_migration.txt
Random test fails?    → flaky_test.txt
Just docs?            → srs_only.txt
Ready to ship?        → release_only.txt
```

---

## Copy-Paste Template

```
[Paste content of: prompts/by_[category]/[file].txt]

Additional Context:
- Project: [name/description]
- Current State: [what's done]
- Objective: [what you want]
- Constraints: [any limitations]
```

---

## Emergency Quick Start

**Production is down?**

1. Copy `prompts/by_scenario/emergency_hotfix.txt`
2. Add: Severity (P0), bug description, production tag
3. Paste into AI
4. Follow instructions
5. Run `security_audit_only.txt` after

**Don't know what to use?**

1. Copy `prompts/by_entrypoint/existing_project.txt`
2. Describe your situation
3. AI will route to correct scenario

---

## State Check (Always Do This)

After ANY prompt execution:

```
Check: agent/09_state/PROJECT_STATE.md
Verify: Current state value
Confirm: Artifacts created in plans/
```

If state wasn't updated → Something went wrong → Re-run with explicit state update request.
