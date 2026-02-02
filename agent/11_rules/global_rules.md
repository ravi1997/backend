# Global Rules

## 1. State Consistency

- Every change that alters the project's logic must be reflected in `agent/09_state/`.
- If a plan is approved, its status in the header must be updated to `APPROVED`.

## 2. Absolute Path Mastery

- All tool calls involving file paths MUST use absolute paths starting from the calculated project root.

## 3. Atomic File Edits

- Prefer surgical edits (via `replace_file_content`) over overwriting entire large files (via `write_to_file`).

## 4. No Hallucinations

- If a command fails, report the failure. Never "pretend" a command succeeded.
- If a dependency is missing, do not assume it can be installed; verify the package manager exists first.
