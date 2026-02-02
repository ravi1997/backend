# Scenario: Incomplete or Ambiguous User Input

## Purpose

Handling situations where the user provides vague, incomplete, or contradictory instructions.

## Inputs

- User request that lacks critical details (e.g., "Make it better", "Fix the app").

## Clarification Phase (Adopt `profile_analyst_srs.md`)

1. **Question Generation**: Use `agent/06_skills/analysis/skill_verify_reqs.md` to identify missing information:
   - **Who**: Which user role is affected?
   - **What**: What specific behavior needs to change?
   - **Why**: What problem does this solve?
   - **Success Criteria**: How will we know it's done?
2. **Structured Questionnaire**: Present questions in a numbered list, saved to `plans/Questions/CLARIFICATION_[ID].md`.
3. **Context Gathering**: Review existing SRS and state files to infer possible intent.

## Interpretation Phase (Adopt `profile_rule_checker.md`)

1. **Assumption Documentation**: If the user doesn't respond, make reasonable assumptions and document them clearly:
   - "ASSUMPTION: By 'better', we interpret this as 'faster response time'."
2. **Risk Flagging**: Mark assumptions as "HIGH RISK" if they could lead to wasted work.
3. **Approval Gate**: Do NOT proceed with HIGH RISK assumptions without explicit user confirmation.

## Execution Phase (Adopt `profile_implementer.md`)

1. **Minimal Viable Change**: Implement the smallest possible change that could satisfy the request.
2. **Demo**: Show the result to the user for feedback.
3. **Iteration**: Refine based on feedback.

## STOP Condition

- User confirms the interpretation is correct and approves the implementation.

## Related Files

- `agent/04_workflows/03_srs_generation.md`
- `agent/00_system/03_decision_policy.md`
