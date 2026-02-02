# Prompt Selector - Decision Tree

## Quick Decision Flow

```
START
  │
  ├─ Is this a NEW project? ────────────────────────> new_project.txt
  │   (empty directory)
  │
  ├─ Is this an EXISTING project? ──┐
  │                                  │
  │                                  ├─ Need docs only? ──────────> srs_only.txt
  │                                  │
  │                                  ├─ Have SRS, need plan? ─────> plan_only.txt
  │                                  │
  │                                  ├─ Ready to code? ───────────> implement_only.txt
  │                                  │
  │                                  ├─ Need to test? ────────────> test_only.txt
  │                                  │
  │                                  ├─ Security review? ─────────> security_audit_only.txt
  │                                  │
  │                                  ├─ Review code changes? ─────> pr_review_only.txt
  │                                  │
  │                                  ├─ Ready to release? ────────> release_only.txt
  │                                  │
  │                                  └─ Specific problem? ────────> See Problem Matrix below
  │
  └─ Emergency/Production issue? ────────────────────> emergency_hotfix.txt
```

---

## Problem Matrix

| Problem | Prompt File | Risk Level |
|---------|-------------|------------|
| **Bug in code** | `bug_fix.txt` | Medium |
| **Production outage** | `emergency_hotfix.txt` | **CRITICAL** |
| **Code is messy** | `refactor.txt` | Low |
| **Slow performance** | `performance_investigation.txt` | Medium |
| **Need to update libraries** | `dependency_update.txt` | Medium |
| **Database schema change** | `data_migration.txt` | **HIGH** |
| **Working with old code** | `legacy_integration.txt` | High |
| **Tests fail randomly** | `flaky_test.txt` | Medium |
| **Circular import errors** | `circular_dependency.txt` | Medium |
| **External API down** | `api_failure.txt` | High |
| **Conflicting requirements** | `conflict_resolution.txt` | Medium |
| **Vague user request** | `ambiguous_input.txt` | Low |
| **Multiple environments** | `multi_env_config.txt` | Medium |

---

## Risk Level Guide

### **CRITICAL** (Emergency Only)

- Use `emergency_hotfix.txt`
- Bypasses normal workflows
- Requires post-mortem
- **Always** run security audit after

### **HIGH** (Proceed with Caution)

- Use scenario-specific prompt
- **Must** have backups (especially for `data_migration.txt`)
- **Must** test on staging first
- **Must** have rollback plan

### **Medium** (Standard Process)

- Use scenario-specific prompt
- Follow all gates
- Update state files
- Run tests

### **Low** (Safe)

- Use scenario-specific prompt
- Minimal risk
- Can iterate quickly

---

## Workflow Combinations

### **Full New Project Lifecycle**

1. `new_project.txt` → SRS + Architecture + Backlog
2. `implement_only.txt` → Build features
3. `test_only.txt` → Validate quality
4. `security_audit_only.txt` → Security review
5. `release_only.txt` → Production ready

### **Maintenance Cycle**

1. `existing_project.txt` → Understand codebase
2. `bug_fix.txt` OR `refactor.txt` → Fix issues
3. `test_only.txt` → Verify no regressions
4. `pr_review_only.txt` → Review changes

### **Emergency Response**

1. `emergency_hotfix.txt` → Fix immediately
2. `security_audit_only.txt` → Verify no new vulnerabilities
3. `test_only.txt` → Full regression check
4. Post-mortem (manual)

---

## Special Situations

### **Don't Know What You Need?**

→ Use `existing_project.txt` with a general description
→ AI will route to `ambiguous_input.txt` and help clarify

### **Multiple Problems at Once?**

→ Prioritize by risk level (CRITICAL → HIGH → MEDIUM → LOW)
→ Use one prompt at a time
→ Update state between each

### **AI Seems Confused?**

→ Check `agent/09_state/PROJECT_STATE.md`
→ Use `agent/00_system/08_context_management.md`
→ Start new session with state dump

---

## Release Readiness Checklist

Before using `release_only.txt`, verify:

- [ ] All features in milestone are complete
- [ ] `test_only.txt` shows 100% pass rate
- [ ] `security_audit_only.txt` shows no HIGH/CRITICAL issues
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is current
- [ ] All state files in `agent/09_state/` are accurate

If ANY checkbox is unchecked, use the corresponding prompt to fix it first.

---

## Mobile Quick Reference

### Starting Fresh?

→ `new_project.txt`

### Working on Existing?

→ `existing_project.txt`

### Emergency?

→ `emergency_hotfix.txt`

### Just Testing?

→ `test_only.txt`

### Just Security?

→ `security_audit_only.txt`

### Ready to Ship?

→ `release_only.txt`

---

## Advanced: Custom Routing

If you need to combine multiple scenarios:

1. Use `existing_project.txt` as the entry point
2. Specify: "Execute scenario X, then scenario Y"
3. The AI will chain them using the Agent OS framework

Example:

```
Use existing_project.txt

Objective: Update dependencies (scenario_dependency_update.md),
then run full security audit (scenario_security_audit_only.md),
then run all tests (run_test_only.md).
```

The AI will execute all three in sequence, updating state between each.
