# Skill: Integration Testing

## Purpose

Verifying the interaction between multiple components or external services (DB, API).

## Execution Procedure

1. **Environment Setup**: Ensure test databases or mock servers are running (e.g., via `docker-compose`).
2. **State Initialization**: Prepare the system state (e.g., seed database).
3. **Flow Execution**: Trigger the multi-step process being tested.
4. **Verification**: Check side effects in the database or external state.
5. **Cleanup**: Revert the system to the baseline.

## Output Contract

- **Integration Report**: Evidence of successful component handoffs.
