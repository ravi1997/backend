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
