# Static Web (HTML/CSS/JS) Hard Cases & Failure Scenarios

Issue-Key example: `Issue-Key: STATICWEB-8c1f2a`. Prompt: `prompts/hard_cases/static_web_hard_cases.txt`.

## Assets & Paths

### HC-STATICWEB-001: Broken Relative Paths
**Symptom:** images/CSS/JS 404 after deploy.
**Likely Causes:** wrong base href; nested routes using relative links.
**Fast Diagnosis:** open devtools network; check `<base>` tag.
**Fix Steps:** use absolute paths or set correct `<base href>`; adjust bundler output paths.
**Prevention:** deploy preview to verify asset paths; tests with `npm run build && npx serve`.

### HC-STATICWEB-002: Case-Sensitive Paths
**Symptom:** assets load locally (mac) but 404 on Linux.
**Likely Causes:** filename case mismatch.
**Fast Diagnosis:** `find public -type f | sort`; compare href/src casing.
**Fix Steps:** fix filenames/refs to consistent case.
**Prevention:** CI on case-sensitive FS; lint for case mismatches.

### HC-STATICWEB-003: Bundler Output Not Updated
**Symptom:** old JS served.
**Likely Causes:** caching, not running build.
**Fast Diagnosis:** check build timestamps; cache-control headers.
**Fix Steps:** rebuild; bust cache with hashes; set cache headers.
**Prevention:** hashed filenames; CI builds before deploy.

### HC-STATICWEB-004: Source Maps Missing/Exposed
**Symptom:** cannot debug or leaking source.
**Likely Causes:** sourceMap disabled or published in prod unintentionally.
**Fast Diagnosis:** check build config; devtools for source maps.
**Fix Steps:** enable maps for staging only; remove from prod if sensitive.
**Prevention:** environment-specific build flags.

## Security & Networking

### HC-STATICWEB-005: CSP Blocking Scripts
**Symptom:**
```
Refused to load the script because it violates the Content Security Policy
```
**Likely Causes:** CSP missing host or unsafe inline.
**Fast Diagnosis:** check console errors; view Response Headers CSP.
**Fix Steps:** adjust CSP to allow required origins; use nonces/hashes; remove inline JS.
**Prevention:** CSP test cases; use strict CSP templates.

### HC-STATICWEB-006: XSS Injection Points
**Symptom:** unsanitized user input reflected.
**Likely Causes:** innerHTML usage with untrusted data.
**Fast Diagnosis:** search for `innerHTML =` / `dangerouslySetInnerHTML` (if static React exports).
**Fix Steps:** escape/encode user input; avoid inline HTML injection; use DOMPurify when needed.
**Prevention:** lint for innerHTML; security review.

### HC-STATICWEB-007: Mixed Content
**Symptom:** blocked HTTP assets on HTTPS site.
**Likely Causes:** http links.
**Fast Diagnosis:** devtools security tab.
**Fix Steps:** update to https; use protocol-relative or secure CDN.
**Prevention:** content scan for http://; CSP upgrade-insecure-requests.

### HC-STATICWEB-008: CORS Failures for API Calls
**Symptom:**
```
Access to fetch at ... from origin ... has been blocked by CORS policy
```
**Likely Causes:** API lacks CORS headers or using wrong origin.
**Fast Diagnosis:** inspect response headers.
**Fix Steps:** configure API CORS; use proxy; preflight handling.
**Prevention:** contract with backend; test preflight via curl.

### HC-STATICWEB-009: Service Worker Stale Cache
**Symptom:** clients stuck on old assets.
**Likely Causes:** SW cache not busted; skipWaiting not called.
**Fast Diagnosis:** devtools Application > Service Workers; check SW version.
**Fix Steps:** update cache keys; call `skipWaiting`/`clients.claim`; prompt refresh.
**Prevention:** versioned caches; SW tests during deploy.

### HC-STATICWEB-010: CORS with Credentials Misused
**Symptom:** cookies not sent or blocked.
**Likely Causes:** missing `credentials: 'include'` or server not allowing credentials.
**Fast Diagnosis:** check fetch options; response headers.
**Fix Steps:** set `credentials: 'include'`; server must set `Access-Control-Allow-Credentials: true` and non-wildcard origin.
**Prevention:** CORS policy docs; tests from browser automation.

## Performance

### HC-STATICWEB-011: Large Bundles
**Symptom:** slow load, high TTI.
**Likely Causes:** bundling everything, no code splitting.
**Fast Diagnosis:** Lighthouse bundle size; `source-map-explorer`.
**Fix Steps:** code split; tree shake; remove unused polyfills.
**Prevention:** performance budget in CI; bundle analyzer reports.

### HC-STATICWEB-012: Unoptimized Images
**Symptom:** heavy image loads.
**Likely Causes:** raw PNG/JPEG uncompressed.
**Fast Diagnosis:** inspect image sizes; Lighthouse.
**Fix Steps:** compress images; use webp/avif; responsive sizes.
**Prevention:** image optimization pipeline; lint on PR.

