# Error Handling

## Purpose

Defines how the Agent reacts to tool failures, environment issues, and logic errors.

## Recovery Procedures

### 1. Tool Execution Failure

- **Symptoms**: `run_command` returns non-zero exit code.
- **Procedure**:
  1. Read the `stderr`.
  2. Search for the error string in the project (to see if it has happened before).
  3. Attempt 1 automated fix (e.g., missing dependency install).
  4. If failure persists, escalate to the User with the full log.

### 2. Context Overflow / Token Budget Exhaustion

- **Symptoms**: AI starts losing track of earlier instructions or state, token usage > 60% of budget.
- **Procedure**:
  1. Assess trigger level per `agent/00_system/12_token_budget_and_model_switching.md`.
  2. Create continuity snapshot in `plans/Continuity/`.
  3. Attempt model switch if platform supports it.
  4. If unavailable, activate context diet and least-token mode.
  5. Use chunking for any remaining large outputs.
  6. If CRITICAL, save final snapshot and request user to start new session.

### 3. Infinite Loops

- **Symptoms**: Agent repeating the same command 3+ times with the same result.
- **Procedure**:
  1. **STOP**.
  2. Flag the loop to the User.
  3. Identify the "Cycle Break" (a different approach or manual intervention).

### 4. Permission Denied

- **Symptoms**: Filesystem or Network access errors.
- **Procedure**:
  1. Verify the path is within `01_scope_and_limits.md`.
  2. Request the User to grant permissions via terminal commands or manual chmod.

## Error Codes

- `E-DET-001`: Stack detection failed (Too ambiguous).
- `E-GATE-500`: Gate failure (Quality threshold not met).
- `E-SEC-666`: Security violation (Leak detected).
- `E-TOKEN-999`: Token budget exhausted (Context overflow).

## Related Files

- `agent/00_system/04_error_handling.md`
- `agent/00_system/12_token_budget_and_model_switching.md`
- `agent/05_gates/enforcement/gate_failure_playbook.md`
