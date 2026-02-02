# Skill: Changelog Management

## Purpose

Automating the generation of release notes and commit summaries using Git history.

## Execution Procedure

1. **Log Retrieval**: `git log --oneline [last_tag]..HEAD`.
2. **Categorization**: Group by type (`feat`, `fix`, `chore`).
3. **Deduplication**: Merge similar commit messages.
4. **Sync**: Update the root `CHANGELOG.md`.

## Output Contract

- **Changelog Update**: Incremental update to the project log.
