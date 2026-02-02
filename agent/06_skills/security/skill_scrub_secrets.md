# Skill: Secret Scrubbing

## Purpose

Removing leacked credentials from git history.

## Procedure

1. Identify the leaked string.
2. Use `git filter-repo --replace-text <(echo "secret==>REMOVED")`.
3. Force push to the current branch (with user approval).
