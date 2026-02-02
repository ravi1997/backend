# System Procedure: Token Budget Management + Continuity + Model Switching

## Purpose

Ensures the Agent OS survives token exhaustion through proactive monitoring, continuity snapshots, chunking strategies, and model switching (when platform-supported). This is a **cross-cutting capability** that applies to all workflows, skills, and outputs.

## Core Principles

1. **Platform Agnostic**: The system MUST work even if model switching is NOT supported.
2. **No Hallucination**: Never claim a model switch occurred unless the platform explicitly confirms it.
3. **Continuity First**: Snapshots are the canonical handoff mechanism for session recovery.
4. **Chunking Over Truncation**: Long outputs must be written incrementally to disk.
5. **Least-Token Mode**: When budget is constrained, minimize prompt overhead and maximize task completion.

## Token Safety Triggers

### Trigger Levels

| Level | Threshold | Action Required |
| --- | --- | --- |
| **GREEN** | < 60% of budget used | Normal operation. |
| **YELLOW** | 60-75% of budget used | Enable continuity snapshot protocol. |
| **ORANGE** | 75-85% of budget used | Activate least-token mode + chunking. |
| **RED** | > 85% of budget used | Attempt model switch (if supported) OR initiate graceful handoff. |
| **CRITICAL** | > 95% of budget used | STOP all new work. Write final snapshot and exit. |

### Monitoring Procedure

1. **Check Budget**: Every 5 tool calls, estimate current token usage.
2. **Assess Risk**: Determine trigger level based on remaining budget and task complexity.
3. **Log Status**: Update `plans/Continuity/PROGRESS.md` with current level.
4. **Escalate**: If YELLOW or higher, activate appropriate protocol.

## Continuity Snapshot Protocol

### When to Create Snapshots

- **Mandatory**: At YELLOW trigger level or higher.
- **Recommended**: Before any large output generation (> 500 lines).
- **Always**: Before attempting model switch or session handoff.

### Snapshot Components

All snapshots MUST be written to `plans/Continuity/`:

1. **CONTEXT_SNAPSHOT.md**: Current task, stack, phase, and loaded context.
2. **PROGRESS.md**: Completed steps, current step, and blockers.
3. **DECISIONS.md**: Key decisions made, rationale, and reversibility notes.
4. **NEXT.md**: Immediate next actions and alternative paths.

### Snapshot Creation Procedure

1. **Trigger Detection**: Identify that snapshot is needed.
2. **Use Template**: Copy from `agent/07_templates/continuity/CONTEXT_SNAPSHOT_TEMPLATE.md`.
3. **Populate Fields**: Fill all sections with current state (NO placeholders).
4. **Write to Disk**: Save to `plans/Continuity/` using absolute paths.
5. **Verify**: Confirm all 4 files exist and are non-empty.
6. **Log**: Update `agent/09_state/RECOVERY_CHECKPOINT.md` with snapshot location.

## Model Switching Strategy (Platform-Dependent)

### Pre-Switch Checklist

- [ ] Verify platform supports mid-session model switching.
- [ ] Confirm continuity snapshot is complete and written to disk.
- [ ] Identify target model (e.g., larger context window, lower cost).
- [ ] Document switch rationale in `plans/Continuity/DECISIONS.md`.

### Switch Execution

1. **Request Switch**: Use platform-specific API or command.
2. **Await Confirmation**: Do NOT proceed until platform confirms success.
3. **Verify Context**: Check that new model has access to conversation history.
4. **Resume Work**: Continue from last checkpoint in snapshot.

### Switch Failure Fallback

If switch is NOT supported or fails:

1. **Acknowledge Limitation**: Clearly state "Model switching not available on this platform."
2. **Activate No-Switch Protocol**: Use context diet + chunking + least-token mode.
3. **Prepare Handoff**: Write comprehensive snapshot for manual session restart.

## No-Switch Fallback Strategy

### Context Diet

1. **Unload Non-Essential**: Remove inactive stack rules, unused skills, and old logs.
2. **Summarize History**: Condense conversation into `plans/Continuity/PROGRESS.md`.
3. **Purge Redundancy**: Delete duplicate information from loaded context.

### Chunking Rules

For any output > 300 lines:

