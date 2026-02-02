# Node Gate: Build

## Purpose

Ensure server-side JS/TS compiles.

## Rules

1. **Transpilation**: If TS, `tsc` must pass.
2. **Dependencies**: `package-lock.json` must exist and match `package.json`.
3. **Scripts**: `npm run build` must be defined if build step exists.

## Check Command

```bash
npm install
npm run build --if-present
```

## Failure criteria

- Build script failure.
- TypeScript compiler errors.
