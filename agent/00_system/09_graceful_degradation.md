# System Procedure: Graceful Degradation & Failure Handling

## Purpose

Defines how the Agent OS should behave when encountering unrecoverable errors or reaching the limits of its capabilities.

## Failure Categories

### 1. Tool Failure (Cannot Execute Command)

**Symptoms**: `run_command` returns error, file system is read-only, network is down.

**Response**:

1. **Retry Once**: Attempt the command one more time after a 2-second delay.
2. **Escalate**: If retry fails, report the exact error to the User with:
   - The command that failed.
   - The error message.
   - Suggested manual remediation steps.
3. **State Preservation**: Save the current task state to `agent/09_state/RECOVERY_CHECKPOINT.md`.

### 2. Knowledge Gap (Unknown Stack or Pattern)

**Symptoms**: No matching fingerprint in `agent/02_detection/stack_fingerprints/`, unfamiliar error message.

**Response**:

1. **Web Search**: Use `search_web` to find documentation or Stack Overflow answers.
2. **User Query**: Ask the User: "This appears to be [X]. Can you confirm and provide documentation links?"
3. **Learning**: Once resolved, create a new fingerprint file in `agent/02_detection/stack_fingerprints/custom_[name].md`.

### 3. Logical Impossibility (Contradictory Requirements)

**Symptoms**: Cannot satisfy all constraints simultaneously.

**Response**:

1. **Route to Scenario**: Use `agent/01_entrypoints/scenarios/scenario_conflict_resolution.md`.
2. **Do Not Guess**: Never silently choose one requirement over another.

### 4. Resource Exhaustion (Out of Memory, Disk Full)

**Symptoms**: System errors, slow performance, tool timeouts.

**Response**:

1. **Cleanup**: Close unnecessary terminals, delete temporary files in `/tmp/`.
2. **Report**: Notify the User of resource constraints.
3. **Pause**: Do not continue implementation until resources are freed.

### 5. Context Overflow / Token Budget Exhaustion

**Symptoms**: Agent starts repeating itself, forgetting earlier decisions, token usage > 60% of budget.

**Response**:

1. **Assess Level**: Determine trigger level (YELLOW/ORANGE/RED/CRITICAL) per `agent/00_system/12_token_budget_and_model_switching.md`.
2. **Create Snapshot**: Immediately write continuity snapshot to `plans/Continuity/` using `agent/06_skills/metacognition/skill_continuity_snapshot.md`.
3. **Attempt Model Switch**: If platform supports it, use `agent/06_skills/metacognition/skill_model_switching_policy.md` to request larger context model.
4. **Fallback - Context Diet**: If switch unavailable, activate no-switch protocol:
   - Unload non-essential context (see `agent/00_system/08_context_management.md`).
   - Summarize history into `plans/Continuity/PROGRESS.md`.
   - Enable least-token mode for remaining work.
5. **Chunking**: For any remaining large outputs, use incremental writes to disk.
6. **User Handoff**: If CRITICAL level reached, inform user: "Token budget exhausted. Continuity snapshot saved to `plans/Continuity/`. Please start new session with snapshot reference to continue."

## General Principles

- **Fail Loudly**: Never silently ignore errors.
- **Preserve State**: Always save progress before reporting a failure.
- **User Autonomy**: Give the User clear options, not just "I can't do this".

## Related Files

- `agent/00_system/04_error_handling.md`
- `agent/00_system/08_context_management.md`
- `agent/00_system/12_token_budget_and_model_switching.md`
