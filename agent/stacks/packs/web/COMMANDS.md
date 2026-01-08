# Web Command Map

## Toolchain Selection
1. **PNPM**: If `pnpm-lock.yaml` exists.
2. **Yarn**: If `yarn.lock` exists.
3. **NPM**: Default fallback.

## Canonical Commands

### Build
**Vite/Next/Webpack**
```bash
npm run build
```

### Test
**Vitest/Jest**
```bash
npm run test
# OR
npm run test:unit
```

**End-to-End**
```bash
npm run test:e2e
# OR
npx playwright test
```

### Lint/Format
**ESLint & Prettier**
```bash
npm run lint
npm run format
```

### Run
**Dev Server**
```bash
npm run dev
# OR
npm start
```

### Package
**Docker**
```bash
docker build -t my-app .
```

### CI
**GitHub Actions (Example)**
```yaml
- uses: actions/setup-node@v3
  with:
    node-version: 18
    cache: 'npm'
- run: npm ci
- run: npm run lint
- run: npm test
- run: npm run build
```
