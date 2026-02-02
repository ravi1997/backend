# Skill: Git Hygiene & Conventional Commits

## Purpose

Enforce clean Git history and standardized commit messaging for readability and automation compatibility.

## Input Contract

- **Changeset**: Modified files.
- **Task ID**: e.g., `T-001`.

## Execution Procedure

1. **Staging**: `git add` only the files relevant to the current atomic task.
2. **Linting**: Run `git diff --cached` and scan for debug logs or secrets using `agent/06_skills/security/skill_scrub_secrets.md`.
3. **Message Composition**:
    - Format: `<type>(<scope>): <subject>`
    - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
    - Body: Include "Resolves: #TaskID".
4. **Verification**: Ensure no merge conflicts exist with the target branch.

## Failure Modes

- **Generic Message**: Refuse to commit if message is "fix" or "update".
- **Large Commits**: If `git diff` exceeds 500 lines, recommend splitting the commit.

## Output Contract

- **Commit Signature**: A clean Git commit with a standardized message.
