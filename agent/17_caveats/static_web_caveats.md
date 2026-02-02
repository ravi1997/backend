# Static Web Caveats & Footguns

Issue-Key example: `Issue-Key: STATICWEB-4ab7c2`.

- Relative paths break on nested routes; prefer root-relative URLs or set `<base href>` explicitly.
- Case-sensitive filesystems in production catch casing errors—CI on Linux is mandatory.
- Service workers can serve stale assets; version caches and provide refresh prompts.
- CSP must be explicit; avoid `unsafe-inline` and wildcards, use nonces/hashes.
- Avoid `innerHTML` with untrusted data; sanitize or use textContent.
- Performance budgets should be enforced (bundle size, TTI, image weight); automate Lighthouse checks.
- Accessibility cannot be deferred: alt text, labels, focus order, contrast, and keyboard support are required.
- Cross-browser support must be tested; Safari/WebKit differs on newer APIs—feature-detect and polyfill accordingly.
- Cache-control headers need hashed filenames; avoid long caching for HTML documents.
