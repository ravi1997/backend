# Recovery Checkpoint

## Session Information

- **Date**: [TIMESTAMP]
- **Active Profile**: [Profile Name]
- **Current Workflow**: [Workflow Name]
- **Current Task**: [Task ID from Backlog]
- **Token Budget Level**: [GREEN/YELLOW/ORANGE/RED/CRITICAL]

## Continuity Snapshot

- **Snapshot Location**: `plans/Continuity/`
- **Snapshot Status**: [COMPLETE/PARTIAL/NOT_CREATED]
- **Trigger Reason**: [Token budget level / Error / Manual checkpoint]
- **Files Present**:
  - [ ] `CONTEXT_SNAPSHOT.md`
  - [ ] `PROGRESS.md`
  - [ ] `DECISIONS.md`
  - [ ] `NEXT.md`

## Progress Summary

- **Completed Steps**: [List of completed steps]
- **Current Step**: [What was being attempted when checkpoint was created]
- **Blocker**: [Description of the error or issue, if any]

## State Snapshot

- **Modified Files**: [List of files changed in this session]
- **Uncommitted Changes**: [Yes/No]
- **Test Status**: [Last known test results]
- **Gate Status**: [Last gate check results]

## Next Actions

- **Immediate**: [What needs to happen to resume or unblock]
- **Alternative Path**: [If current approach is blocked, what's plan B]

## Context for New Session

[Brief summary of the project goal and current objective that can be provided to a new AI session. Reference `plans/Continuity/CONTEXT_SNAPSHOT.md` for full details.]

## Recovery Instructions

1. Read all files in `plans/Continuity/` to restore context.
2. Review `PROGRESS.md` to understand what was completed.
3. Check `DECISIONS.md` for key choices made.
4. Execute actions listed in `NEXT.md` to resume work.

## Related Files

- `plans/Continuity/CONTEXT_SNAPSHOT.md`
- `plans/Continuity/PROGRESS.md`
- `plans/Continuity/DECISIONS.md`
- `plans/Continuity/NEXT.md`
- `agent/00_system/12_token_budget_and_model_switching.md`
