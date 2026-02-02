# Workflow: Architecture and Design

## Purpose

Define the technical structure of the solution.

## Inputs

- Approved SRS.

## Procedure

1. **Adopt Profile**: `profile_architect.md`.
2. **System Design**: Define high-level modules.
3. **Data Modeling**: Create ERD (Entity Relationship Diagram) using Mermaid.
4. **API Design**: Define endpoints or interface signatures.
5. **Sequence Diagrams**: Map complex workflows (like Auth or Payment).
6. **Storage**: Save all diagrams to `plans/Architecture/`.

## STOP Condition

- All core modules have a defined interface or diagram.

## Required Gates

- **Completeness**: Diagrams cover all SRS modules.
- **Feasibility**: Design uses supported stacks/technologies.

## State Update

- Update `agent/09_state/PROJECT_STATE.md`:
  - Set `current_stage` to "ARCHITECTURE_DEFINED".

## Related Files

- `agent/07_templates/diagrams/`
