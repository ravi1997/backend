# Agent Self-Check (Hallucination Prevention)

**Purpose:** Prevent agent hallucination and ensure evidence-based responses
**When to use:** Before every response, before marking work complete
**Prerequisites:** Work has been attempted
**Enforcement:** MANDATORY - must pass all checks

---

## CRITICAL: Stop and Verify

**Before responding to user, STOP and run this checklist.**

If ANY answer is "no" → Fix that first, do NOT proceed.

---

## Checklist 1: Environment & Context

### 1.1 Environment Detection
- [ ] Did I read `policy/ENV_DETECTION.md`?
- [ ] Did I detect environment using the specified rules?
- [ ] Can I state the environment with confidence? (dev/staging/production)
- [ ] If uncertain, did I default to production?

**Validation:**
- "What is the environment?" → Must answer: dev/staging/production
- "How did I detect it?" → Must cite specific evidence
- "Am I certain?" → If no, must treat as production

**If failed:**
- Re-read ENV_DETECTION.md
- Run detection algorithm
- Default to production if uncertain

---

### 1.2 Project Context
- [ ] Did I READ (not assume) `01_PROJECT_CONTEXT.md`?
- [ ] Did I use actual values from the file?
- [ ] Did I use autofill for missing values (not guesses)?
- [ ] Can I cite where each value came from?

**Validation:**
- "Where did I get app_name?" → Must cite: PROJECT_CONTEXT or autofill
- "Did I assume any values?" → Must be NO
- "Are all values evidence-based?" → Must be YES

**If failed:**
- Read PROJECT_CONTEXT.md again
- Use autofill/PATH_AND_SERVICE_INFERENCE.md
- Never proceed with assumed values

---

## Checklist 2: Production Safety

### 2.1 Production Policy Compliance
- [ ] If production/uncertain: Did I avoid ALL write actions?
- [ ] Did I check the command blocklist?
- [ ] Did I provide commands for user (not execute)?
- [ ] Did I document rollback plan?

**Validation:**
- "Is this production?" → If yes or uncertain, continue checks
- "Did I execute any write commands?" → Must be NO
- "Did I check blocklist?" → Must be YES

**If failed:**
- Review PRODUCTION_POLICY.md
- Remove any write actions
- Convert to read-only recommendations

---

### 2.2 Command Safety
- [ ] Did I check each command against safety rules?
- [ ] Did I avoid destructive commands?
- [ ] Did I provide rollback for risky commands?
- [ ] Did I get user approval for risky actions?

**Validation:**
- "Are all commands safe?" → Must be YES
- "Did I check COMMAND_SAFETY.md?" → Must be YES
- "Is rollback documented?" → Must be YES (if risky)

**If failed:**
- Review each command
- Check COMMAND_SAFETY.md
- Add rollback plans

---

## Checklist 3: Evidence Collection

### 3.1 Evidence-Based Claims
- [ ] Did I collect evidence using the correct checklist?
- [ ] Did I run ALL commands in the checklist?
- [ ] Did I capture actual output (not assumed)?
- [ ] Are my claims tied to evidence?

**Validation:**
- "Which checklist did I use?" → Must name specific file
- "Did I run all commands?" → Must be YES
- "Can I cite evidence for each claim?" → Must be YES

**Examples:**

✅ **GOOD:**
```
Claim: "Gunicorn is not running"
Evidence: systemctl status shows "inactive (dead)"
Command run: systemctl status gunicorn
```

❌ **BAD:**
```
Claim: "Probably a timeout issue"
Evidence: None
Command run: None
```

**If failed:**
- Go back and run the checklist
- Collect all evidence
- Base claims on evidence only

---

### 3.2 Root Cause vs Symptoms
- [ ] Did I identify root cause (not just symptoms)?
- [ ] Is root cause based on evidence?
- [ ] Did I distinguish between symptom and cause?
- [ ] Did I identify contributing factors?

**Validation:**
- "What is the root cause?" → Must be specific
- "What is the symptom?" → Must be different from cause
- "What evidence supports root cause?" → Must cite logs/output

**If failed:**
- Re-analyze evidence
- Separate symptoms from causes
- State evidence-based root cause

---

## Checklist 4: PHI/PII Safety

### 4.1 Redaction Check
- [ ] Did I check for PHI/PII in logs?
- [ ] Did I redact emails, names, phones?
- [ ] Did I avoid logging request bodies?
- [ ] Did I follow PHI_SAFE_LOGGING.md?

**Validation:**
- "Did I check for PHI/PII?" → Must be YES
- "Is everything redacted?" → Must be YES
- "Did I follow the policy?" → Must be YES

**If failed:**
- Review PHI_SAFE_LOGGING.md
- Redact all sensitive data
- Re-check output

---

### 4.2 Secrets Check
- [ ] Did I avoid exposing secrets/API keys?
- [ ] Did I check code for hardcoded secrets?
- [ ] Did I redact secrets in logs?
- [ ] Are environment variables safe?

**Validation:**
- "Are there any secrets exposed?" → Must be NO
- "Did I check for hardcoded secrets?" → Must be YES

**If failed:**
- Remove all secrets
- Use environment variables
- Redact from logs

---

## Checklist 5: Quality & Completeness

### 5.1 Quality Gates
- [ ] Did I pass ALL quality gates?
- [ ] Did tests pass?
- [ ] Did linting pass?
- [ ] Did security checks pass?

**Validation:**
- "Did I run quality gates?" → Must be YES
- "Did all gates pass?" → Must be YES
- "Which gates did I skip?" → Must be NONE

**If failed:**
- Run gates/QUALITY_GATES.md
- Fix failing gates
- Re-run until all pass

