# Next Actions Template

## Snapshot Information

- **Snapshot ID**: [Timestamp: YYYY-MM-DD-HH-MM-SS]
- **Related Context Snapshot**: `CONTEXT_SNAPSHOT.md`
- **Token Budget Level**: [GREEN / YELLOW / ORANGE / RED / CRITICAL]
- **Resume Priority**: [IMMEDIATE / HIGH / NORMAL / LOW]

## Immediate Next Actions

### Action 1: [Brief Title]

- **Action ID**: ACT-[YYYYMMDD]-001
- **Priority**: [CRITICAL / HIGH / MEDIUM / LOW]
- **Estimated Duration**: [Time estimate]
- **Prerequisites**: [What must be done first, if anything]

**Description**:
[Detailed description of what needs to be done]

**Steps**:

1. [Specific step 1]
2. [Specific step 2]
3. [Specific step 3]

**Expected Outcome**:
[What should result from this action]

**Verification**:
[How to confirm action was successful]

**Blocker Risk**: [LOW / MEDIUM / HIGH]
**Blocker Details**: [Potential issues that could prevent completion]

---

### Action 2: [Brief Title]

- **Action ID**: ACT-[YYYYMMDD]-002
- **Priority**: [...]
- **Estimated Duration**: [...]
- **Prerequisites**: [...]

[Repeat structure above for each immediate action]

---

### Action 3: [Brief Title]

[Continue for top 3-5 immediate actions]

---

## Sequential Action Plan

### Phase 1: [Phase Name]

**Goal**: [What this phase accomplishes]

**Actions**:

1. [Action ID] - [Brief description]
2. [Action ID] - [Brief description]
3. [Action ID] - [Brief description]

**Completion Criteria**: [How to know phase is done]

### Phase 2: [Phase Name]

**Goal**: [What this phase accomplishes]

**Actions**:

1. [Action ID] - [Brief description]
2. [Action ID] - [Brief description]

**Completion Criteria**: [How to know phase is done]

### Phase 3: [Phase Name]

[Continue for all planned phases]

## Alternative Paths

### If Current Approach Blocked

**Scenario**: [What blocker would trigger this path]

**Alternative Actions**:

1. [Alternative action 1]
2. [Alternative action 2]
3. [Alternative action 3]

**Trade-offs**:

- **Pros**: [Benefits of alternative]
- **Cons**: [Drawbacks of alternative]

### If Token Budget Exhausted

**Actions**:

1. Create final continuity snapshot (if not already done).
2. Update `agent/09_state/RECOVERY_CHECKPOINT.md`.
3. Inform user: "Token budget exhausted. Snapshot saved to `plans/Continuity/`. Please start new session with snapshot reference."

**Resume Instructions for New Session**:

1. Read all files in `plans/Continuity/`.
2. Load context from `CONTEXT_SNAPSHOT.md`.
3. Review `PROGRESS.md` to understand what was completed.
4. Check `DECISIONS.md` for key choices made.
5. Execute actions listed in this file (`NEXT.md`).

### If Tests Fail

**Scenario**: [What test failures would trigger this path]

**Debugging Actions**:

1. [Debugging step 1]
2. [Debugging step 2]
3. [Debugging step 3]

**Fallback**: [What to do if debugging doesn't resolve]

### If Gate Fails

**Scenario**: [What gate failure would trigger this path]

**Remediation Actions**:

1. [Remediation step 1]
2. [Remediation step 2]
3. [Remediation step 3]

**Escalation**: [When to escalate to user]

## Dependencies and Prerequisites

### External Dependencies

- **Dependency**: [e.g., API access, credentials]
  - **Status**: [AVAILABLE / PENDING / BLOCKED]
  - **Required For**: [Which actions need this]
  - **Unblock Path**: [How to obtain if not available]

- **Dependency**: [...]
  - **Status**: [...]
  - **Required For**: [...]
  - **Unblock Path**: [...]

### Internal Prerequisites

- **Prerequisite**: [e.g., schema migration, data seeding]
  - **Status**: [COMPLETE / IN_PROGRESS / NOT_STARTED]
  - **Required For**: [Which actions need this]
  - **Owner**: [Who is responsible]

## Resource Requirements

### Time Estimates

- **Immediate Actions**: [Total time for top 3 actions]
- **Phase 1**: [Time estimate]
- **Phase 2**: [Time estimate]
- **Total Remaining Work**: [Overall estimate]

### Token Budget Considerations

- **Current Usage**: [X%]
- **Estimated Usage for Next Actions**: [Y%]
- **Risk Level**: [Will next actions trigger token safety mode?]
- **Mitigation**: [How to manage token budget]

### Human Input Required

- **Input Needed**: [What user must provide]
- **For Actions**: [Which actions need this input]
- **Format**: [How user should provide input]

## Success Criteria

### Task Completion

- [ ] All immediate actions completed
- [ ] All phases completed
- [ ] Tests passing
- [ ] Gates passing
- [ ] Documentation updated

### Quality Metrics

- **Code Coverage**: [Target %]
- **Performance**: [Target metrics]
- **Security**: [Scan results expected]

## Rollback Plan

### If Actions Fail

**Rollback Steps**:

1. [How to undo changes]
2. [How to restore previous state]
3. [How to verify rollback success]

**Rollback Cost**: [Effort required]

## Communication Plan

### User Updates

- **Update Frequency**: [How often to inform user]
- **Update Content**: [What to report]
- **Escalation Triggers**: [When to ask for help]

### Documentation Updates

- **Files to Update**: [List of docs that need updating]
- **Update Timing**: [When to update them]

## Verification Checklist

- [ ] Top 3 immediate actions clearly defined
- [ ] All actions have steps and expected outcomes
- [ ] Alternative paths documented
- [ ] Dependencies identified
- [ ] Time estimates provided
- [ ] Token budget risk assessed
- [ ] Success criteria defined
- [ ] No placeholder text remains

## Related Files

- `plans/Continuity/CONTEXT_SNAPSHOT.md`
- `plans/Continuity/PROGRESS.md`
- `plans/Continuity/DECISIONS.md`
- `agent/09_state/RECOVERY_CHECKPOINT.md`
- `agent/09_state/BACKLOG_STATE.md`
- `agent/00_system/12_token_budget_and_model_switching.md`
