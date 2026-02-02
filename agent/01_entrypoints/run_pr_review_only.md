# Entrypoint: Run PR Review Only

## Purpose

Used to review a set of changes (diffs) against project standards.

## Inputs

- Diff of the changes or a branch name.

## Procedure

1. **Profile**: `profile_pr_reviewer.md`.
2. **Analysis**: Check for code style, logic errors, and security flaws.
3. **Checklist**: Run `agent/12_checks/checklists/pr_review_checklist.md`.
4. **Feedback**: Provide inline-style comments and a summary in `plans/Release/REVIEWS.md`.

## Related Files

- `agent/04_workflows/09_pr_review_loop.md`
