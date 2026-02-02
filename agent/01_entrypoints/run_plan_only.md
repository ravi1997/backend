# Entrypoint: Run Plan Only

## Purpose

Used to generate the technical roadmap (backlog, milestones, architecture) for an existing SRS.

## Inputs

- Existing SRS in `plans/SRS/`.

## Procedure

1. **Profile**: `profile_architect.md`.
2. **Decomposition**: Breakdown SRS into milestones.
3. **Backlog**: Populate `agent/09_state/BACKLOG_STATE.md`.
4. **Architecture**: Create diagrams in `plans/Architecture/`.

## Stop Conditions

- Backlog is approved.

## Related Files

- `agent/04_workflows/05_milestones_and_backlog.md`
