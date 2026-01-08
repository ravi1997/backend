# Subflow: Web Feature Delivery

**Stack:** Web (Node/TS/JS)
**Parent:** `../feature_delivery.md`

## Build & Test

```bash
# Install
npm install

# Build
npm run build

# Test
npm test
```

## Linting

```bash
# Format
npm run format

# Lint
npm run lint
```

## Missing Environment

If the environment cannot run tests (e.g. valid cross-compile toolchain missing):
1. **Reproduce:** Document setup in `REPRODUCE.md`.
2. **Minimal Test:** Create a script to run available tests.
3. **Confidence:** Downgrade confidence until verified on target.

## Role Checklist: Tester

**Reference:** `agent/stacks/packs/web/TESTING.md`

- [ ] **Lint:** `npm run lint` is clean.
- [ ] **Unit:** Vitest/Jest tests pass (100%).
- [ ] **E2E:** Playwright/Cypress smoke tests pass.
- [ ] **Build:** `npm run build` is warning-free.
