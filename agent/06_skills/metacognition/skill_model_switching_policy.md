# Skill: Model Switching Policy

## Purpose

Defines the procedure for attempting model switching when token budget constraints are reached, including platform verification, pre-switch preparation, and fallback handling.

## Input Contract

- **Current Token Usage**: Percentage of budget consumed.
- **Trigger Level**: Current safety level (should be RED or CRITICAL).
- **Platform**: Execution environment (e.g., API, CLI, web interface).
- **Target Model**: Desired model with larger context or better efficiency.

## Execution Procedure

### 1. Verify Platform Support

**Critical**: Do NOT assume model switching is available.

Check if platform supports mid-session model switching:

- **API-based platforms**: Check API documentation for model switch endpoints.
- **CLI-based platforms**: Check for model selection flags or commands.
- **Web interfaces**: Check for model selector UI elements.

**Decision Point**:

- If switching IS supported → Proceed to Step 2.
- If switching is NOT supported → Skip to Step 7 (No-Switch Fallback).

### 2. Pre-Switch Preparation

Before attempting switch:

1. **Create Continuity Snapshot**: Use `agent/06_skills/metacognition/skill_continuity_snapshot.md`.
2. **Verify Snapshot**: Confirm all 4 files in `plans/Continuity/` are complete.
3. **Document Intent**: Add entry to `plans/Continuity/DECISIONS.md`:
   - Current model and context window.
   - Target model and expected improvement.
   - Rationale for switch (token exhaustion, performance, cost).
4. **Save Current State**: Ensure all work is written to disk, no in-memory-only data.

### 3. Identify Target Model

Select appropriate target model based on:

- **Context Window**: Larger than current model.
- **Capabilities**: Maintains or improves current model's abilities.
- **Availability**: Model is accessible on current platform.
- **Cost**: Within acceptable budget (if applicable).

**Common Targets**:

- If current is "standard" → Try "extended context" variant.
- If current is "small" → Try "medium" or "large" variant.
- If current is "fast" → Try "balanced" or "quality" variant.

### 4. Execute Switch Request

**Platform-Specific Actions**:

#### API-Based

```
POST /api/v1/session/switch-model
{
  "target_model": "model-name-extended",
  "preserve_context": true
}
```

#### CLI-Based

```bash
--model model-name-extended --resume-session
```

#### Web Interface

- Locate model selector dropdown.
- Select target model.
- Confirm context preservation option is enabled.

### 5. Await Confirmation

**Critical**: Do NOT proceed until platform confirms switch success.

Expected confirmations:

- **API**: HTTP 200 with `{"status": "switched", "model": "target-name"}`.
- **CLI**: Output message confirming model change.
- **Web**: UI update showing new model name.

**Timeout**: Wait maximum 30 seconds for confirmation.

### 6. Verify Context Preservation

After confirmed switch:

1. **Test Recall**: Reference a decision made earlier in session.
2. **Check State**: Verify access to `plans/Continuity/` files.
3. **Validate History**: Confirm conversation history is intact.

**If verification fails** → Treat as switch failure, proceed to Step 7.

**If verification succeeds**:

- Log successful switch in `plans/Continuity/DECISIONS.md`.
- Update token budget tracking with new model's limits.
- Resume work from last checkpoint.

### 7. No-Switch Fallback Protocol

**Trigger**: Platform does not support switching OR switch failed.

#### 7.1 Acknowledge Limitation

Output to user:

```
Token budget constraint detected. Model switching is not available on this platform.
Activating no-switch fallback protocol.
```

**Do NOT claim**: "Switching to larger model" or "Context expanded."

#### 7.2 Activate Context Diet

Use `agent/00_system/08_context_management.md` to:

- Unload non-essential stack rules.
- Remove inactive skills from memory.
- Purge old terminal outputs and logs.
- Summarize conversation history into `plans/Continuity/PROGRESS.md`.

#### 7.3 Enable Least-Token Mode

Per `agent/00_system/12_token_budget_and_model_switching.md`:

- Minimize explanations (terse, action-focused language).
- Skip examples (reference existing files instead).
- Batch operations (combine multiple edits).
- Defer non-critical work (postpone documentation updates).

