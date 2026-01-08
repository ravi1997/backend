# Quality Gates (Must Pass Before "Done")

**Purpose:** Ensure all work meets quality standards before completion
**When to use:** Before marking any task as complete
**Prerequisites:** Work has been completed
**Enforcement:** MANDATORY - cannot skip

---

## CRITICAL: No Shortcuts

**ALL gates must pass before saying "done"**

If a gate fails:
1. Fix the issue
2. Re-run the gate
3. Repeat until pass

**Never skip a gate. Never.**

---

## Gate 1: Evidence Collection

**Applies to:** Incidents, bugs, errors

### Pass Criteria
- [ ] Correct checklist was used (nginx/docker/systemd/migration/perf)
- [ ] All checklist commands were run
- [ ] Output was captured and analyzed
- [ ] Evidence is cited in response

### Commands to Run
```bash
# Example for nginx 502
systemctl status nginx
systemctl status myapp
journalctl -u myapp -n 50
tail -n 100 /var/log/nginx/error.log
curl -I http://localhost:8000/healthz
```

### Validation
Agent must answer:
- "Which checklist did I use?" → Must name specific file
- "What evidence did I collect?" → Must cite actual output
- "Did I run all commands?" → Must be yes

### If Failed
- Go back and run the checklist
- Collect all required evidence
- Do not proceed with fix until evidence is complete

---

## Gate 2: Root Cause Analysis

**Applies to:** All incidents and bugs

### Pass Criteria
- [ ] Root cause is stated clearly
- [ ] Root cause is based on evidence (not guesses)
- [ ] Contributing factors identified
- [ ] Symptoms vs cause are distinguished

### Validation
Agent must answer:
- "What is the root cause?" → Must be specific, not vague
- "What evidence supports this?" → Must cite logs/output
- "Is this the symptom or the cause?" → Must be cause

### Examples

✅ **GOOD:**
```
Root cause: Gunicorn service is not running
Evidence: systemctl status shows "inactive (dead)"
Contributing factor: Service failed to start due to missing dependency
```

❌ **BAD:**
```
Root cause: Something is wrong with the server
Evidence: Users are seeing errors
```

### If Failed
- Re-analyze the evidence
- Distinguish symptoms from root cause
- State specific, evidence-based cause

---

## Gate 3: Testing

**Applies to:** Code changes, fixes, features

### Pass Criteria
- [ ] Regression test added (when feasible)
- [ ] All existing tests pass
- [ ] New tests pass
- [ ] Test coverage is adequate

### Commands to Run
```bash
# Python
pytest -v
pytest --cov=app tests/

# Node.js
npm test
npm run test:coverage

# Specific test
pytest tests/test_feature.py -v
```

### Expected Output
```
# All tests must pass
===== X passed in Y.YYs =====

# No failures allowed
===== 0 failed =====
```

### Validation
- "Did all tests pass?" → Must be YES
- "Did I add a regression test?" → Must be YES (if applicable)
- "What is the test coverage?" → Must be >80% for new code

### If Failed
- Fix failing tests
- Add missing tests
- Re-run until all pass

---

## Gate 4: Linting & Formatting

**Applies to:** All code changes

### Pass Criteria
- [ ] Linter passes with no errors
- [ ] Code is formatted correctly
- [ ] No style violations

### Commands to Run
```bash
# Python
ruff check .
ruff format .

# Node.js
npm run lint
npm run format

# Check only (no changes)
ruff check . --diff
prettier --check .
```

### Expected Output
```
# Ruff
All checks passed!

# ESLint
✨ No problems found

# Prettier
All matched files use Prettier code style!
```

### Validation
- "Did linter pass?" → Must be YES
- "Is code formatted?" → Must be YES
- "Any style violations?" → Must be NO

### If Failed
- Fix linting errors
- Run formatter
- Re-check until clean

---

## Gate 5: Security Check

**Applies to:** All changes

### Pass Criteria
- [ ] No secrets/API keys in code
- [ ] No PHI/PII in logs
- [ ] Input validation present
- [ ] SQL is parameterized (if applicable)
- [ ] No security vulnerabilities introduced

### Commands to Run
```bash
# Check for secrets
grep -r "api_key\|password\|secret" . --exclude-dir=.git

# Check for PHI in logs
grep -r "email\|phone\|ssn\|name" app/logging/

# Security scan (if available)
bandit -r app/
npm audit
```

