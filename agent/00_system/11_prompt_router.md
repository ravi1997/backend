# System Component: Prompt Router & Orchestrator

## Purpose

Acts as the "Air Traffic Controller" for the Agent OS, directing specific tasks to the correct sub-agent profiles and ensuring modular context loading.

## Routing Logic

When a task is received, the Router evaluates the **Complexity** and **Domain**:

| Task Type | Domain | Profile Target | Context Stack |
| --- | --- | --- | --- |
| Requirement Mining | Analysis | `profile_analyst_srs.md` | `agent/07_templates/srs/` |
| Feature Implementation | Implementation | `profile_implementer.md` | `agent/06_skills/implementation/` |
| Infrastructure/CI | DevOps | `profile_devops.md` | `agent/06_skills/devops/` |
| Bug Fix | Implementation | `profile_implementer.md` | `agent/01_entrypoints/scenarios/` |
| Security Audit | Security | `profile_security_auditor.md` | `agent/10_security/` |
| PR Review | Quality | `profile_pr_reviewer.md` | `agent/12_checks/` |

## Modular Activation Protocol

To prevent context bloat, the Router must enforce these rules:

1. **Strict Filtering**: Only pass the specific `agent/11_rules/stack_rules/[stack]_rules.md` relevant to the project.
2. **Skill Injection**: Do not provide the list of all skills. Inject only the specific skill snippet needed for the current sub-task.
3. **Template Precision**: Only load the template relevant to the current output contract (e.g., `SRS_INDEX.md` or `FEATURE_SPEC.md`).

## Handoff Procedure

1. **Decomposition**: Use `agent/06_skills/metacognition/skill_subtask_decomposition.md` to break the goal into sub-agent tasks.
2. **Briefing**: Generate a `SUBAGENT_BRIEF.md` with explicit Inputs/Outputs.
3. **Execution**: Transition to the target profile.
4. **Reconciliation**: Use `agent/06_skills/metacognition/skill_merge_and_reconcile.md` to integrate sub-agent results.

## Related Files

- `agent/00_system/10_orchestration_protocol.md`
- `agent/07_templates/orchestration/`
- `agent/03_profiles/`
