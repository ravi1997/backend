# Example: New Node.js Project Walkthrough

1. **Trigger**: User runs `new_project_entrypoint`.
2. **Context**:
   - Stack: Node.js (Express)
   - Goal: REST API
3. **Execution**:
   - Agent detects empty dir.
   - Agent verifies `node` and `npm` installed (Gate).
   - Agent runs `npm init -y`.
   - Agent installs `express`, `jest`, `eslint`.
   - Agent creates `src/index.js` (Hello World).
   - Agent runs `npm test` (Green).
4. **State**: `PROJECT_STATE.md` -> `stage: "MVP_READY"`.
