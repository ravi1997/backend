# Workflow: Intake and Context Build

## Purpose

Standardized discovery process to transform a vague USER_REQUEST into a clear, stack-aware project context.

## Required Inputs

- **User Command**: Initial prompt.
- **Repository Access**: Read access to the current directory.

## Expected Outputs

- **Stack Identification**: Recorded in `agent/09_state/STACK_STATE.md`.
- **Initial Project Map**: Generated using `agent/06_skills/knowledge_extraction/skill_generate_project_map.md`.
- **Intake Report**: Logged in `agent/09_state/PROJECT_STATE.md`.

## Procedure (Adopt `agent/03_profiles/profile_analyst_srs.md`)

0. **Token Risk Check**: Assess current token budget per `agent/00_system/12_token_budget_and_model_switching.md`. If > 60%, create snapshot.
1. **Inventory**: Run a recursive scan and file count. Use `agent/06_skills/knowledge_extraction/skill_discover_monorepo.md` if multiple packages are found.
2. **Detection**: Execute `agent/02_detection/` to identify the primary stack and DevOps presence.
3. **Baseline Audit**:
    - If existing project: Run `agent/04_workflows/02_repo_audit_and_baseline.md`.
    - If new project: Run `agent/12_checks/checklists/intake_checklist.md`.
4. **Context Extraction**: Run `agent/06_skills/knowledge_extraction/skill_extract_context.md` on detected README and config files.
5. **User Calibration**: Ask specific questions regarding:
    - Target Environment.
    - Security Requirements.
    - Performance Constraints.
6. **State Initialization**: Update state to "BOOTSTRAP".

## Failure Modes & Recovery

- **Unknown Stack**: If detection fails, use `agent/00_system/09_graceful_degradation.md` to trigger a generic stack setup and request manual stack name from User.
- **Empty Repo**: If no files found, transition immediately to `agent/01_entrypoints/run_new_project.md`.

## Required Gates

- `agent/12_checks/checklists/intake_checklist.md` (Must Pass)

## State Update

- Update `agent/09_state/PROJECT_STATE.md`:
  - Set `current_stage` to "INTAKE_COMPLETE".
  - Update `stack_context` with detected stack.

## Related Files

- `agent/00_system/12_token_budget_and_model_switching.md`
- `agent/02_detection/detect_stack_signals.md`
- `agent/09_state/PROJECT_STATE.md`
