# Context Snapshot Template

## Session Metadata

- **Snapshot ID**: [Timestamp: YYYY-MM-DD-HH-MM-SS]
- **Snapshot Type**: [PROACTIVE / PRE_SWITCH / EMERGENCY / MANUAL]
- **Token Budget Level**: [GREEN / YELLOW / ORANGE / RED / CRITICAL]
- **Token Usage**: [X%] of budget consumed

## Active Context

### Profile and Workflow

- **Active Profile**: [Profile name from `agent/03_profiles/`]
- **Active Workflow**: [Workflow name from `agent/04_workflows/`]
- **Current Workflow Step**: [Step number and name]

### Stack and Phase

- **Detected Stack(s)**: [From `agent/09_state/STACK_STATE.md`]
  - Primary: [e.g., Python, Node, C++]
  - Secondary: [If multi-stack]
  - DevOps: [Docker, GitHub Actions, etc.]
- **SDLC Phase**: [IDLE / BOOTSTRAP / SPEC / PLAN / DEV / AUDIT / RELEASE]
- **Current Task**: [Task ID and brief description]

### Loaded Agent OS Components

List of currently active Agent OS files in context:

**System (Tier 1)**:

- `agent/AGENT_MANIFEST.md`
- `agent/00_system/00_principles.md`
- [Other system files...]

**Stack-Specific (Tier 2)**:

- [e.g., `agent/11_rules/stack_rules/python_rules.md`]
- [e.g., `agent/05_gates/by_stack/python/`]

**Workflow and Skills (Tier 3)**:

- [e.g., `agent/04_workflows/06_feature_implementation_loop.md`]
- [e.g., `agent/06_skills/implementation/skill_write_code.md`]

## Project State

### Repository Information

- **Project Root**: [Absolute path]
- **Repository Type**: [Monorepo / Single-stack / Multi-stack]
- **Git Branch**: [Current branch name]
- **Git Status**: [Clean / Uncommitted changes / Untracked files]

### State Files

- **PROJECT_STATE.md**: [Current stage and summary]
- **STACK_STATE.md**: [Detected stacks]
- **BACKLOG_STATE.md**: [Active tasks count]
- **TEST_STATE.md**: [Last test results]
- **SECURITY_STATE.md**: [Security scan status]

## Token Budget Management

### Current Status

- **Budget Consumed**: [X%]
- **Trigger Level**: [GREEN / YELLOW / ORANGE / RED / CRITICAL]
- **Snapshot Trigger**: [Why this snapshot was created]

### Actions Taken

- [ ] Context diet applied (if ORANGE+)
- [ ] Least-token mode activated (if ORANGE+)
- [ ] Model switch attempted (if RED+)
- [ ] Model switch successful (if applicable)

### Model Information

- **Current Model**: [Model name and variant]
- **Context Window**: [Token limit]
- **Switched From**: [Previous model, if applicable]
- **Switch Status**: [N/A / SUCCESS / FAILED / NOT_SUPPORTED]

## Session Context for Recovery

### What Was Happening

[2-3 sentence description of what the agent was doing when this snapshot was created]

### Key Decisions Made This Session

[List 3-5 most important decisions or changes made]

1. [Decision 1]
2. [Decision 2]
3. [Decision 3]

### Files Modified This Session

[List of files changed, added, or deleted]

- Modified: [file paths]
- Added: [file paths]
- Deleted: [file paths]

### Conversation Summary

[Brief summary of user requests and agent responses in this session]

## Recovery Instructions

To resume from this snapshot:

1. Read this file (`CONTEXT_SNAPSHOT.md`) to understand session state.
2. Review `PROGRESS.md` for completed steps and current blockers.
3. Check `DECISIONS.md` for rationale behind key choices.
4. Execute actions in `NEXT.md` to resume work.
5. Restore context by loading the Agent OS files listed in "Loaded Agent OS Components" section.

## Verification Checklist

- [ ] All metadata fields populated (no placeholders)
- [ ] Stack and phase correctly identified
- [ ] Loaded components list is accurate
- [ ] Token budget status is current
- [ ] Session context is clear and actionable
- [ ] Recovery instructions are complete

## Related Files

- `plans/Continuity/PROGRESS.md`
- `plans/Continuity/DECISIONS.md`
- `plans/Continuity/NEXT.md`
- `agent/09_state/RECOVERY_CHECKPOINT.md`
- `agent/00_system/12_token_budget_and_model_switching.md`