---

### 5.2 Artifact Generation
- [ ] Did I generate the required artifact?
- [ ] Is the artifact complete?
- [ ] Does it follow the template?
- [ ] Did I validate artifact completeness?

**Validation:**
- "Which artifact did I create?" → Must name file
- "Is it complete?" → Must be YES
- "Does it follow template?" → Must be YES

**If failed:**
- Create missing artifact
- Complete all sections
- Follow template structure

---

## Checklist 6: Hallucination Detection

### 6.1 Assumption Check
- [ ] Did I make any assumptions?
- [ ] Did I guess any values?
- [ ] Did I proceed without evidence?
- [ ] Did I assume environment is dev?

**RED FLAGS - Stop if YES to any:**
- 🚩 "I assumed this value because..."
- 🚩 "Probably this is..."
- 🚩 "It's likely that..."
- 🚩 "I think the issue is..."
- 🚩 "This should be..."

**If any red flag → STOP:**
- Identify the assumption
- Find actual evidence
- Replace assumption with fact

---

### 6.2 Evidence Citation
- [ ] Can I cite evidence for every claim?
- [ ] Did I read actual file contents?
- [ ] Did I see actual command output?
- [ ] Can I quote specific lines?

**Validation:**
- "Where is the evidence?" → Must cite specific source
- "Did I read or assume?" → Must be READ
- "Can I quote the evidence?" → Must be YES

**Examples:**

✅ **GOOD:**
```
Claim: "Port 8000 is configured"
Evidence: Line 23 of docker-compose.yml shows "8000:8000"
Source: Read docker-compose.yml
```

❌ **BAD:**
```
Claim: "Port 8000 is probably used"
Evidence: None
Source: Assumption
```

**If failed:**
- Find actual evidence
- Read actual files
- Quote specific lines

---

### 6.3 Confidence Check
- [ ] Am I confident in my answer?
- [ ] Do I have sufficient evidence?
- [ ] Have I validated my conclusions?
- [ ] Should I ask for clarification?

**Confidence Levels:**
- **HIGH (90-100%):** Proceed with answer
- **MEDIUM (70-89%):** State uncertainty, provide answer with caveats
- **LOW (<70%):** Ask user for clarification, do NOT guess

**If confidence is LOW:**
- State what you know
- State what you don't know
- Ask specific questions
- Do NOT proceed with guesses

---

## Checklist 7: Rollback & Safety

### 7.1 Rollback Plan
- [ ] Did I document rollback steps?
- [ ] Is rollback simple and fast?
- [ ] Did I test rollback (if possible)?
- [ ] Is backup available (if needed)?

**Validation:**
- "Is rollback documented?" → Must be YES
- "Can it be done quickly?" → Must be YES
- "Is backup available?" → Must be YES (if data modified)

**If failed:**
- Document rollback steps
- Ensure it's simple
- Create backup if needed

---

### 7.2 Risk Assessment
- [ ] Did I assess risk level?
- [ ] Did I warn about high-risk actions?
- [ ] Did I provide safer alternatives?
- [ ] Did I get user approval (if risky)?

**Validation:**
- "What is the risk level?" → Must state: LOW/MEDIUM/HIGH
- "Did I warn user?" → Must be YES (if high risk)
- "Are there safer alternatives?" → Must explore

**If failed:**
- Assess risk properly
- Warn user of risks
- Provide alternatives

---

## Checklist 8: Smallest Safe Change

### 8.1 Change Scope
- [ ] Did I propose the smallest safe change?
- [ ] Did I avoid unnecessary refactoring?
- [ ] Is the change focused and minimal?
- [ ] Did I avoid scope creep?

**Validation:**
- "Is this the smallest change?" → Must be YES
- "Did I add unnecessary changes?" → Must be NO
- "Is it focused?" → Must be YES

**If failed:**
- Reduce scope
- Remove unnecessary changes
- Focus on the issue

---

## Final Validation

Before responding, verify ALL checklists:

```markdown
## Agent Self-Check Summary

- [ ] Checklist 1: Environment & Context ✓
- [ ] Checklist 2: Production Safety ✓
- [ ] Checklist 3: Evidence Collection ✓
- [ ] Checklist 4: PHI/PII Safety ✓
- [ ] Checklist 5: Quality & Completeness ✓
- [ ] Checklist 6: Hallucination Detection ✓
- [ ] Checklist 7: Rollback & Safety ✓
- [ ] Checklist 8: Smallest Safe Change ✓

ALL checklists must be checked before responding.
```

---

## If Any Check Fails

**DO NOT RESPOND TO USER**

1. Identify which check failed
2. Fix the issue
3. Re-run the check
4. Continue only when passed

**Never skip a failing check.**

---

## Red Flags - Stop Immediately

🚩 **Stop if you:**
- Cannot cite evidence for a claim
- Assumed a value you didn't read
- Guessed instead of checking
- Proceeded without running checklist
- Skipped quality gates
- Exposed PHI/PII or secrets
- Made assumptions about environment
- Proposed changes without rollback
- Hallucinated file contents
- Stated facts without evidence

**If you see ANY red flag → STOP, fix it, then proceed.**

---

## See Also

- [`QUALITY_GATES.md`](QUALITY_GATES.md) - Quality requirements
- [`../policy/PRODUCTION_POLICY.md`](../policy/PRODUCTION_POLICY.md) - Production safety
- [`../policy/PHI_SAFE_LOGGING.md`](../policy/PHI_SAFE_LOGGING.md) - PHI/PII safety
- [`../00_INDEX.md`](../00_INDEX.md) - Routing validation
