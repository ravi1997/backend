# System Procedure: Context & Memory Management

## Purpose

Ensures the Agent operates within its "Token Budget" by loading only relevant context and modularizing activation based on the detected stack and current phase.

## Modular Loading Rules (MANDATORY)

1. **Phase 0: Bootstrapping (Minimal)**
    - ALWAYS Load: `agent/AGENT_MANIFEST.md`, `agent/00_system/00_principles.md`.
    - NEVER Load: Gates, Skills, or specific Rules during initial intake.

2. **Phase 1: Detection (Stack Identification)**
    - Load: `agent/02_detection/`.
    - Result: Identify STACK and REPO_TYPE.

3. **Phase 2: Execution (Context Activation)**
    - **Stack-Specific Activation**: Load only the rules/gates/skills for the identified stack.
        - *Example*: If Python is detected, ONLY load `agent/11_rules/stack_rules/python_rules.md` and `agent/05_gates/by_stack/python/`.
        - *Example*: If C++ is detected, ONLY load `agent/11_rules/stack_rules/cpp_rules.md` and `agent/05_gates/by_stack/cpp/`.
    - **Skill Budgeting**: Do NOT load all skills. Load specific skill files only when a Workflow step explicitly calls for them.

4. **Phase 3: Cleanup (Context Deactivation)**
    - Once a feature is "DONE" and gated, unload the specific Implementation skills/templates to make room for testing or deployment context.

## Context Budgeting Procedure

1. **Monitor Density**: If conversation history exceeds 20k tokens, initiate "Refinement".
2. **Check Token Budget**: Every 5 tool calls, assess token usage against budget (see `agent/00_system/12_token_budget_and_model_switching.md`).
3. **Trigger Continuity**: If token usage reaches YELLOW level (60%+), create continuity snapshot in `plans/Continuity/`.
4. **Summarize Session**: Condense recent tool outputs and decisions into `agent/09_state/PROJECT_STATE.md`.
5. **Purge Logs**: Clear internal scratchpads or temporary terminal outputs from memory.
6. **Activate Least-Token Mode**: If ORANGE level (75%+), minimize explanations and use chunking for large outputs.

## State Refresher Routine

1. **Sync**: Every 5 tool calls, refresh the "Top Level Goals" from `agent/09_state/PROJECT_STATE.md`.
2. **Validate**: Check if currently loaded rules still apply to the active task.

## Related Files

- `agent/00_system/11_prompt_router.md`
- `agent/00_system/12_token_budget_and_model_switching.md`
- `agent/06_skills/metacognition/skill_context_budgeting.md`
- `agent/09_state/PROJECT_STATE.md`
