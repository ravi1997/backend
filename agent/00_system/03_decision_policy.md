# Decision Policy

## Purpose

Provides a logic framework for the Agent to make autonomous decisions while ensuring they are reversible and justified.

## Decision Matrix

| Risk Level | Definition | Authority | Action Required |
| --- | --- | --- | --- |
| **Low** | Typos, code style, doc updates. | Autonomous | Proceed and log. |
| **Medium** | New functions, dependency updates, refactors. | Peer Review | Propose in PR/Task, wait for ACK. |
| **High** | Schema changes, security policy, architecture. | Human-in-Loop | Stop, present options, wait for signature. |
| **Critical** | Data deletion, credential rotation, API keys. | Prohibited | Never execute autonomously. |

## Procedure

1. **Identify**: Determine the Risk Level of the proposed action.
2. **Check Token Budget**: Assess if action may trigger token safety mode (see `agent/00_system/12_token_budget_and_model_switching.md`).
3. **Consult Rules**: Check `agent/11_rules/` for any specific constraints.
4. **Justify**: Write a 1-sentence "Rationale" for the decision.
5. **Execute/Wait**: Based on the Matrix, either perform the action or pause.
6. **Log**: Record the decision in `agent/09_state/PROJECT_STATE.md` under "Recent Decisions".

## Reversibility Rule

Every "Medium" or "High" risk decision must have a "Rollback Plan".

- *Example*: Before migrating a database, the Agent must ensure a backup command is identified.

## Related Files

- `agent/00_system/03_decision_policy.md`
- `agent/00_system/12_token_budget_and_model_switching.md`
- `agent/05_gates/enforcement/gate_failure_playbook.md`
