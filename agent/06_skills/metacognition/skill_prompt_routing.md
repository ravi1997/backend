# Skill: Prompt Routing & Orchestration Logic

## Purpose

Selecting the optimal sub-agent profile and context stack to maximize reasoning quality while staying within token limits.

## Input Contract

- **User Intent**: Parsed from the latest request.
- **Repository Context**: Detected stack/type.

## Execution Procedure

1. **Intent Classification**:
    - **Drafting**: Route to `profile_analyst_srs.md`.
    - **Implementing**: Route to `profile_implementer.md`.
    - **Validating**: Route to `profile_tester.md`.
    - **Governing**: Route to `profile_rule_checker.md`.
2. **Context Assembly**:
    - Call `agent/06_skills/metacognition/skill_context_budgeting.md` to select files.
3. **Handoff Briefing**:
    - Populate `agent/07_templates/orchestration/SUBAGENT_BRIEF.md`.
4. **Transition**: Instruct the AI to "Adopt Profile X".

## Failure Modes

- **Ambiguous Intent**: If the task maps to multiple profiles, use the Planner to split the sub-tasks before routing.

## Output Contract

- **Routing Decision**: Logged in the internal trace.
- **Active Profile**: The chosen sub-agent persona.
