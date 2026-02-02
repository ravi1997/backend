# Token Safety Checklist

## Purpose

To ensure the Agent OS maintains operational continuity and prevents data loss due to token budget exhaustion.

## Verification Protocol

**Frequency**:

- Before starting any "Large Work Item" (> 500 lines of code/text).
- When token usage crosses a "Safety Threshold" (YELLOW/ORANGE).
- Before attempting a Model Switch.

## Checklist

### 1. Continuity Preparedness

- [ ] **Snapshot Directory Exists**: `plans/Continuity/` is present.
- [ ] **State is Current**: `agent/09_state/` files are up-to-date.
- [ ] **Git Cleanliness**: No uncommitted critical changes in working tree (where possible).

### 2. Risk Assessment

- [ ] **Current Budget Level**: [GREEN / YELLOW / ORANGE / RED / CRITICAL]
- [ ] **Estimated Task Cost**: Does the remaining budget cover the next action?
- [ ] **Fallback Plan**: If budget hits limit mid-task, is the resume point clear?

### 3. Active Management

- [ ] **Snapshot Created**: If YELLOW+, `CONTEXT_SNAPSHOT.md` exists and is populated.
- [ ] **Context Optimized**: If ORANGE+, unused skills/rules are unloaded.
- [ ] **Chunking Enabled**: Long outputs are planned as incremental writes.
- [ ] **Model Switch Ready**: (Use ONLY if platform supports)
  - [ ] Target model verified.
  - [ ] Switch API/Command confirmed.
  - [ ] Pre-switch snapshot saved.

### 4. Handoff Integrity

- [ ] **All Files Written**: No content exists only in conversation history.
- [ ] **Decisions Logged**: `plans/Continuity/DECISIONS.md` captures recent choices.
- [ ] **Next Steps Defined**: `plans/Continuity/NEXT.md` has clear instructions.
- [ ] **User Informed**: (If exiting) User knows exactly how to resume.

## Failure Criteria (STOP if any true)

- [ ] Token usage is CRITICAL (> 95%) and no snapshot exists.
- [ ] Output buffer contains > 500 lines of unsaved text.
- [ ] Model switch attempted without pre-switch snapshot.

## Related Files

- `agent/00_system/12_token_budget_and_model_switching.md`
- `agent/06_skills/metacognition/skill_continuity_snapshot.md`
