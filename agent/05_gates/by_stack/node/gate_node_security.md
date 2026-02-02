# Node Gate: Security

## Purpose

Vulnerability scanning for Node packages.

## Rules

1. **Audit**: `npm audit` (or `pnpm audit` / `yarn audit`).
2. **Secrets**: No `.env` files committed.
3. **Sanitization**: Input validation (e.g., `joi`, `zod`) for API endpoints.

## Check Command

```bash
npm audit --production
```

## Failure criteria

- High/Critical vulnerabilities found.
