# Entrypoint: Orchestrator

## Purpose

Official entrypoint for orchestrated multi-agent operation. This workflow triggers the high-fidelity orchestration protocol to handle complex, multi-phase engineering tasks.

## Initial Trigger

Run this entrypoint when:

- The task requires multiple specialized roles (Architecture, Testing, Security, etc.).
- You are starting a significant new project or feature.
- You need absolute consistency across a large set of interrelated artifacts.
- The project involves complex stack dependencies (e.g., Docker + GitHub Actions + Multi-tier Backend).

## Execution Sequence

### Phase 1: Orchestration Bootstrap

1. Read `agent/AGENT_MANIFEST.md` to confirm system boundaries.
2. Read `agent/00_system/10_orchestration_protocol.md` for the execution model.
3. Read `agent/00_system/11_prompt_router.md` to prepare the routing logic.
4. Initialize `plans/Orchestration/` directory.

### Phase 2: Intelligence Routing

1. Execute `agent/06_skills/metacognition/skill_prompt_routing.md`.
2. Select primary prompt from `prompts/by_entrypoint/` or `prompts/by_scenario/`.
3. Select supporting prompts (DevOps, Security, etc.).
4. Record decision in `plans/Orchestration/prompt_routing.md`.

### Phase 3: Task Decomposition

1. Execute `agent/06_skills/metacognition/skill_subtask_decomposition.md`.
2. Map workflow steps to sub-agent profiles in `agent/03_profiles/`.
3. Create `plans/Orchestration/taskboard.md`.

### Phase 4: Sequential Execution

For each sub-agent defined in the taskboard:

1. Provision the sub-agent wrap using `agent/07_templates/orchestration/SUBAGENT_BRIEF.md`.
2. Apply the matching prompt from `prompts/orchestrator/01_subagent_profile_prompts/`.
3. Collect the deliverable using `agent/07_templates/orchestration/SUBAGENT_OUTPUT.md`.
4. Store results in `plans/Orchestration/subagents/`.

### Phase 5: Synthesis & Review

1. Execute `agent/06_skills/metacognition/skill_merge_and_reconcile.md`.
2. Resolve any contradictions using `agent/07_templates/orchestration/CONFLICT_RESOLUTION.md`.
3. Finalize `plans/Orchestration/final_action_plan.md`.

### Phase 6: State & Gate Audit

1. Run all mandatory gates from `agent/05_gates/`.
2. Record results in `plans/Orchestration/gate_results.md`.
3. Update all relevant state files in `agent/09_state/`.

## Stop Conditions

- **Success**: All sub-agent tasks complete, all gates pass (100%), and state is finalized.
- **Critical Failure**: Any gate fails twice, or a logic conflict exists that cannot be auto-resolved.

## Final Response Format

The response must include:

1. **Selection Summary**: Which prompts were routed.
2. **Sub-agent Status**: Success/failure of each role.
3. **Artifact Index**: Relative paths to all generated plans and code.
4. **State Transition**: Previous state → New state.
