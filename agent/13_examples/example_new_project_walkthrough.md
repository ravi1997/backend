# Example: New Project Walkthrough

## Scenario

The User wants a high-performance "Real-Time Weather CLI" in Python that fetches data from an API and caches it locally.

## Step 1: Bootstrap & Intake

- **User Prompt**: "Build a weather CLI in Python. Use OpenWeatherMap API. Cache results for 10 minutes."
- **Agent Action**:
  - Executes `agent/04_workflows/01_intake_and_context_build.md`.
  - Detects: `Stack: Python`, `Type: New Project`.
  - Initializes `agent/09_state/PROJECT_STATE.md` with status `BOOTSTRAP`.

## Step 2: Requirements & Architecture

- **Agent Action**:
  - Switches to `agent/03_profiles/profile_analyst_srs.md`.
  - Generates `agent/07_templates/srs/SRS_INDEX.md` and related spec files.
  - Defines **Non-Functional Requirements**: "Latecy < 200ms", "Zero-leakage of API keys".
  - Switches to `agent/03_profiles/profile_architect.md`.
  - Generates `plans/Architecture/OVERVIEW.mermaid.md` (CLI -> Cache -> API).

## Step 3: Planning

- **Agent Action**:
  - Executes `agent/04_workflows/05_milestones_and_backlog.md`.
  - Sets Milestones: `M1: API Client`, `M2: Cache implementation`, `M3: CLI Interface`.
  - Populates `agent/09_state/BACKLOG_STATE.md` with T-001 to T-005.

## Step 4: Implementation Loop (M1)

- **Agent Action**:
  - Executes `agent/04_workflows/06_feature_implementation_loop.md` for `T-001: API Connection`.
  - Generates `agent/07_templates/feature/FEATURE_SPEC.md`.
  - Runs `agent/05_gates/by_stack/python/gate_python.md` (Black, Flake8).
  - Writes `tests/test_api.py`.
  - **Self-Correction**: If the API call fails, the agent reads the log, identifies the missing `requests` package, updates `requirements.txt`, and tries again.

## Step 5: Security & Quality Gate

- **Agent Action**:
  - Executes `agent/04_workflows/08_security_review.md`.
  - Runs `agent/06_skills/security/skill_scrub_secrets.md` to ensure OpenWeather key isn't in Git history.
  - Verifies `agent/05_gates/global/gate_global_quality.md`.

## Step 6: Release

- **Agent Action**:
  - Executes `agent/04_workflows/10_release_process.md`.
  - Generates `agent/07_templates/release/RELEASE_NOTES.md`.
  - Tags repository with `v1.0.0` using `agent/06_skills/devops/skill_release_tagging.md`.

## Result

A fully functional, versioned, and security-hardened repository with 100% traceabilty between code and requirements.
