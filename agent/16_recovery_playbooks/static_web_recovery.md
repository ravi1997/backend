# Static Web Recovery Playbook

Issue-Key `Issue-Key: STATICWEB-<hash>`. Map to HC-STATICWEB-XXX.

## RECOVERY-STATICWEB-001: Asset/Path Issues
- Verify `<base href>` and asset paths; fix casing; rebuild with hashed filenames; clear service worker caches (`navigator.serviceWorker.getRegistrations()` remove).
- Validate via local `npx serve dist` and devtools network (200 for assets).

## RECOVERY-STATICWEB-002: Security/CORS/CSP
- Check console for CSP/CORS/mixed content errors; adjust CSP to allow required hosts with nonces/hashes; enforce HTTPS URLs.
- Configure API CORS server-side; for static proxies, align origins and credentials settings.
- Validate with curl/preflight tests; rerun page load to ensure no CSP/CORS errors.

## RECOVERY-STATICWEB-003: Performance Problems
- Run Lighthouse; analyze bundle with source-map-explorer; enable code splitting, image compression, caching headers.
- Defer/async scripts; inline critical CSS; reduce DOM weight.
- Validate improved scores/perf budgets.

## RECOVERY-STATICWEB-004: Accessibility Failures
- Run axe/Lighthouse a11y; add alt/labels, contrast fixes, keyboard support, aria roles.
- Validate with automated checks and manual keyboard navigation.

## RECOVERY-STATICWEB-005: JS Runtime Errors
- Inspect console stack; ensure correct script order and polyfills; add error handling for async.
- Validate by reloading in target browsers (Chrome/WebKit/Firefox) and running smoke tests.
