# Profile: Aggressive Auto-Fix (Staging/Dev Only)

Use when the user wants maximum automation.

Rules:
- You may propose multi-file refactors if they reduce recurring failures.
- Always run full test suite + lint + basic security scan.
- Always add at least one regression test for any bug fix.
- If tests are missing, create a minimal test harness.

Still blocked:
- production direct writes
- commands matching destructive patterns (unless user explicitly overrides AND backups exist)
