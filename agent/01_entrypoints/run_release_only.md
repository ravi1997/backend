# Entrypoint: Run Release Only

## Purpose

Used to finalize a version and prepare for production deployment.

## Inputs

- Current stable branch/state.

## Procedure

1. **Profile**: `profile_release_manager.md`.
2. **Verification**: Run `agent/05_gates/global/gate_global_release.md`.
3. **Doc Update**: Generate `plans/Release/RELEASE_NOTES.md`.
4. **Artifacts**: Package the build if required.
5. **State Update**: Update `agent/09_state/RELEASE_STATE.md`.

## Related Files

- `agent/04_workflows/10_release_process.md`
