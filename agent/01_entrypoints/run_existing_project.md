# Entrypoint: Run Existing Project (Deep)

## Purpose

The primary trigger when the Agent is introduced to an already established codebase.

## Inputs

- Access to the root directory.
- User's primary objective (e.g., "Add a login feature" or "Fix bug X").

## Procedure (Adopt `profile_rule_checker.md`)

1. **Intake**: Execute `agent/04_workflows/01_intake_and_context_build.md`.
2. **Context Map**: Run `agent/06_skills/knowledge_extraction/skill_discover_monorepo.md` to map the topology.
3. **Health Audit**: Run `agent/02_detection/detect_repo_health.md` to establish a baseline.
4. **Scenario Selection**:
   - If objective is a bug: Route to `agent/01_entrypoints/scenarios/scenario_bug_fix.md`.
   - If objective is a refactor: Route to `agent/01_entrypoints/scenarios/scenario_refactor.md`.
   - If objective is a new feature: Route to `agent/04_workflows/06_feature_implementation_loop.md`.
   - If objective is vague: Initiate `agent/04_workflows/03_srs_generation.md`.
5. **State Initialization**: Update `agent/09_state/PROJECT_STATE.md` with the selected path.
6. **Execution**: Proceed with the chosen scenario.

## STOP Condition

- The selected Scenario is complete and all Gates pass.
