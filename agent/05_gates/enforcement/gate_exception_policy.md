# Gate Exception Policy

## Purpose

Rules for when a Gate can be bypassed (Use with extreme caution).

## Conditions for Exception

1. **Proto-Speed**: When building a rapid prototype and quality gates are temporarily disabled (Must be re-enabled for M1).
2. **Environment Blocker**: When a test fails due to environment issues outside Agent control (e.g., 3rd party API down).
3. **Implicit Approval**: When the Human User explicitly says "Ignore and proceed".

## Procedure

1. Create a "Gate Exception" entry in `agent/09_state/PROJECT_STATE.md`.
2. Define the "Sunset Date" for the exception (When will it be fixed?).
3. Add a `[GATE_BYPASS]` comment in the source code or doc.
