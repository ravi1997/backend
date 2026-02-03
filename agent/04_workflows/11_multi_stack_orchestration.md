# Workflow: Multi-Stack Orchestration

**ID**: WF-11  
**Trigger**: Multi-stack repo detected or requested  
**Output**: Coordinated build/test/release artifacts

---

## 1. Context Loading

### 1.1 Read Stack Map

- **Action**: Read `plans/Detection/STACK_MAP.md`.
- **Verify**: Ensure all subprojects are identified and mapped to valid stacks.
- **Fail**: If STACK_MAP is missing or invalid (run `detect_multi_stack` first).

### 1.2 Dependency Graph

- **Action**: Analyze dependency order (e.g., Shared Libs → Backend → Frontend).
- **Plan**: Create a "Build Order Plan" in `plans/Detection/BUILD_ORDER.md`.

---

## 2. Parallel Execution (Per Subproject)

For each subproject (in topological order of dependency):

### 2.1 Context Switch

- **Action**: Temporarily set context to subproject root.
- **Load Gate**: Load `gate_<stack>.md` for that subproject.

### 2.2 Execution

- **Step**: Run `gate_<stack>_build`.
- **Step**: Run `gate_<stack>_tests` (Unit tests only).
- **Step**: Run `gate_<stack>_style`.
- **Step**: Run `gate_<stack>_security`.

### 2.3 Result Aggregation

- **Success**: Mark subproject as PASS.
- **Failure**: Mark subproject as FAIL. Stop downstream dependents.

---

## 3. Integration Phase

### 3.1 Environment Setup

- **Action**: Spin up all dependency containers (DB, Redis).
- **Action**: Start Backend services (using `docker compose`).

### 3.2 Cross-Stack Tests

- **Action**: Run E2E tests (e.g., Cypress/Playwright) aimed at the full stack.
- **Action**: Validate API contracts (Frontend can talk to Backend).

### 3.3 Global Security

- **Action**: Run global security scan (Trivy on all images).
- **Action**: Check for leaked secrets across entire repo.

---

## 4. Release Preparation

### 4.1 Versioning

- **Strategy**: Determine if "Fixed Version" (all projects v1.2.0) or "Independent Version" (lerna/nx style).
- **Action**: Bump versions accordingly.

### 4.2 Changelog

- **Action**: Aggregate changelogs from all subprojects into a master `CHANGELOG.md`.

### 4.3 Artifacts

- **Action**: Build production Docker images for all services.
- **Action**: Package shared libs (if publishing).
- **Action**: Build static web assets.

---

## 5. Exit Criteria & State Update

### 5.1 Final Check

- [ ] All subprojects passed individual gates
- [ ] Integration tests passed
- [ ] Docker images built and scanned
- [ ] Documentation updated

### 5.2 State Update

- **Update**: `agent/09_state/state_release.md`
- **Status**: `READY_FOR_RELEASE` (if passed) or `BLOCKED` (if failed).

---

## Recovery Actions

- **Single Subproject Fail**: Isolate the failure. If it's a leaf node (e.g., just one frontend app), determine if partial release is possible (unlikely).
- **Integration Fail**: Check logs of all services. Revert changes if needed.

---

## Tooling Recommendation

- **Monorepo Tools**: Recommend using `Turborepo` or `Nx` for valid multi-stack orchestration if not present.
- **CI**: Generate a Matrix CI workflow.
