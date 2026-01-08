# Web Testing Strategy

## Overview

Frontend/Backend JS/TS testing covering components and E2E flows.

## Recommended Tools

| Type | Tool | Notes |
| :--- | :--- | :--- |
| **Unit** | Vitest / Jest | Vitest preferred for Vite apps. |
| **Component** | Testing Library | React/Vue Testing Library. |
| **E2E** | Playwright / Cypress | Browser automation. |
| **Linting** | ESLint / Prettier | Standard. |

## QA Gates Profile

### 1. Lint & Check
- `npm run lint` (ESLint).
- `tsc --noEmit` (Type check for TypeScript).

### 2. Unit Tests
- `npm run test` (Vitest/Jest).
- Requirement: 100% pass.

### 3. E2E Tests
- `npx playwright test`
- **Dev-Loop:** Run smoke tests.
- **CI:** Run full suite (headless).

## Sample Command Pattern

```bash
# Type Check
tsc --noEmit

# Unit Tests
npm run test:unit

# E2E Tests (Headless)
npx playwright test
```
