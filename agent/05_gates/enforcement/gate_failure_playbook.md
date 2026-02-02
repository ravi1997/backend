# Gate Failure Playbook

## Purpose

Standard operating procedure when a Gate (Quality, Security, etc.) yields a FAIL result.

## Steps

1. **Quarantine**: Halt all further implementation in the current workflow.
2. **Analysis**: Read the failure reason from the logs/state.
3. **Classification**:
   - **Trivial**: Typos, minor linting. (Agent fixes immediately).
   - **Significant**: Logic error, test failure. (Agent adopts `profile_implementer.md`).
   - **Severe**: Security breach, architecture mismatch. (Agent halts and requests human input).
4. **Fix**: Implement the correction.
5. **Re-Gate**: Re-run the specific Gate that failed.
6. **Log**: Document the failure and fix in `PROJECT_STATE.md`.

## Related Files

- `agent/00_system/04_error_handling.md`
