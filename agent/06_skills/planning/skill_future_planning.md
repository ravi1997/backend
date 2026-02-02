# Skill: Future Planning

## Purpose

Analyze the existing codebase and current plans to identify, categorize, and detail potential future capabilities ("Epics") or features. This involves creating a structured library of future possibilities, fully detailed to SRS standards.

## Execution Procedure

1. **Context Acquisition**:
   - Recursively list and read key files in `src/` to understand the current technical implementation.
   - Read `plan/` or `plans/` to understand the currently active roadmap and avoid duplication.

2. **Opportunity Identification**:
   - Brainstorm future capabilities based on:
     - Logical extensions of current features.
     - Technical debt reduction and refactoring theories.
     - Market trends standard for this type of application.
     - "Moonshot" ideas that leverage the core architecture.

3. **Workspace Preparation**:
   - Create a directory `future_plans/` (if it does not exist) at the project root.

4. **Detailed Specification Generation**:
   - For *each* identified future opportunity (Epic):
     - Create a subdirectory: `future_plans/<epic_name_snake_case>/`.
     - Generate a comprehensive plan using the structure of the Agent OS SRS templates (`agent/07_templates/srs/`):
       - `00_executive_summary.md`: High-level vision and value proposition.
       - `01_functional_requirements.md`: detailed user stories and feature lists.
       - `02_technical_architecture.md`: Anticipated data models, API changes, and component interactions.
       - `03_risk_analysis.md`: Potential challenges and mitigation strategies.
     - Ensure the level of detail allows a developer to pick up the plan and start the `implementation` workflow immediately.

5. **Index Maintenance**:
   - Create or update `future_plans/README.md` to serve as a navigable index of all potential futures, summarized by impact and estimated effort.

## Output Contract

- A `future_plans/` directory containing populated sub-folders for each idea.
- High-fidelity markdown documents in each sub-folder comparable to an SRS (Software Requirements Specification).
