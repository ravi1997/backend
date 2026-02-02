# Static Web Diagnostics Bundle

- Build and serve preview: `npm run build` (or equivalent) then `npx serve dist`.
- Asset check: devtools network waterfall; `find dist -type f -maxdepth 3 | head` to verify outputs.
- CSP/CORS: open console; `curl -I https://site/path` to inspect headers; attempt preflight with `curl -X OPTIONS -H "Origin: https://example.com" ...`.
- Lighthouse/Axe: run `npx lighthouse http://localhost:3000 --quiet` or `npx axe http://localhost:3000` (if available).
- Bundle analysis: `npx source-map-explorer dist/*.js` or `webpack-bundle-analyzer` if configured.
- Accessibility: tab through UI; check `<meta name="viewport">`, alt text, labels; run `npx playwright test --project=webkit` if configured.
- Service workers: devtools Application tab; unregister/clear caches to test updates.
