# Web Troubleshooting

## Common Issues

### Node Version Mismatch
- **Symptom**: Weird build errors or "engine not supported".
- **Fix**: Use `nvm use` or check `.nvmrc`.

### Hydration Mismatch (SSR)
- **Symptom**: "Text content does not match server-rendered HTML".
- **Fix**: Ensure deterministic rendering (no random numbers/dates on initial render). Use `useEffect` for client-only logic.

### CORS Errors
- **Symptom**: API requests blocked by browser.
- **Fix**: Configure proxy in `vite.config.ts` or `package.json` for dev. Fix server headers for prod.

### Module Not Found
- **Symptom**: `Cannot find module ...`
- **Fix**: Check `tsconfig.json` paths mapping vs standard imports.
