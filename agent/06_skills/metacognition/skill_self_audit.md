# Skill: Self-Audit & Meta-Improvement

## Purpose

Enables the Agent to evaluate its own performance and suggest optimizations to the Agent OS.

## Procedure

### 1. Failure Analysis

After any Tool Error (`E-XXXX`) or Gate Failure (`FAIL`):

1. **Root Cause**: Determine if the failure was due to:
   - Ambiguous instructions in a workflow.
   - Missing stack fingerprint.
   - Faulty logic in its own implementation.
   - Token budget exhaustion (check `E-TOKEN-999`).
2. **Persistence**: Has this happened before? (Check history or state).
3. **Token Risk**: Assess current token usage level per `agent/00_system/12_token_budget_and_model_switching.md`.

### 2. Efficiency Review

During the "Release" phase of a milestone:

1. **Cycle Time**: Did any step take longer than expected?
2. **User Friction**: Did the user have to correct the Agent multiple times on the same topic?
3. **Token Management**: Were continuity snapshots created when needed? Check `plans/Continuity/` for large tasks.
4. **Draft Improvement**: Create a proposal for updating the relevant `agent/` file.

### 3. Updating the Agent Folder

1. **Propose**: Generate the new file content.
2. **Cross-Ref**: Check `agent/00_system/06_templates_index.md` or `agent/04_workflows/` to ensure no breakages.
3. **Execute**: Overwrite the file after getting `[USER_APPROVAL]`.

## STOP Condition

- Every identified inefficiency has a corresponding "Improvement Task" in the backlog.
- Agent OS remains internally consistent.
- Token budget risk is assessed and documented.
- Continuity snapshots exist for all large tasks.

## Related Files

- `agent/00_system/12_token_budget_and_model_switching.md`
- `agent/06_skills/metacognition/skill_continuity_snapshot.md`
- `plans/Continuity/`
