# Agent OS Prompts - Comprehensive Guide

## Table of Contents

1. [Entrypoint Prompts](#entrypoint-prompts)
2. [Scenario Prompts](#scenario-prompts)
3. [When to Use What](#when-to-use-what)
4. [Common Mistakes](#common-mistakes)
5. [Advanced Usage](#advanced-usage)

---

## Entrypoint Prompts

### `new_project.txt`

**When to Use**: Starting a brand new project from scratch.

**Preconditions**:

- Empty or nearly-empty directory
- High-level project idea
- Optional: preferred tech stack

**What It Does**:

1. Generates complete SRS with functional/non-functional requirements
2. Creates architecture diagrams (system overview, ERD)
3. Builds milestone plan and backlog
4. Initializes all state files

**Artifacts Produced**:

- `plans/SRS/` (3-5 documents)
- `plans/Architecture/` (2+ diagrams)
- `plans/Milestones/MILESTONE_PLAN.md`
- `agent/09_state/` (all state files initialized)

**Success Looks Like**: You have a complete plan ready for implementation, with clear acceptance criteria and a prioritized backlog.

**Common Mistakes**:

- ❌ Using this on existing projects (use `existing_project.txt` instead)
- ❌ Not reviewing the SRS before approving
- ❌ Skipping the architecture review

**Links**: `agent/01_entrypoints/run_new_project.md`

---

### `existing_project.txt`

**When to Use**: Working on an established codebase.

**Preconditions**:

- Existing code repository
- Specific task/objective in mind

**What It Does**:

1. Analyzes current codebase (stack detection, health check)
2. Routes to appropriate scenario based on your objective
3. Executes the task following Agent OS structure
4. Updates state to reflect changes

**Artifacts Produced**:

- `agent/09_state/PROJECT_STATE.md` (baseline)
- `agent/09_state/STACK_STATE.md` (detected stack)
- Scenario-specific outputs (varies by task)

**Success Looks Like**: The AI understands your codebase and completes the task using the appropriate workflow.

**Common Mistakes**:

- ❌ Not providing clear objective
- ❌ Expecting the AI to "figure out" what needs doing
- ❌ Not verifying the detected stack is correct

**Links**: `agent/01_entrypoints/run_existing_project.md`

---

### `srs_only.txt`

**When to Use**: Need documentation/planning without implementation.

**Preconditions**:

- Project idea or rough notes
- Stakeholder alignment needed

**What It Does**:

- Generates professional SRS document
- Creates user stories with acceptance criteria
- Defines non-functional requirements (performance, security)

**Artifacts Produced**:

- `plans/SRS/` (complete specification)

**Success Looks Like**: You have a document you can share with stakeholders or use for RFP/bidding.

**Links**: `agent/01_entrypoints/run_srs_only.md`

---

### `plan_only.txt`

**When to Use**: Have SRS, need technical roadmap.

**Preconditions**:

- Existing SRS in `plans/SRS/`

**What It Does**:

- Creates architecture diagrams
- Breaks project into milestones
- Generates detailed backlog

**Artifacts Produced**:

- `plans/Architecture/` (diagrams)
- `plans/Milestones/` (roadmap)
- `agent/09_state/BACKLOG_STATE.md`

**Success Looks Like**: You have a clear implementation path with estimated effort.

**Links**: `agent/01_entrypoints/run_plan_only.md`

---

### `implement_only.txt`

**When to Use**: Ready to code, have approved plan.

**Preconditions**:

- Approved SRS and architecture
- Populated backlog

**What It Does**:

- Picks tasks from backlog
- Implements with test-driven approach
- Enforces quality gates
- Updates state after each task

**Artifacts Produced**:

- Source code files
- Test files
- `plans/Features/` (implementation summaries)

**Success Looks Like**: Features are implemented, tested, and pass all quality gates.

**Common Mistakes**:

- ❌ Starting without approved SRS
- ❌ Skipping tests
- ❌ Not running the full test suite

**Links**: `agent/01_entrypoints/run_implement_only.md`

---

### `test_only.txt`

**When to Use**: Validate code quality without new features.

**Preconditions**:

- Existing codebase with tests

**What It Does**:

- Runs full test suite
- Generates coverage report
- Identifies edge cases
- Evaluates quality gate

**Artifacts Produced**:

- `plans/Tests/LATEST_RESULTS.md`
- `plans/Tests/COVERAGE_REPORT.md`

**Success Looks Like**: You know exactly what's tested, what's not, and where bugs might hide.

**Links**: `agent/01_entrypoints/run_test_only.md`

---

### `security_audit_only.txt`

**When to Use**: Security review before release or periodically.

**Preconditions**:

- Access to all code and dependencies

**What It Does**:

- Scans for leaked secrets
- Audits dependencies for CVEs
- Creates threat model
- Evaluates security gate

**Artifacts Produced**:

- `plans/Security/AUDIT_REPORT.md`
- `plans/Security/THREAT_MODEL.md`
- `plans/Security/VULNERABILITIES.md`

**Success Looks Like**: You have a clear security posture and remediation plan for any issues.

**High Risk Scenarios**: Always run this before production deployment.

**Links**: `agent/01_entrypoints/run_security_audit_only.md`

---

### `pr_review_only.txt`

**When to Use**: Review code changes before merging.

**Preconditions**:

- Diff or branch to review

**What It Does**:

- Checks code against project standards
- Applies quality rubrics
- Provides structured feedback

**Artifacts Produced**:

- `plans/Release/REVIEWS/PR_[ID]_REVIEW.md`

**Success Looks Like**: You get objective, consistent code review feedback.

**Links**: `agent/01_entrypoints/run_pr_review_only.md`

---

### `release_only.txt`

**When to Use**: Finalizing a version for production.

**Preconditions**:

- All features complete
- All tests passing

**What It Does**:

- Verifies ALL gates pass
- Generates release notes
- Creates version tag
- Updates CHANGELOG

**Artifacts Produced**:

- `plans/Release/RELEASE_NOTES_V[X.Y.Z].md`
- Git tag
- Updated CHANGELOG.md

**Success Looks Like**: You have a production-ready release with complete documentation.

**High Risk Scenarios**: This is the final checkpoint before users see your code.

**Links**: `agent/01_entrypoints/run_release_only.md`

---

## Scenario Prompts

### `bug_fix.txt`

**When to Use**: Fixing a confirmed software defect.

**Preconditions**: Bug report with reproduction steps.

**What It Does**: Diagnostic-first approach with reproduction test, surgical fix, regression verification.

**Artifacts**: Fixed code, new tests, bug report.

**Success**: Bug fixed, no regressions, prevention measures added.

**Links**: `agent/01_entrypoints/scenarios/scenario_bug_fix.md`

---

### `emergency_hotfix.txt`

**When to Use**: Critical production issue requiring immediate fix.

**Preconditions**: P0/P1 severity bug, production access.

**What It Does**: Rapid triage, minimal fix, staging verification, production deployment, post-mortem.

**Artifacts**: Hotfix branch, incident log, release notes.

**Success**: Production stable, issue resolved, root cause documented.

**High Risk**: This bypasses normal workflows for speed. Use only for genuine emergencies.

**Links**: `agent/01_entrypoints/scenarios/scenario_emergency_hotfix.md`

---

### `refactor.txt`

**When to Use**: Improving code structure without changing behavior.

**Preconditions**: High test coverage (≥90%) or willingness to write tests first.

**What It Does**: Baseline capture, atomic transformations, behavior verification.

**Artifacts**: Refactored code, refactor notes.

**Success**: Code is cleaner, all tests pass, no performance regression.

**Links**: `agent/01_entrypoints/scenarios/scenario_refactor.md`

---

### `dependency_update.txt`

**When to Use**: Upgrading libraries or responding to security alerts.

**Preconditions**: List of packages to update or CVE alert.

**What It Does**: Changelog review, impact mapping, migration, verification.

**Artifacts**: Updated package files, upgrade plan.

**Success**: Dependencies updated, no breaking changes, tests pass.

**Links**: `agent/01_entrypoints/scenarios/scenario_dependency_update.md`

---

### `performance_investigation.txt`

**When to Use**: Diagnosing slow response times or resource issues.

**Preconditions**: Performance complaint, access to profiling tools.

**What It Does**: Baseline measurement, profiling, optimization, verification.

**Artifacts**: Optimized code, performance notes, load test results.

**Success**: Performance meets SRS targets, no regressions.

**Links**: `agent/01_entrypoints/scenarios/scenario_performance_investigation.md`

---

### `data_migration.txt`

**When to Use**: Evolving database schemas.

**Preconditions**: Schema change proposal, database access.

**What It Does**: Migration planning, backup, execution, verification.

**Artifacts**: Migration scripts, migration plan, backup confirmation.

**Success**: Schema updated, data intact, rollback plan ready.

**High Risk**: Always test on staging first. Always have backups.

**Links**: `agent/01_entrypoints/scenarios/scenario_data_migration.md`

---

### `legacy_integration.txt`

**When to Use**: Working with old, undocumented code.

**Preconditions**: Legacy codebase, integration requirement.

**What It Does**: Code archaeology, characterization testing, strangler fig modernization.

**Artifacts**: Test harness, facade code, integration plan.

**Success**: Legacy code safely encapsulated or replaced.

**Links**: `agent/01_entrypoints/scenarios/scenario_legacy_integration.md`

---

### `flaky_test.txt`

**When to Use**: Tests that pass/fail randomly.

**Preconditions**: Flaky test name, CI logs.

**What It Does**: Pattern detection, root cause analysis, stabilization, stress testing.

**Artifacts**: Fixed tests, flaky test log.

**Success**: 100% pass rate over 1000 runs.

**Links**: `agent/01_entrypoints/scenarios/scenario_flaky_test.md`

---

### `circular_dependency.txt`

**When to Use**: Build errors from circular imports.

**Preconditions**: Build error logs.

**What It Does**: Dependency graphing, cycle breaking, prevention.

**Artifacts**: Refactored code, dependency diagram.

**Success**: All cycles resolved, CI check added.

**Links**: `agent/01_entrypoints/scenarios/scenario_circular_dependency.md`

---

### `api_failure.txt`

**When to Use**: Third-party API unavailable or rate-limited.

**Preconditions**: API error logs.

**What It Does**: Failure classification, mock creation, circuit breaker implementation.

**Artifacts**: Mock code, circuit breaker, dependency docs.

**Success**: App handles API failures gracefully.

**Links**: `agent/01_entrypoints/scenarios/scenario_api_failure.md`

---

### `conflict_resolution.txt`

**When to Use**: Contradictory requirements in SRS.

**Preconditions**: Conflicting requirements identified.

**What It Does**: Trade-off analysis, user escalation, decision capture.

**Artifacts**: Conflict analysis, updated SRS.

**Success**: Conflict resolved, SRS consistent.

**Links**: `agent/01_entrypoints/scenarios/scenario_conflict_resolution.md`

---

### `ambiguous_input.txt`

**When to Use**: User request is vague or incomplete.

**Preconditions**: Unclear user input.

**What It Does**: Structured questioning, assumption documentation, minimal implementation.

**Artifacts**: Clarification questions, assumptions doc.

**Success**: User confirms interpretation.

**Links**: `agent/01_entrypoints/scenarios/scenario_ambiguous_input.md`

---

### `multi_env_config.txt`

**When to Use**: Managing dev/staging/prod configurations.

**Preconditions**: Multiple deployment environments.

**What It Does**: Config strategy design, loader implementation, secret management.

**Artifacts**: Config loader, example files, access control docs.

**Success**: All environments configured, no secrets leaked.

**Links**: `agent/01_entrypoints/scenarios/scenario_multi_env_config.md`

---

## Common Mistakes

### 1. **Using the Wrong Prompt**

- ❌ Using `new_project.txt` on existing code
- ✅ Check `prompts/cheatsheets/prompt_selector.md` first

### 2. **Skipping State Files**

- ❌ Not checking `agent/09_state/` after execution
- ✅ Always verify state was updated correctly

### 3. **Ignoring Gate Failures**

- ❌ Proceeding when gates fail
- ✅ Fix issues before moving forward

### 4. **Not Providing Context**

- ❌ Pasting prompt with no additional info
- ✅ Include project description, current objective, relevant details

### 5. **Expecting Magic**

- ❌ Thinking AI will "figure it out"
- ✅ Be specific about what you want

---

## Advanced Usage

### Chaining Prompts

For complex projects, use prompts in sequence:

1. `new_project.txt` → Get SRS and plan
2. `implement_only.txt` → Build features
3. `test_only.txt` → Validate quality
4. `security_audit_only.txt` → Check security
5. `release_only.txt` → Finalize release

### Custom Scenarios

If your situation doesn't match any scenario:

1. Use `existing_project.txt` with detailed objective
2. The AI will route to `scenario_ambiguous_input.md`
3. Answer clarification questions
4. AI will create custom execution plan

### State Recovery

If the AI loses context:

1. Point it to `agent/09_state/PROJECT_STATE.md`
2. Use `agent/00_system/08_context_management.md`
3. The AI will rebuild context from state files

---

## Quick Reference

| Situation | Prompt File |
|---|---|
| Brand new project | `by_entrypoint/new_project.txt` |
| Add feature to existing code | `by_entrypoint/existing_project.txt` |
| Fix a bug | `by_scenario/bug_fix.txt` |
| Production emergency | `by_scenario/emergency_hotfix.txt` |
| Code is slow | `by_scenario/performance_investigation.txt` |
| Update dependencies | `by_scenario/dependency_update.txt` |
| Refactor messy code | `by_scenario/refactor.txt` |
| Database schema change | `by_scenario/data_migration.txt` |
| Tests are flaky | `by_scenario/flaky_test.txt` |
| Just need docs | `by_entrypoint/srs_only.txt` |
| Ready for release | `by_entrypoint/release_only.txt` |
