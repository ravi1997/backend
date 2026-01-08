# Web Build & Debug Workflow

**Purpose**: Diagnose and fix build failures in Web/Node.js projects.

## 1. Diagnose
1.  **Check Logs**: Look for `ModuleNotFound`, `SyntaxError`, or `WebpackError`.
2.  **Verify Node Version**: `node -v` vs `.nvmrc`.
3.  **Check Dependencies**:
    -   Are `node_modules` present?
    -   Run `npm install` (if safe).

## 2. Common Fixes
-   **Missing Module**: `npm install <package>` (Check safety matrix first).
-   **Version Mismatch**: `nvm use`.
-   **Cache Issues**: `rm -rf .next` or `rm -rf dist`.

## 3. Verify
-   Run `npm run build` locally.
-   Run `npm run dev` to smoke test.
