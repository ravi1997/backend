# Progress Tracking Template

## Snapshot Information

- **Snapshot ID**: [Timestamp: YYYY-MM-DD-HH-MM-SS]
- **Related Context Snapshot**: `CONTEXT_SNAPSHOT.md`
- **Token Budget Level**: [GREEN / YELLOW / ORANGE / RED / CRITICAL]

## Workflow Progress

### Active Workflow

- **Workflow Name**: [From `agent/04_workflows/`]
- **Workflow Purpose**: [Brief description]
- **Total Steps**: [Number]
- **Completion**: [X / Y steps complete]

### Completed Steps

| Step # | Step Name | Status | Timestamp | Notes |
| --- | --- | --- | --- | --- |
| 1 | [Step name] | COMPLETE | [YYYY-MM-DD HH:MM] | [Brief note] |
| 2 | [Step name] | COMPLETE | [YYYY-MM-DD HH:MM] | [Brief note] |
| ... | ... | ... | ... | ... |

### Current Step

- **Step Number**: [X]
- **Step Name**: [Name of current step]
- **Status**: [IN_PROGRESS / BLOCKED / PAUSED]
- **Started**: [YYYY-MM-DD HH:MM]
- **Progress**: [X%] complete
- **Description**: [What is being done in this step]

### Remaining Steps

| Step # | Step Name | Status | Dependencies |
| --- | --- | --- | --- |
| [X+1] | [Step name] | PENDING | [Prerequisites] |
| [X+2] | [Step name] | PENDING | [Prerequisites] |
| ... | ... | ... | ... |

## Task-Level Progress

### Current Task

- **Task ID**: [From backlog or feature plan]
- **Task Name**: [Brief description]
- **Assigned Profile**: [Profile name]
- **Priority**: [HIGH / MEDIUM / LOW]
- **Estimated Effort**: [Time estimate]
- **Actual Effort**: [Time spent so far]

### Sub-Tasks

- [ ] [Sub-task 1] - [Status]
- [ ] [Sub-task 2] - [Status]
- [ ] [Sub-task 3] - [Status]
- [ ] [Sub-task 4] - [Status]

## Files Modified

### Code Changes

**Modified**:

- `[file path]` - [Brief description of changes]
- `[file path]` - [Brief description of changes]

**Added**:

- `[file path]` - [Purpose]
- `[file path]` - [Purpose]

**Deleted**:

- `[file path]` - [Reason]

### Plan Documents

**Created**:

- `plans/[folder]/[file]` - [Purpose]
- `plans/[folder]/[file]` - [Purpose]

**Updated**:

- `plans/[folder]/[file]` - [What changed]

## Test and Gate Status

### Tests

- **Last Test Run**: [YYYY-MM-DD HH:MM]
- **Test Status**: [PASS / FAIL / NOT_RUN]
- **Passing**: [X / Y tests]
- **Failing**: [List of failing tests, if any]

### Gates

- **Last Gate Check**: [YYYY-MM-DD HH:MM]
- **Gate Status**: [PASS / FAIL / PENDING]
- **Failed Checks**: [List of failed checks, if any]

## Blockers and Issues

### Active Blockers

1. **Blocker**: [Description]
   - **Type**: [TECHNICAL / DEPENDENCY / DECISION / RESOURCE]
   - **Impact**: [HIGH / MEDIUM / LOW]
   - **Identified**: [YYYY-MM-DD HH:MM]
   - **Resolution Path**: [How to unblock]

2. **Blocker**: [Description]
   - **Type**: [...]
   - **Impact**: [...]
   - **Identified**: [...]
   - **Resolution Path**: [...]

### Resolved Blockers

1. **Blocker**: [Description]
   - **Resolution**: [How it was resolved]
   - **Resolved**: [YYYY-MM-DD HH:MM]

## Token Budget Impact

### Chunking Applied

- [ ] Large output divided into chunks
- **Chunks Completed**: [X / Y]
- **Chunks Remaining**: [List]

### Context Diet Applied

- [ ] Non-essential context unloaded
- **Unloaded Components**: [List of files removed from context]

### Least-Token Mode

- [ ] Least-token mode activated
- **Impact**: [How it affected work]

## Session Summary

### What Was Accomplished

[2-3 sentence summary of progress made in this session]

### What Remains

[2-3 sentence summary of work still to be done]

### Estimated Completion

- **If No Blockers**: [Time estimate]
- **If Blockers Persist**: [Alternative timeline]

## Verification Checklist

- [ ] All completed steps documented with timestamps
- [ ] Current step status is accurate
- [ ] All modified files listed
- [ ] Blockers clearly identified with resolution paths
- [ ] Test and gate status is current
- [ ] Token budget impact documented
- [ ] No placeholder text remains

## Related Files

- `plans/Continuity/CONTEXT_SNAPSHOT.md`
- `plans/Continuity/DECISIONS.md`
- `plans/Continuity/NEXT.md`
- `agent/09_state/PROJECT_STATE.md`
- `agent/09_state/BACKLOG_STATE.md`
