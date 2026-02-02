# Static Web Accessibility Checklist (Add-On)

- Provide alt text for all images/icons; label form controls and associate with inputs (for/id or aria-label/aria-labelledby).
- Ensure focus order and keyboard navigation work; visible focus styles present; no keyboard traps.
- Color contrast meets WCAG AA; verify via automated check; avoid text on busy backgrounds without overlay.
- Include `<meta name="viewport" content="width=device-width, initial-scale=1">`; layouts responsive on mobile.
- Use semantic elements (button, nav, main, header, footer); avoid div/span for interactive controls.
- Provide ARIA roles/states only when necessary and valid; avoid aria-hidden on focusable elements.
- Announce form validation errors inline with aria-describedby; do not rely on color alone.
- Run axe/Lighthouse a11y audits in CI; fix all severe/critical findings before release.
