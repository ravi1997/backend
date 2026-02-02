# Skill: Subtask Decomposition

## Purpose

Breaks down a complex orchestration plan into discrete, profile-aligned tasks that can be executed by specialized "virtual" agents.

## Execution Logic

1. **Phase Breakdown**:
   - Divide the high-level objective into SDLC phases (Spec, Plan, Dev, Audit, Release).
   - Use the "Execution Order" defined in the primary selected prompt as a template.

2. **Role Mapping**:
   - Assign each phase to a profile from `agent/03_profiles/`.
   - **Planner**: Backlog and Milestones.
   - **Analyst**: Requirements (SRS).
   - **Architect**: ADPs, Diagrams, System Design.
   - **Implementer**: Code changes.
   - **Tester**: Test cases and execution.
   - **Security Auditor**: Vulnerability assessment.

3. **Input/Output Definition**:
   - For each sub-task, explicitly define the *required inputs* (previous task outputs) and *strict expected artifacts* (files to write).

4. **Dependency Graph**:
   - Sequence tasks to avoid race conditions (e.g., Code cannot be written before Architecture is approved).

## Rules

- **No Overlap**: Each sub-task must have a single owner profile.
- **Granularity**: A sub-task should represent no more than 20% of the total project scope.
- **State Awareness**: Every sub-task must include a step to update its relevant `agent/09_state/` file.

## Output

- Create or update `plans/Orchestration/taskboard.md`.
