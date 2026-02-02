# Detection: Project Type

## Purpose

Categorizes the project into a high-level bucket to determine which workflows apply.

## Inputs

- Repository file list (`ls -R`).

## Categories

- **WEB_APP**: Presence of index.html, JS frameworks, or CSS.
- **API_SERVICE**: Presence of routing files, HTTP methods, and no frontend.
- **LIBRARY_PACKAGE**: Presence of package metadata (setup.py, package.json) and exported modules.
- **CLI_TOOL**: Presence of argument parsing logic (argparse, clap, commander).
- **MOBILE_APP**: Presence of `android/`, `ios/`, or `flutter/` directories.
- **EMBEDDED**: Presence of C/C++ files and hardware HAL references.

## Procedure

1. **Scan**: Perform a non-recursive scan of the root.
2. **Weight**: Assign scores to each category based on files found.
3. **Decide**: Choose the category with the highest score.
4. **Log**: Update `agent/09_state/PROJECT_STATE.md`.

## STOP Condition

- If multiple categories have equal high scores, ask the User for clarification.

## Related Files

- `detect_stack_signals.md`