### Validation
- "Are there any secrets in code?" → Must be NO
- "Is PHI/PII redacted in logs?" → Must be YES
- "Is input validated?" → Must be YES

### If Failed
- Remove secrets
- Add PHI/PII redaction
- Add input validation
- Fix security issues

---

## Gate 6: Rollback Plan

**Applies to:** Risky changes, production changes

### Pass Criteria
- [ ] Rollback steps documented
- [ ] Rollback tested (if possible)
- [ ] Backup taken (if modifying data)
- [ ] Rollback is simple and fast

### Documentation Required
```markdown
## Rollback Plan

**If this change causes issues:**

1. **Immediate rollback:**
   ```bash
   git revert abc123
   systemctl restart myapp
   ```

2. **Verify rollback:**
   ```bash
   curl http://localhost:8000/healthz
   # Expected: 200 OK
   ```

3. **Restore data (if needed):**
   ```bash
   psql mydb < backup_2026-01-05.sql
   ```

**Estimated rollback time:** 2 minutes
```

### Validation
- "Is rollback documented?" → Must be YES
- "Can rollback be done quickly?" → Must be YES
- "Is backup available?" → Must be YES (if data modified)

### If Failed
- Document rollback steps
- Test rollback procedure
- Create backup if needed

---

## Gate 7: Artifact Generation

**Applies to:** All work

### Pass Criteria
- [ ] Appropriate artifact created
- [ ] Artifact is complete
- [ ] Artifact follows template

### Required Artifacts by Type

| Work Type | Required Artifact |
|-----------|------------------|
| Incident | `artifacts/incident_report.md` |
| Feature | `artifacts/pr_summary.md` |
| Decision | `artifacts/DECISION_RECORD.md` |
| Deployment | `artifacts/runbook.md` |
| Major outage | `artifacts/postmortem.md` |

### Validation
- "Which artifact did I create?" → Must name specific file
- "Is artifact complete?" → Must be YES
- "Does it follow template?" → Must be YES

### If Failed
- Create missing artifact
- Complete all sections
- Follow template structure

---

## Gate 8: Verification

**Applies to:** All changes

### Pass Criteria
- [ ] Change was tested manually
- [ ] Expected behavior confirmed
- [ ] No regressions introduced
- [ ] Health check passes

### Commands to Run
```bash
# Health check
curl -I http://localhost:8000/healthz
# Expected: HTTP/1.1 200 OK

# Functional test
curl -X POST http://localhost:8000/api/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
# Expected: Success response

# Check logs for errors
journalctl -u myapp -n 20 | grep -i error
# Expected: No new errors
```

### Validation
- "Did I test the change?" → Must be YES
- "Does it work as expected?" → Must be YES
- "Any regressions?" → Must be NO

### If Failed
- Test the change
- Fix any issues
- Verify again

---

## Special Gates for Production

**Additional gates when `env == production`:**

### Gate 9: Production Safety
- [ ] No write actions executed
- [ ] Commands provided are safe
- [ ] User approval obtained (if needed)
- [ ] Monitoring points included

### Gate 10: Incident Documentation
- [ ] Incident report complete
- [ ] Timeline documented
- [ ] Impact assessed
- [ ] Prevention steps identified

---

## Final Checklist

Before marking work as "done", verify ALL gates:

```markdown
## Quality Gates Checklist

- [ ] Gate 1: Evidence collected ✓
- [ ] Gate 2: Root cause identified ✓
- [ ] Gate 3: Tests pass ✓
- [ ] Gate 4: Linting passes ✓
- [ ] Gate 5: Security checked ✓
- [ ] Gate 6: Rollback documented ✓
- [ ] Gate 7: Artifact generated ✓
- [ ] Gate 8: Verification complete ✓
- [ ] Gate 9: Production safety (if applicable) ✓
- [ ] Gate 10: Incident docs (if applicable) ✓

ALL gates must be checked before proceeding.
```

---

## If Any Gate Fails

**DO NOT PROCEED**

1. Identify which gate failed
2. Fix the issue
3. Re-run the gate
4. Continue only when passed

**Never skip a failing gate.**

---

## See Also

- [`AGENT_SELF_CHECK.md`](AGENT_SELF_CHECK.md) - Self-validation checklist
- [`../policy/PRODUCTION_POLICY.md`](../policy/PRODUCTION_POLICY.md) - Production rules
- [`../testing/TEST_STRATEGY.md`](../testing/TEST_STRATEGY.md) - Testing guidance
