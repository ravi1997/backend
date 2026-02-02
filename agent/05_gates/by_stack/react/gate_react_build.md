# React Gate: Build

## Purpose

Verify frontend bundle generation.

## Rules

1. **Tool**: Vite or CRA (Webpack).
2. **Environment**: `NODE_ENV=production` for build check.
3. **Assets**: Ensure images/fonts are linking correctly.

## Check Command

```bash
npm install
npm run build
```

## Failure criteria

- Build command failure.
- Bundle size limit exceeded (if configured).
