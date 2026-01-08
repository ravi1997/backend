# Test Strategy Matrix

## Choose test type by change
### Pure logic change
- Unit tests (fast)
- Focus on edge cases

### Flask route change
- Flask test client request tests
- Validate status, payload shape, redirects
- Ensure PHI masking in logs if logging touched

### DB model/migration
- Integration tests with temporary DB
- Check migrations apply cleanly
- Add regression test for the bug if possible

### React UI change
- Component tests (Vitest)
- E2E optional (Playwright) for critical flows

## Minimum bar for incident fixes
- Repro steps recorded
- Regression test added (where feasible)
- Tests pass locally/CI

---

## Standard Test Report Format
Every feature implementation or fix must include a detailed test summary:

1.  **Iterative Verification Phase**: Summary of tests run after each small change.
2.  **App-Scoped Correctness**: Explicit confirmation that all errors in `@app` were identified and resolved.
3.  **Final Test Run**: Full suite execution results.
4.  **Evidence**: Logs, screenshots, or terminal output showing 100% pass rate.

**Rule**: No push allowed until the Standard Test Report is verified and `Gate 2` is passed.
