# Next.js Framework Pack

## Detection

- **Files**: `next.config.js`, `next.config.mjs`, `next.config.ts`
- **Dependencies**: `next` in `package.json`

## Commands

### Development

- **Start Dev Server**: `npm run dev` (Default Port: 3000)
- **Lint**: `npm run lint`

### Build

- **Build Production**: `npm run build`
- **Output**: `.next/`

### Testing

- **Unit**: `npm run test` (usually Jest/Vitest)
- **E2E**: `npm run cypress` or `npm run playwright` (if configured)

## Key Files

- `app/` (App Router) or `pages/` (Pages Router)
- `public/` (Static assets)
- `next.config.js` (Configuration)

## Common Issues

- **Hydration Errors**: Mismatch between server-rendered HTML and client-side React.
- **Image Optimization**: Images not loading if domain not added to `images.domains` in config.
