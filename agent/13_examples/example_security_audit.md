# Example: Security Audit

## Scenario

Running a weekly scan on a mature project.

## Steps

1. **Command**: `run_security_audit_only.md`.
2. **Tool**: Agent runs `pip-audit`. Finds 1 dependency vulnerability in `requests`.
3. **Tool**: Agent runs secret scanner. Finds an old AWS key in a `.bak` file.
4. **Action**:
   - Updates `requests` to the latest version.
   - Deletes the `.bak` file and uses BFG to scrub the AWS key from history.
5. **State**: Updates `agent/09_state/SECURITY_STATE.md` with "Audit Status: CLEARED".
