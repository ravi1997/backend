# Scenario: Conflicting Requirements Resolution

## Purpose

Handling situations where the SRS contains contradictory requirements or when stakeholder feedback conflicts with the existing architecture.

## Inputs

- Two or more requirements that cannot coexist.
- User feedback that contradicts the approved SRS.

## Detection Phase (Adopt `profile_analyst_srs.md`)

1. **Conflict Identification**: When reading the SRS, flag any requirements that:
   - Use mutually exclusive terms (e.g., "Must be stateless" AND "Must maintain session").
   - Have impossible performance targets (e.g., "Sub-1ms response" on a network-dependent API).
   - Violate security principles (e.g., "Store passwords in plaintext for debugging").
2. **Stakeholder Mapping**: Identify which User Story or stakeholder requested each conflicting requirement.

## Analysis Phase (Adopt `profile_architect.md`)

1. **Trade-off Matrix**: Create a comparison table in `plans/Questions/CONFLICT_ANALYSIS.md`:
   - Option A: Pros, Cons, Risk Level.
   - Option B: Pros, Cons, Risk Level.
2. **Technical Feasibility**: Determine if a "Hybrid" solution exists that satisfies both requirements partially.
3. **Precedent Search**: Check if similar conflicts were resolved in `agent/09_state/PROJECT_STATE.md` under "Recent Decisions".

## Resolution Phase (Adopt `profile_rule_checker.md`)

1. **User Escalation**: Present the conflict and the trade-off matrix to the User.
2. **Decision Capture**: Once the User chooses, update the SRS to mark the rejected requirement as `[REJECTED - Reason: X]`.
3. **Architecture Sync**: Ensure the chosen path is reflected in `plans/Architecture/`.

## STOP Condition

- Conflict is resolved, documented, and the SRS is internally consistent.

## Related Files

- `agent/04_workflows/03_srs_generation.md`
- `agent/00_system/03_decision_policy.md`