### HC-STATICWEB-013: No Caching Headers
**Symptom:** repeated downloads.
**Likely Causes:** cache-control missing.
**Fast Diagnosis:** inspect response headers.
**Fix Steps:** add Cache-Control/ETag; use hashed filenames.
**Prevention:** CDN config templates; CI check for cache headers in preview.

### HC-STATICWEB-014: Render-Blocking Resources
**Symptom:** slow first paint.
**Likely Causes:** sync scripts/styles.
**Fast Diagnosis:** Lighthouse/Devtools coverage.
**Fix Steps:** defer/async scripts; preload critical CSS; inline minimal critical CSS.
**Prevention:** performance budgets; use HTTP/2 push cautiously.

### HC-STATICWEB-015: Excessive DOM Size
**Symptom:** slow interactions.
**Likely Causes:** huge DOM tree.
**Fast Diagnosis:** performance profile; devtools DOM size warnings.
**Fix Steps:** simplify layout; paginate; virtualize lists.
**Prevention:** design review for DOM weight; automated Lighthouse thresholds.

## Accessibility

### HC-STATICWEB-016: Missing Alt/Text Labels
**Symptom:** accessibility audit fails.
**Likely Causes:** images without alt, inputs without labels.
**Fast Diagnosis:** axe/Lighthouse; inspect DOM.
**Fix Steps:** add alt text; associate labels; use aria-label where needed.
**Prevention:** run axe in CI; a11y checklist.

### HC-STATICWEB-017: Poor Color Contrast
**Symptom:** low contrast warnings.
**Likely Causes:** design colors not meeting WCAG.
**Fast Diagnosis:** devtools contrast checker.
**Fix Steps:** adjust colors to meet WCAG AA; add focus outlines.
**Prevention:** design tokens with contrast; automated contrast tests.

### HC-STATICWEB-018: Keyboard Navigation Broken
**Symptom:** cannot tab through UI.
**Likely Causes:** tabindex misuse; custom controls without focus handlers.
**Fast Diagnosis:** keyboard test; devtools accessibility tree.
**Fix Steps:** correct tabindex; add focus styles and key handlers; use semantic elements.
**Prevention:** keyboard-only test in CI via playwright/axe.

### HC-STATICWEB-019: Missing ARIA Roles
**Symptom:** screen readers misinterpret controls.
**Likely Causes:** divs used as buttons.
**Fast Diagnosis:** accessibility tree inspection.
**Fix Steps:** use button/input elements; add appropriate roles/states.
**Prevention:** lint rules for interactive elements; a11y tests.

### HC-STATICWEB-020: Form Validation Without Feedback
**Symptom:** users cannot submit; no errors shown.
**Likely Causes:** missing inline errors.
**Fast Diagnosis:** manual form test.
**Fix Steps:** show inline error messages; aria-describedby linking.
**Prevention:** form UX checklist; tests for validation messages.

## JS Runtime

### HC-STATICWEB-021: Undefined is Not a Function
**Symptom:** runtime JS errors.
**Likely Causes:** wrong script order; missing polyfills.
**Fast Diagnosis:** console stack trace; check bundler output.
**Fix Steps:** ensure dependencies loaded first; add polyfills; bundle modules properly.
**Prevention:** module bundling with dependency graph; ESM preferred.

### HC-STATICWEB-022: Async Errors Swallowed
**Symptom:** silent failures in fetch promises.
**Likely Causes:** missing catch/logging.
**Fast Diagnosis:** look for unhandled promise rejection; enable `window.onunhandledrejection` logging.
**Fix Steps:** add error handling; use async/await with try/catch; surface errors to UI.
**Prevention:** lint for floating promises; add logging hooks.

### HC-STATICWEB-023: Deprecated APIs in Old Browsers
**Symptom:** site fails on Safari/IE11-like envs.
**Likely Causes:** using modern APIs without polyfills.
**Fast Diagnosis:** test with BrowserStack or `npx playwright test --project=webkit`.
**Fix Steps:** transpile/polyfill; feature detection.
**Prevention:** browser support matrix documented; automated cross-browser tests.

### HC-STATICWEB-024: CSS Specificity Wars
**Symptom:** styles not applied as expected.
**Likely Causes:** !important sprawl; conflicting selectors.
**Fast Diagnosis:** devtools computed styles to see specificity.
**Fix Steps:** reduce specificity; use BEM/utility classes; remove !important.
**Prevention:** stylelint rules; design tokens.

### HC-STATICWEB-025: Mobile Responsiveness Issues
**Symptom:** layout broken on mobile.
**Likely Causes:** missing viewport meta; fixed widths.
**Fast Diagnosis:** device emulation; check viewport tag.
**Fix Steps:** add `<meta name="viewport" content="width=device-width, initial-scale=1">`; use flexible layouts/media queries.
**Prevention:** responsive design checklist; run Lighthouse mobile.

## Issue-Key and Prompt Mapping
- Example Issue-Key: `Issue-Key: STATICWEB-f0d123`
- Use prompt: `prompts/hard_cases/static_web_hard_cases.txt`
