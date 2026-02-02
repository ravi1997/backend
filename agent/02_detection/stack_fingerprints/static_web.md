# Stack Fingerprint: Static Web

## Purpose

Identifies and configures for a plain HTML/CSS/JS project.

## Signals

- `index.html`.
- No `package.json` or build system.
- Browser-compatible JS.

## Configuration

- **Server**: Static file server (e.g. `python -m http.server`).
- **Tests**: Manual browser checks or Playwright.
