# FLOW: Autofix Loop (dev/staging)

> Production: blocked by policy.

## Loop
1) **Reproduce**
- Capture exact failure
- Write minimal repro notes

2) **Test-first**
- Add/adjust test to fail (when applicable)
- See `testing/TEST_STRATEGY.md`

3) **Patch**
- Smallest change that fixes root cause

4) **Verify**
- run: unit/integration tests
- run: lint/format
- run: security quick checks (if relevant)

5) **Commit**
- branch name: `fix/<incident-id>-<short>`
- commit message includes incident id
- produce `artifacts/PR_SUMMARY.md`

6) **Regression guard**
- keep the test that would catch recurrence

## Stop conditions
- Fix is risky without more evidence → return to evidence checklist
- Production → switch to `profiles/PROD_SAFE.md`
