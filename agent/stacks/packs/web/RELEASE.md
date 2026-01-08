# Web Release & Packaging

## Deployment Targets
- **Static Hosting**: Vercel, Netlify, GitHub Pages, S3+CloudFront.
- **Docker/Container**: For SSR apps (Next.js, Remix).
- **Node Server**: PM2, Systemd.

## Release Checklist
- [ ] Run full build `npm run build`.
- [ ] Check bundle size (source-map-explorer).
- [ ] Bump version in `package.json`.
- [ ] Create git tag.

## Command Example
```bash
# Analyze bundle
npx source-map-explorer build/static/js/*.js
```
