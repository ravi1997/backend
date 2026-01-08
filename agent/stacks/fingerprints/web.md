# Web (Node/JS/TS) Project Fingerprint

## Signatures

| File / Pattern | Type | Confidence | Notes |
| :--- | :--- | :--- | :--- |
| `package.json` | Config | 1.0 | Node.js / Web project root |
| `pnpm-lock.yaml` | Lockfile | 1.0 | pnpm package manager |
| `yarn.lock` | Lockfile | 1.0 | Yarn package manager |
| `package-lock.json` | Lockfile | 1.0 | npm package manager |
| `bun.lockb` | Lockfile | 1.0 | Bun package manager |
| `vite.config.*` | Config | 0.9 | Vite bundler |
| `next.config.*` | Config | 0.9 | Next.js framework |
| `tsconfig.json` | Config | 0.8 | TypeScript project |
| `webpack.config.*` | Config | 0.8 | Webpack bundler |
| `*.js`, `*.ts`, `*.jsx`, `*.tsx`| Source Code | 0.2 | Source files (very common, weak signal on its own) |

## Related Tools

-   **Package Managers**: `npm`, `yarn`, `pnpm`, `bun`
-   **Build**: `npm run build`, `yarn build`, `pnpm build`
-   **Run/Dev**: `npm run dev`, `npm start`
-   **Test**: `jest`, `vitest`, `mocha`, `cypress`, `playwright`
