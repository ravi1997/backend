# Skill: Merge and Reconcile

## Purpose

Synthesizes the outputs of multiple sub-agents into a single, unified execution plan or codebase, resolving any logical or structural contradictions.

## Execution Logic

1. **Aggregation**:
   - Collect all `plans/Orchestration/subagents/*_output.md` deliverables.
   - Scan for all new files created across the orchestration run.

2. **Contradiction Detection**:
   - Check for conflicting architectural decisions (e.g., Architect says "Postgres", Implementer writes "MongoDB").
   - Find missing dependencies (e.g., Implementation references a requirement not in the SRS).
   - Verify that all Security Audit recommendations are addressed in the final implementation.

3. **Reconciliation**:
   - Use `agent/07_templates/orchestration/CONFLICT_RESOLUTION.md` to document and solve issues.
   - Profile Authority Hierarchy:
     1. Security Auditor (Safety first)
     2. Architect (Structural integrity)
     3. Analyst (Business logic)
     4. Implementer (Execution)

4. **Consistency check**:
   - Ensure all naming conventions defined in `agent/08_plan_output_contract/` are met.
   - Verify that and `agent/09_state/` updates are mutually consistent.

## Output

- Create `plans/Orchestration/merge_report.md`.
- Finalize `plans/Orchestration/final_action_plan.md`.
