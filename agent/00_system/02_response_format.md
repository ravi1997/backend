# Response Format

## Purpose

Standardizes how the AI Agent communicates with the User and other AI models to ensure machine-readability and human clarity.

## Standard Output Structure

Every response from the Agent should follow this pattern:

1. **Active Profile**: "[Profile Name] active."
2. **Current Objective**: Brief summary of the current task.
3. **Token Safety Status** (if YELLOW or higher): Level, budget used, snapshot status (see `agent/00_system/12_token_budget_and_model_switching.md`).
4. **Execution Log**:
   - `[Action]` -> Result
   - `[Action]` -> Result
5. **State Update**: Any changes to `agent/09_state/`.
6. **Gates Status**: "Gate [Name]: [PASS/FAIL/PENDING]"
7. **Next Steps**: Bulleted list of what happens next.

## Markdown Guidelines

- **Code Blocks**: Always include the language (e.g., ` ```python `).
- **Paths**: Bold all file paths (e.g., **/home/user/project/file.py**).
- **Headings**: Use hierarchical headings (H1, H2, H3).
- **Links**: Use relative links for cross-referencing files within the `agent/` folder.

## Automation Markers

If a response requires user approval for a "Risky" command, it must be marked with:
`[APPROVAL_REQUIRED]: <Command to run>`

## Error Reporting

When an error occurs, use this format:

- **Error ID**: ERR-XXXX
- **Context**: What was happening.
- **Stack Trace/Log**: Snippet of the failure.
- **Remediation**: Steps to fix.

## Related Files

- `agent/00_system/04_error_handling.md`
- `agent/00_system/06_templates_index.md`
- `agent/00_system/12_token_budget_and_model_switching.md`
