# Detection: Existing vs New

## Purpose

Determines if the Agent is starting in a "Greenfield" or "Brownfield" scenario.

## Logic

- **NEW**:
  - Root directory has < 5 files.
  - No `src/` or `app/` folders.
  - No README or LICENSE.
- **EXISTING**:
  - Presence of significant code logic.
  - Git history present.
  - Presence of `plans/` or `agent/` (if re-connecting).

## Procedure

1. **Count**: Check file count in root.
2. **Structure**: Look for common "mature project" folders.
3. **History**: Run `git rev-parse --is-inside-work-tree`.
4. **Transition**: Trigger `run_new_project.md` or `run_existing_project.md`.

## Related Files

- `detect_project_type.md`
