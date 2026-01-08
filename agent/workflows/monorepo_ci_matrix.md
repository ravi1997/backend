# Monorepo: CI Matrix Generation

**Purpose**: Execute Build, Test, and Lint jobs in parallel for specific components.
**When to use**: In CI pipelines, or locally when validating multiple components.
**Prerequisites**: Component List (from `monorepo_change_impact.md` or manual selection).
**Type**: Monorepo Workflow

---

## Workflow Contract

| Attribute | Details |
| :--- | :--- |
| **Inputs** | List of Components / `ALL` |
| **Outputs** | Pass/Fail status per component |
| **Policy** | Fail Fast or Fail at End (Configurable) |
| **Scope Rule** | Security/Perf checks run on Active Scope first |

---

## Step 1: Input Resolution

Determine the scope of the matrix.

**Option A: Impact-Based (Smart)**
- Input: `AFFECTED_COMPONENTS` from `monorepo_change_impact.md`.
- Action: Generate jobs only for these components.

**Option B: Full Scope (Nightly/Master)**
- Input: `ALL`.
- Action: Generate jobs for every component in `agent/COMPONENT_GRAPH.md`.

---

## Step 2: Matrix Definition

For each target component, construct the job definition.

**Job Template:**
```yaml
id: [component-id]
path: [component-path]
stack: [detected-stack]
steps:
  - build
  - test
  - lint
```

**Stack-Specific Commands:**
Retrieve commands from `agent/components/[id].md` or `agent/stacks/[stack].md`.

- **Node/Web**:
  - Build: `npm run build`
  - Test: `npm test`
  - Lint: `npm run lint`
- **Python**:
  - Build: `pip install -r requirements.txt` (Environment setup)
  - Test: `pytest`
  - Lint: `pylint` / `flake8`
- **Java/Maven**:
  - Build: `mvn package -DskipTests`
  - Test: `mvn test`

---

## Step 3: Execution Strategy

**Parallel execution** is recommended for independent components.

### 3.1: Build Phase
- Run `build` for all components.
- *Dependency Order*: If Component A depends on B, build B first. (Or use tools like `Nx` / `Bazel` to handle this).

### 3.2: Test & Lint Phase
- Can usually run fully in parallel once artifacts are built.
- **Fail Fast**: Stop if critical components fail.

### 3.3: Global Checks (Root)
- If `root` was affected, run global checks (e.g., repository-wide formatting, dependency audits).

---

## Step 4: Security & Performance Scoping

**Rule**: Security and Performance workflows must run within active scope first, then optionally expand.

**Security:**
- Run `npm audit` / `safety check` **only** inside the directory of the affected component first.
- If high severity issues found, block.
- *Expansion*: Run global scan if `root` dependencies changed.

**Performance:**
- Run benchmark suite for the specific component (e.g., `lighthouse` for a specific web app).

---

## Step 5: Aggregation & Reporting

Collect results from all jobs.

- **Status**:
  - ✅ All jobs Passed.
  - ❌ One or more jobs Failed.
  - ⚠️ Skipped (No changes detected).

- **Artifacts**:
  - Gather test reports (JUnit XML, coverage) from each component.
  - Combine into a master report.

---

## Completion Criteria

- ✅ All targeted components have executed their Build/Test/Lint lifecycle.
- ✅ Report clearly identifies which component failed.
- ✅ No "global" failure blocked a "local" success (unless configured otherwise).
