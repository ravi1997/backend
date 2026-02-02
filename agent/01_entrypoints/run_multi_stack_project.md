# Entrypoint: Multi-Stack Project

**Workflow**: Multi-Stack Orchestration  
**Primary Agent**: Lead Architect  
**Output**: Coordinated build across all subprojects

---

## Trigger Condition

- User request: "run full build", "handle this monorepo", "deploy everything".
- Detection: `detect_multi_stack` identifies >1 stack in the repo.

---

## Execution Steps

### 1. Detection

- **Skill**: `detect_multi_stack`
- **Output**: `plans/Detection/STACK_MAP.md`
- **Verification**: User confirms detected map is correct (especially regarding shared libs).

### 2. Planning (Topological)

- **Role**: Lead Architect
- **Action**: Analyze dependency graph from STACK_MAP.
- **Output**: `plans/Detection/BUILD_ORDER.md` (which project builds first).

### 3. Orchestration

- **Workflow**: `11_multi_stack_orchestration.md`
- **Execution**:
  1. Iterate through `BUILD_ORDER`.
  2. For each project, switch context contextually.
  3. Run stack-specific workflows (`gate_build`, `gate_test`, etc.).
  4. Aggregate results.

### 4. Integration

- **Gate**: Global Integration Tests.
- **Action**: Spin up shared environment (Docker Compose).
- **Verify**: API contracts between Frontend/Backend.

### 5. Finalize

- **Gate**: Global Release Gate.
- **Action**: Generate release artifacts (images, binaries).
- **State**: Update `state_release.md`.

---

## Outputs

- `STACK_MAP.md`
- `BUILD_ORDER.md`
- Individual project artifacts
- Aggregated Test Report

---

## Stop Conditions

- **Partial Failure**: If a leaf node fails, mark it failed but continue parallel branches if unrelated.
- **Critical Failure**: If a shared library/service fails, STOP all dependent builds immediately.
