# Skill: Rollback Planning

## Purpose

Pre-emptive identification of recovery steps for failed deployments or data-destructive operations.

## Input Contract

- **Target Action**: e.g., "Database Migration", "Cluster Update".
- **Risk Assessment**: High/Medium.

## Execution Procedure

1. **Snapshot Baseline**: Identify the exact commit or state BEFORE the action.
2. **Destruction Analysis**:
    - Does this action delete data? (If yes, backup is mandatory).
    - Does this action change APIs? (If yes, version check is mandatory).
3. **Step-by-Step Reversal**:
    - Step 1: `git checkout $BASELINE_SHA`.
    - Step 2: Restore backup (if applicable).
    - Step 3: Verify system health.
4. **Verification Command**: Define a single "I'm back to safety" check command.

## Failure Modes

- **Irreversible Action**: If the action cannot be undone (e.g., permanent deletion), flagging it as "CRITICAL" and requesting Human-in-Loop.

## Output Contract

- **Rollback Script**: A set of executable commands saved in `plans/Deployment/rollback_plan.md`.
