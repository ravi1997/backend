# Universal QA Gates

**Purpose:** Define mandatory quality gates that every feature and release must pass.
**Applicability:** All stacks (C++, Java, Python, Flutter, Web).
**Enforcement:** Mandatory for `feature_delivery` and `deploy` workflows.

---

## The 5 Golden Gates

Every unit of work (feature, bugfix, hotfix) must pass these 5 gates before merge/deploy.

### Gate 1: Compilation / Build
- **Requirement:** The code must compile or build without errors.
- **Strict Mode:** No warnings allowed (treat warnings as errors) where possible.
- **Verification:** `exit code 0` from build command.

### Gate 2: Tests
- **Requirement:** All tests must pass.
- **Scope:**
    - Unit Tests: 100% pass rate.
    - Integration Tests: 100% pass rate (if env available).
- **Metric:** Maintain or improve code coverage (do not decrease it).
- **Verification:** `exit code 0` from test runner.

### Gate 3: Linting & Formatting
- **Requirement:** Code must adhere to style guides.
- **Verification:**
    - Linter: No errors (e.g., eslint, flake8, clippy, checkstyle).
    - Formatter: Check or Auto-fix applied (e.g., prettier, black, clang-format).

### Gate 4: Security Baseline
- **Requirement:** No known high/critical vulnerabilities introduced.
- **Verification:**
    - Dependency Scan: `npm audit`, `pip-audit`, `snyk`, or equivalent.
    - Static Analysis: Basic security linter if available.

### Gate 5: Documentation & Rollback
- **Requirement:** No "ghost code" (undocumented changes).
- **Checklist:**
    - [ ] `README.md` or specialized doc updated if behaviors changed.
    - [ ] `CHANGELOG.md` entry added (if applicable).
    - [ ] Rollback strategy confirmed (database migrations are reversible, feature flags exists, or artifacts differ).

---

## Handling Missing Environments

If a specific environment (e.g., Integration Server, Device Farm) is **missing**, you cannot pass Gate 2 fully.

**Policy:**
1.  **Confidence Score:** Reduce reported confidence in `PR_SUMMARY.md`.
2.  **Reproducible Setup:** You MUST provide a "Reproducible Environment Setup" section in the PR, explaining how a human reviewer can verify the change manually (e.g., Docker container, local script).
3.  **Bypass:** Explicitly mark as `[SKIPPED: NO ENV]` with a justification.

---

## Role Responsibilities

### Developer
- Ensures Gates 1-3 pass locally before opening a PR.
- Writes tests.

### Tester (Agent/Human)
- Verifies Gate 2 (Tests) thoroughly.
- Checks edge cases not covered by happy-path tests.

### Reviewer
- Verifies Gate 4 (Security) and Gate 5 (Docs).
- Checks code logic and design patterns.