1. **Plan Chunks**: Divide output into logical sections (e.g., by file, by feature).
2. **Write Incrementally**: Use `write_to_file` or `replace_file_content` for each chunk.
3. **Update State**: After each chunk, update `plans/Continuity/PROGRESS.md`.
4. **Verify Completion**: Confirm all chunks written before marking task done.

### Least-Token Mode

When in ORANGE or RED:

- **Minimize Explanations**: Use terse, action-focused language.
- **Skip Examples**: Reference existing files instead of repeating content.
- **Batch Operations**: Combine multiple edits into single tool calls.
- **Defer Non-Critical**: Postpone documentation updates until budget recovers.

## Standard Output Format During Token Safety Mode

When operating in YELLOW or higher:

```markdown
## Token Safety Status

**Level**: [GREEN/YELLOW/ORANGE/RED/CRITICAL]
**Budget Used**: [X%]
**Snapshot Status**: [COMPLETE/IN_PROGRESS/NOT_STARTED]
**Snapshot Location**: `plans/Continuity/`

## Current Action

[Brief description of what is being done]

## Next Checkpoint

[When the next snapshot or status update will occur]
```

## Do-Not-Hallucinate Constraints

### Prohibited Claims

- **NEVER** say "Switching to larger model" unless platform confirms it.
- **NEVER** say "Context window expanded" without verification.
- **NEVER** claim "Unlimited budget" or "No token limits."

### Required Honesty

- **ALWAYS** state if model switching is attempted but not confirmed.
- **ALWAYS** acknowledge when operating under token constraints.
- **ALWAYS** inform user if task cannot complete within current budget.

## Integration with Workflows

All workflows in `agent/04_workflows/` MUST include:

1. **Token Risk Check**: At workflow start and before large output stages.
2. **Snapshot Gate**: Mandatory snapshot creation if risk is non-trivial.
3. **Chunking Plan**: For any multi-file or large document generation.
4. **State Updates**: After each major step, update continuity files.

## Integration with Skills

All skills in `agent/06_skills/` SHOULD:

1. **Check Budget**: Before starting execution.
2. **Report Risk**: If task may exceed available budget.
3. **Use Chunking**: For large outputs (e.g., code generation, documentation).
4. **Update Snapshots**: If operating in YELLOW or higher.

## Integration with Gates

All gates in `agent/05_gates/` MUST:

1. **Verify Snapshot**: If task is large, confirm snapshot exists.
2. **Check Chunking**: Ensure long outputs were written incrementally.
3. **Validate State**: Confirm `plans/Continuity/PROGRESS.md` is current.

## Failure Modes

### Snapshot Creation Fails

**Symptom**: Cannot write to `plans/Continuity/`.

**Response**:

1. Attempt write to `agent/09_state/EMERGENCY_SNAPSHOT.md`.
2. If that fails, output snapshot content to user in chat.
3. Request user to manually save the snapshot.

### Budget Exhausted Mid-Task

**Symptom**: Reach CRITICAL level before task completion.

**Response**:

1. STOP all new work immediately.
2. Write minimal final snapshot with current state.
3. Inform user: "Token budget exhausted. Snapshot saved to `plans/Continuity/`. Please start new session and reference snapshot to continue."

### Model Switch Rejected

**Symptom**: Platform returns error on switch request.

**Response**:

1. Log error in `plans/Continuity/DECISIONS.md`.
2. Activate no-switch fallback immediately.
3. Inform user of limitation and alternative approach.

## Related Files

- `agent/00_system/08_context_management.md` (Context loading rules)
- `agent/00_system/09_graceful_degradation.md` (Failure handling)
- `agent/00_system/03_decision_policy.md` (Risk assessment)
- `agent/00_system/04_error_handling.md` (Error protocols)
- `agent/00_system/02_response_format.md` (Output standards)
- `agent/06_skills/metacognition/skill_context_budgeting.md` (Context optimization)
- `agent/06_skills/metacognition/skill_continuity_snapshot.md` (Snapshot creation)
- `agent/06_skills/metacognition/skill_model_switching_policy.md` (Switch logic)
- `agent/08_plan_output_contract/folder_layout.md` (Output locations)
- `agent/09_state/RECOVERY_CHECKPOINT.md` (Recovery state)
- `agent/12_checks/checklists/token_safety_checklist.md` (Validation)
- `agent/13_examples/example_token_safety_mode.md` (Reference implementation)

## Version

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-22  
**Status**: Active
