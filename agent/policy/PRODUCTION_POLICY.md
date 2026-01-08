# Production Policy (Read-Only)

**Purpose:** Prevent destructive actions in production environments
**When to use:** When `env == production` OR when uncertain about environment
**Prerequisites:** Environment has been detected via `policy/ENV_DETECTION.md`
**Enforcement:** MANDATORY - no exceptions without explicit user approval

---

## CRITICAL: Default Behavior

**If uncertain about environment → treat as PRODUCTION**

This means:
- Cannot detect environment? → Production mode
- User didn't specify? → Production mode
- Detection failed? → Production mode

**Safety first, always.**

---

## Allowed Actions

Agent MAY perform these actions in production:

✅ **Read Operations:**
- Read logs (with PHI/PII redaction)
- Read metrics and dashboards
- Read configurations (non-secret)
- Read database schema (not data)
- Read file contents (non-secret)

✅ **Analysis:**
- Explain root causes based on evidence
- Analyze error patterns
- Review code for issues
- Suggest optimizations

✅ **Documentation:**
- Create incident reports
- Write postmortems
- Document findings
- Create tickets/issues

✅ **Preparation:**
- Prepare PRs (WITHOUT merging)
- Draft deployment plans (WITHOUT executing)
- Write rollback procedures
- Create runbooks

---

## Blocked Actions (ABSOLUTE)

Agent MUST NOT perform these actions in production:

❌ **Database Operations:**
- Running migrations
- Executing SQL updates/deletes
- Modifying schema
- Truncating tables
- Dropping tables/databases

❌ **Service Operations:**
- Restarting services
- Stopping services
- Changing service configs
- Modifying systemd units
- Reloading configurations

❌ **Code Operations:**
- Pushing commits to production branches
- Merging pull requests
- Deploying builds/images
- Modifying code files
- Changing environment variables

❌ **Infrastructure Operations:**
- Scaling services up/down
- Modifying load balancers
- Changing DNS records
- Updating firewall rules
- Modifying cloud resources

❌ **Destructive Commands:**
- `rm -rf` or any file deletion
- `DROP` statements
- `TRUNCATE` statements
- `systemctl stop/restart`
- `docker-compose down`
- `kubectl delete`

---

## Command Blocklist

These commands are **NEVER** allowed in production:

```bash
# Service management
systemctl restart
systemctl stop
systemctl reload
service restart
service stop

# Docker
docker-compose down
docker-compose restart
docker stop
docker rm

# Database
psql -c "DROP
psql -c "TRUNCATE
mysql -e "DROP
mysql -e "TRUNCATE

# File operations
rm -rf
rm -f /
mv /etc
chmod 777

# Git operations
git push origin main
git push origin master
git merge
git commit --amend
```

**If agent attempts any of these → STOP and warn user**

---

## Approval Workflow for Exceptions

If user explicitly requests a blocked action in production:

### Step 1: Confirm Understanding
```markdown
⚠️ **PRODUCTION SAFETY WARNING**

You've requested: [ACTION]
Environment: production
Risk level: HIGH

This action is normally blocked because:
- [REASON 1]
- [REASON 2]

Are you sure you want to proceed?
```

### Step 2: Require Explicit Confirmation
User MUST respond with exact phrase:
```
"Yes, I understand the risks and want to proceed in production"
```

Any other response → Do not proceed

### Step 3: Document Approval
```markdown
## Production Action Approval

- Action: [WHAT]
- Requested by: [USER]
- Timestamp: [TIME]
- Justification: [WHY]
- Rollback plan: [HOW TO UNDO]
```

### Step 4: Provide Safe Execution Plan
```markdown
## Safe Execution Steps

1. **Backup first:**
   ```bash
   [backup commands]
   ```

2. **Execute action:**
   ```bash
   [actual command]
   ```

3. **Verify success:**
   ```bash
   [verification commands]
   ```

4. **If failed, rollback:**
   ```bash
   [rollback commands]
   ```
```

---

## Required Artifacts (Production Incidents)

For any production issue, agent MUST generate:

1. **Always:**
   - `artifacts/incident_report.md`

2. **If major outage (>5 min downtime):**
   - `artifacts/postmortem.md`

3. **If changes proposed:**
   - `artifacts/DECISION_RECORD.md`

4. **If deployment needed:**
   - `artifacts/runbook.md`

---

## Validation Checklist

Before ANY action in production, verify:

```markdown
## Production Action Checklist
- [ ] Environment confirmed as production
- [ ] Action is on allowed list (not blocked)
- [ ] No destructive commands involved
- [ ] Rollback plan documented
- [ ] User explicitly approved (if risky)
- [ ] Backup taken (if modifying data)
- [ ] Monitoring in place to detect issues
- [ ] Incident report prepared

If ANY checkbox is unchecked → STOP
```

---

## Enforcement Rules

### Rule 1: Read-Only by Default
In production, agent operates in read-only mode unless:
- Action is explicitly on allowed list
- User has provided explicit approval
- Rollback plan exists

### Rule 2: Evidence Required
Agent MUST cite evidence for all claims:
- ✅ "Log shows: [actual log line]"
- ❌ "Probably a timeout issue"

### Rule 3: No Assumptions
Agent MUST NOT assume:
- ❌ "This is probably dev environment"
- ❌ "User wants me to fix it automatically"
- ❌ "This change is safe"

### Rule 4: Escalate When Uncertain
If uncertain about safety:
1. State the uncertainty
2. Explain the risk
3. Ask user for guidance
4. Do NOT proceed

---

## Audit Logging

All production actions must be logged:

```markdown
## Production Action Log

**Timestamp:** [ISO 8601]
**Action:** [WHAT]
**Environment:** production
**User:** [WHO]
**Approval:** [YES/NO]
**Result:** [SUCCESS/FAILURE]
**Evidence:** [LOGS/OUTPUT]
```

---

## Examples

### ✅ ALLOWED: Read logs
```bash
# This is OK
tail -n 100 /var/log/nginx/error.log | grep "502"
journalctl -u myapp -n 50
docker logs myapp --tail 100
```

### ❌ BLOCKED: Restart service
```bash
# This is BLOCKED
systemctl restart myapp

# Agent should instead say:
"I cannot restart services in production. 
Here's the command for you to run:
  sudo systemctl restart myapp
After running, verify with:
  systemctl status myapp"
```

### ✅ ALLOWED: Prepare PR
```bash
# This is OK
git checkout -b fix/production-issue
# Make changes
git commit -m "Fix issue"
git push origin fix/production-issue
# Create PR (don't merge)
```

### ❌ BLOCKED: Merge to production
```bash
# This is BLOCKED
git checkout main
git merge fix/production-issue
git push origin main
```

---

## Red Flags - Stop Immediately

🚩 **Stop if you're about to:**
- Execute a command with `rm`, `DROP`, or `TRUNCATE`
- Restart any service
- Modify production database
- Push to main/master branch
- Assume environment is dev
- Proceed without user confirmation

---

## See Also

- [`ENV_DETECTION.md`](ENV_DETECTION.md) - How to detect environment
- [`COMMAND_SAFETY.md`](COMMAND_SAFETY.md) - Command safety classification
- [`../gates/AGENT_SELF_CHECK.md`](../gates/AGENT_SELF_CHECK.md) - Self-validation

