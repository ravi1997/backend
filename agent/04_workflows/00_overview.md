# Workflows: Overview

## Purpose

This section defines the "Playbooks" for major SDLC phases. Each workflow acts as a standalone script for the Agent to follow.

## Workflow Index

1. `agent/04_workflows/01_intake_and_context_build.md`: First-time setup and understanding.
2. `agent/04_workflows/02_repo_audit_and_baseline.md`: Quality assessment of existing code.
3. `agent/04_workflows/03_srs_generation.md`: Requirements engineering.
4. `agent/04_workflows/04_architecture_and_design.md`: Technical blueprinting.
5. `agent/04_workflows/05_milestones_and_backlog.md`: Roadmap and task management.
6. `agent/04_workflows/06_feature_implementation_loop.md`: The dev "engine" (code/test/repeat).
7. `agent/04_workflows/07_testing_and_validation.md`: Deep quality checks.
8. `agent/04_workflows/08_security_review.md`: Vulnerability scanning.
9. `agent/04_workflows/09_pr_review_loop.md`: Collaborative code review.
10. `agent/04_workflows/10_release_process.md`: Final delivery.

## Global Workflow Rules

- Every workflow must start by identifying the current **State**.
- Every workflow must end by updating **State** and checking a **Gate**.
- If a step fails, go to `agent/00_system/04_error_handling.md`.
