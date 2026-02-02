# Skill: Continuity Snapshot Creation

## Purpose

Creates a comprehensive continuity snapshot that enables seamless session handoff or recovery after token budget exhaustion, model switching, or unexpected termination.

## Input Contract

- **Trigger Level**: Current token safety level (YELLOW/ORANGE/RED/CRITICAL).
- **Current Task**: Description of active work.
- **Active Stack**: Detected technology stack(s).
- **Current Phase**: SDLC phase (BOOTSTRAP/SPEC/PLAN/DEV/AUDIT/RELEASE).

## Execution Procedure

### 1. Verify Snapshot Directory

- Check if `plans/Continuity/` exists.
- If not, create it using absolute path: `/path/to/project/plans/Continuity/`.

### 2. Create CONTEXT_SNAPSHOT.md

Use template from `agent/07_templates/continuity/CONTEXT_SNAPSHOT_TEMPLATE.md`.

Populate with:

- **Session ID**: Timestamp or unique identifier.
- **Active Profile**: Current profile from `agent/03_profiles/`.
- **Active Workflow**: Current workflow from `agent/04_workflows/`.
- **Detected Stack**: From `agent/09_state/STACK_STATE.md`.
- **Loaded Context**: List of currently active Agent OS files.
- **Token Budget Status**: Current level and percentage used.

### 3. Create PROGRESS.md

Use template from `agent/07_templates/continuity/PROGRESS_TEMPLATE.md`.

Populate with:

- **Completed Steps**: List of finished workflow steps with timestamps.
- **Current Step**: What is being worked on right now.
- **Blockers**: Any impediments or errors encountered.
- **Modified Files**: List of files changed in this session.
- **Uncommitted Changes**: Git status summary.

### 4. Create DECISIONS.md

Use template from `agent/07_templates/continuity/DECISIONS_TEMPLATE.md`.

Populate with:

- **Key Decisions**: Major choices made (e.g., architecture, library selection).
- **Rationale**: Why each decision was made.
- **Reversibility**: Whether decision can be undone and how.
- **Risk Assessment**: Impact level of each decision.

### 5. Create NEXT.md

Use template from `agent/07_templates/continuity/NEXT_TEMPLATE.md`.

Populate with:

- **Immediate Next Actions**: Top 3 tasks to resume work.
- **Alternative Paths**: If current approach is blocked, what's plan B.
- **Prerequisites**: Any dependencies that must be resolved first.
- **Expected Duration**: Estimated time to complete next actions.

### 6. Update Recovery Checkpoint

Update `agent/09_state/RECOVERY_CHECKPOINT.md` with:

- Snapshot location: `plans/Continuity/`
- Timestamp of snapshot creation.
- Trigger reason (token budget level or other cause).

### 7. Verify Completeness

- Confirm all 4 files exist in `plans/Continuity/`.
- Verify each file is non-empty and has no placeholder text.
- Check that all critical information is captured.

## Stop Conditions

- All 4 continuity files successfully written to disk.
- `agent/09_state/RECOVERY_CHECKPOINT.md` updated.
- Verification check passes (no empty files, no placeholders).

## Output Contract

- **Snapshot Location**: `plans/Continuity/`
- **Files Created**:
  - `CONTEXT_SNAPSHOT.md`
  - `PROGRESS.md`
  - `DECISIONS.md`
  - `NEXT.md`
- **Status**: COMPLETE/FAILED
- **Verification**: PASS/FAIL

## Failure Modes

### Cannot Write to plans/Continuity/

**Symptom**: Directory creation or file write fails.

**Recovery**:

1. Attempt write to `agent/09_state/EMERGENCY_SNAPSHOT.md`.
2. If that fails, output snapshot content to user in chat.
3. Request user to manually save the snapshot.

### Incomplete Information

**Symptom**: Missing critical data for snapshot (e.g., unknown stack).

**Recovery**:

1. Fill known fields completely.
2. Mark unknown fields with `[UNKNOWN - requires manual input]`.
3. Proceed with partial snapshot rather than failing completely.

### Verification Fails

**Symptom**: Files created but contain placeholders or are empty.

**Recovery**:

1. Log specific verification failures.
2. Re-attempt file creation for failed files only.
3. If second attempt fails, escalate to user with error details.

## Examples

### Example 1: YELLOW Trigger (Proactive Snapshot)

**Context**: Token usage at 65%, implementing large feature.

**Action**:

1. Create snapshot with current progress.
2. Document 3 completed sub-tasks and current sub-task.
3. Note decision to use library X over Y with rationale.
4. List next 3 sub-tasks to complete feature.

**Result**: Snapshot created, work continues normally.

### Example 2: RED Trigger (Pre-Switch Snapshot)

**Context**: Token usage at 87%, about to attempt model switch.

**Action**:

1. Create comprehensive snapshot with all state.
2. Document all decisions made in session.
3. List exact command that will be run next.
4. Mark snapshot as "PRE_MODEL_SWITCH".

**Result**: Snapshot created, model switch attempted.

### Example 3: CRITICAL Trigger (Emergency Handoff)

**Context**: Token usage at 96%, cannot complete current task.

**Action**:

1. STOP all new work immediately.
2. Create minimal but complete snapshot.
3. Document exact point of interruption.
4. Provide clear resume instructions in NEXT.md.

**Result**: Snapshot created, session terminated gracefully.

## Related Files

- `agent/00_system/12_token_budget_and_model_switching.md`
- `agent/07_templates/continuity/CONTEXT_SNAPSHOT_TEMPLATE.md`
- `agent/07_templates/continuity/PROGRESS_TEMPLATE.md`
- `agent/07_templates/continuity/DECISIONS_TEMPLATE.md`
- `agent/07_templates/continuity/NEXT_TEMPLATE.md`
- `agent/08_plan_output_contract/folder_layout.md`
- `agent/09_state/RECOVERY_CHECKPOINT.md`
