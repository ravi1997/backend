# Vite Framework Pack

## Detection

- **Files**: `vite.config.js`, `vite.config.ts`
- **Dependencies**: `vite` in `package.json`

## Commands

### Development

- **Start Dev Server**: `npm run dev` (Default Port: 5173)
- **Preview Build**: `npm run preview`

### Build

- **Build Production**: `npm run build`
- **Output**: `dist/`

### Testing

- **Unit**: `npm run test` (usually Vitest)

## Key Files

- `index.html` (Entry point, usually in root)
- `src/main.tsx` or `src/main.js` (JS Entry)
- `vite.config.ts` (Configuration)

## Common Issues

- **Env Variables**: Must start with `VITE_` to be exposed to client.
- **CORS**: Proxy configuration needed in `vite.config.ts` for backend API calls during dev.
