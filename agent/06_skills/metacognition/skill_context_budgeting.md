# Skill: Context Budgeting & Token Optimization

## Purpose

Provides a procedure for selecting the minimal necessary set of Agent OS components and actively managing token usage to prevent exhaustion.

## Input Contract

- **Task Domain**: (e.g., Python Implementation, Node Security Audit).
- **Current Phase**: (e.g., BOOTSTRAP, SPEC, DEV, RELEASE).
- **Current Token Level**: [GREEN / YELLOW / ORANGE / RED].

## Execution Procedure

### 1. Identify Core Set (Tier 1)

- Always include:
  - `agent/AGENT_MANIFEST.md`
  - `agent/00_system/00_principles.md`
  - `agent/09_state/PROJECT_STATE.md`
  - `agent/00_system/12_token_budget_and_model_switching.md`

### 2. Activate Domain Context (Tier 2)

- Based on the detected **Stack** from `agent/02_detection/`:
  - **If Python**: Activate `agent/11_rules/stack_rules/python_rules.md` and `agent/05_gates/by_stack/python/`.
  - **If Node**: Activate `agent/11_rules/stack_rules/node_rules.md` and `agent/05_gates/by_stack/node/`.
  - **If C++**: Activate `agent/11_rules/stack_rules/cpp_rules.md` and `agent/05_gates/by_stack/cpp/`.
  - Repeat for all supported stacks.

### 3. Activate Workflow Context (Tier 3)

- Load exactly ONE workflow file from `agent/04_workflows/` matching the current task.
- Load exactly ONE profile from `agent/03_profiles/`.

### 4. Continuous Optimization (Dynamic)

**If Level is GREEN (< 60%)**:

- Standard operation. Load Skills/Templates as needed.

**If Level is YELLOW (60-75%)**:

- **Consolidate**: Close any file viewers not immediately needed.
- **Summarize**: Update `plans/Continuity/PROGRESS.md` with recent findings.
- **Snapshot**: Verify `plans/Continuity/CONTEXT_SNAPSHOT.md` exists.

**If Level is ORANGE (75-85%)**:

- **Context Diet**: Unload Tier 2 (Stack Rules) if not currently coding.
- **Reference Only**: Do not read full files; use `grep_search` to find specific lines.
- **Chunking**: Break all outputs > 300 lines into multiple file write operations.

**If Level is RED (> 85%)**:

- **Critical Core Only**: Unload EVERYTHING except `12_token_budget_and_model_switching.md` and `PROJECT_STATE.md`.
- **Handoff Mode**: Focus solely on writing `plans/Continuity/NEXT.md` and exiting.

## Stop Conditions

- Total "Knowledge Base" files loaded in context must not exceed 10 MD files at a time.
- Context window usage for Agent OS rules must be < 15% of total capacity.
- Continuity snapshot verified if > YELLOW.

## Output Contract

- **Context Config**: List of active files for the current sub-agent session.
- **Budget Report**: Number of tokens/files dedicated to system logic vs. project code.
- **Optimization Action**: [NONE / CONSOLIDATED / PRUNED / CRITICAL_PURGE]

## Related Files

- `agent/00_system/08_context_management.md`
- `agent/00_system/11_prompt_router.md`
- `agent/00_system/12_token_budget_and_model_switching.md`
