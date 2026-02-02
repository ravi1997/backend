# Skill: Issue Extraction & Prioritization

## Purpose

Transforming raw user feedback or automated error logs into actionable, structured backlog items.

## Input Contract

- **Source**: (e.g., GitHub Issue URL, Error Log Snippet, User Chat).

## Execution Procedure

1. **Decomposition**:
    - Identify the **Symptom** (What is broken?).
    - Identify the **Impact** (Who is affected?).
    - Identify the **Reproducibility** (Can we trigger it?).
2. **Deduplication**: Search `agent/09_state/BACKLOG_STATE.md` and `agent/14_known_issues/` for similar items.
3. **Prioritization**: Assign a MoSCoW level:
    - **Must**: Security flaw, system crash.
    - **Should**: Feature broken, performance regression.
    - **Could**: Typo, stylistic improvement.
4. **Backlog Creation**:
    - Use `agent/07_templates/feature/FEATURE_SPEC.md` if it's a new feature.
    - Create a task entry in `agent/09_state/BACKLOG_STATE.md`.

## Output Contract

- **Backlog Entry**: A new Task ID with clear acceptance criteria.
