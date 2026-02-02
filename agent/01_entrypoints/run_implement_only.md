# Entrypoint: Run Implement Only

## Purpose

Used to start coding based on an existing plan and SRS.

## Inputs

- Approved Backlog in `agent/09_state/BACKLOG_STATE.md`.
- Approved SRS and Architecture.

## Procedure

1. **Profile**: `profile_implementer.md`.
2. **Selection**: Pick the highest priority task from the backlog.
3. **Execution**: Follow `agent/04_workflows/06_feature_implementation_loop.md`.
4. **Continuous Testing**: After each feature, run `agent/04_workflows/07_testing_and_validation.md`.

## Stop Conditions

- No more tasks in "Todo" status.

## Related Files

- `agent/04_workflows/06_feature_implementation_loop.md`