#### 7.4 Implement Chunking

For any remaining large outputs:

- Divide into logical sections (by file, by feature, by component).
- Write incrementally using `write_to_file` or `replace_file_content`.
- Update `plans/Continuity/PROGRESS.md` after each chunk.
- Verify completion before marking task done.

#### 7.5 Prepare for Handoff

If work cannot complete within remaining budget:

- Finalize continuity snapshot with current state.
- Document exact resume point in `plans/Continuity/NEXT.md`.
- Inform user: "Token budget insufficient to complete task. Snapshot saved to `plans/Continuity/`. Please start new session with snapshot reference."

## Stop Conditions

- Model switch confirmed successful AND context verified.
- OR no-switch fallback fully activated.
- OR user informed of handoff requirement.

## Output Contract

- **Switch Status**: SUCCESS / FAILED / NOT_SUPPORTED
- **Active Model**: Name of current model after procedure.
- **Context Status**: PRESERVED / LOST / N/A
- **Fallback Activated**: YES / NO
- **Snapshot Location**: `plans/Continuity/` (if created)

## Failure Modes

### Platform Rejects Switch

**Symptom**: API returns error, CLI shows unsupported flag, UI has no selector.

**Recovery**:

1. Log error in `plans/Continuity/DECISIONS.md`.
2. Immediately activate no-switch fallback (Step 7).
3. Do NOT retry switch (wastes tokens).

### Context Lost After Switch

**Symptom**: New model session has no memory of previous conversation.

**Recovery**:

1. Treat as critical failure.
2. Load continuity snapshot from `plans/Continuity/`.
3. Reconstruct state from snapshot files.
4. Inform user of context loss and recovery actions.

### Switch Timeout

**Symptom**: No confirmation received within 30 seconds.

**Recovery**:

1. Assume switch failed.
2. Activate no-switch fallback.
3. Log timeout in `plans/Continuity/DECISIONS.md`.

## Do-Not-Hallucinate Rules

### Prohibited Claims

- **NEVER** say "Switched to [model]" without platform confirmation.
- **NEVER** say "Context window expanded" without verification.
- **NEVER** claim "Unlimited budget" or "No token limits."
- **NEVER** invent model names or capabilities.

### Required Honesty

- **ALWAYS** state if switch was attempted but not confirmed.
- **ALWAYS** acknowledge when platform does not support switching.
- **ALWAYS** inform user if fallback protocol is activated.
- **ALWAYS** report if context was lost during switch.

## Examples

### Example 1: Successful Switch (API Platform)

**Context**: Token usage at 88%, API supports switching.

**Actions**:

1. Create continuity snapshot → COMPLETE.
2. Request switch to "gpt-4-extended" → API returns 200.
3. Verify context by referencing earlier decision → SUCCESS.
4. Log switch in DECISIONS.md.
5. Resume work with expanded budget.

**Result**: Switch successful, work continues.

### Example 2: Switch Not Supported (CLI Platform)

**Context**: Token usage at 90%, CLI has no switch flag.

**Actions**:

1. Check CLI help for switch option → NOT FOUND.
2. Output: "Model switching not available on this platform."
3. Activate context diet → Unload 3 inactive stacks.
4. Enable least-token mode → Terse responses.
5. Implement chunking for remaining output.

**Result**: No-switch fallback activated, work continues with constraints.

### Example 3: Switch Failed (Context Lost)

**Context**: Token usage at 92%, switch attempted but context lost.

**Actions**:

1. Request switch → Platform confirms.
2. Test recall → FAILED (no memory of earlier work).
3. Load `plans/Continuity/CONTEXT_SNAPSHOT.md`.
4. Reconstruct: Stack=Python, Phase=DEV, Task=Feature-123.
5. Inform user: "Context lost during switch. Recovered from snapshot."

**Result**: Context reconstructed, work resumes from snapshot.

## Related Files

- `agent/00_system/12_token_budget_and_model_switching.md`
- `agent/00_system/08_context_management.md`
- `agent/06_skills/metacognition/skill_continuity_snapshot.md`
- `agent/06_skills/metacognition/skill_context_budgeting.md`
- `plans/Continuity/DECISIONS.md`
