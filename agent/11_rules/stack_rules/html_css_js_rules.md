# Rules: HTML, CSS & Client-Side JavaScript

**Stack**: Static Web / Vanilla JS  
**Linting**: HTMLHint, Stylelint, ESLint

---

## 1. HTML Guidelines

- **Semantic HTML**: Use correct tags (`<nav>`, `<main>`, `<article>`, `<button>`) for accessibility.
- **Attributes**: Always Quote attributes.
- **Alt Text**: All `<img>` tags MUST have `alt` attributes.
- **Doctype**: always `<!DOCTYPE html>` at the top.
- **Separation**: No inline styles or inline event handlers (`onclick="..."`) in HTML.

## 2. CSS Guidelines

- **Methodology**: Use BEM (Block Element Modifier) or a consistent naming convention.
- **Specificity**: Avoid IDs for styling. Keep specificity low.
- **Variables**: Use CSS Variables (`--main-color`) for design tokens.
- **Reset/Normalize**: Always use a reset or normalize stylesheet.
- **Responsive**: Mobile-first media queries (`min-width`) preferred.

## 3. JavaScript Guidelines (Browser)

- **Modern JS**: Use ES6+ features (`const/let`, Arrow functions, Modules).
- **DOM Manipulation**: Cache DOM queries or use `document.querySelector`.
- **Global Scope**: Avoid polluting the global window object. Use modules or IIFE.
- **Asynchronous**: Prefer `async/await` and `fetch` APIs.
- **Strict Mode**: `'use strict';` (implied in modules, required in scripts).

## 4. Security

- **XSS**: Do NOT use `innerHTML` with user-supplied content. Use `textContent` or `innerText`.
- **CSP**: Content Security Policy should be used to restrict script sources.
- **Inputs**: Validate all form inputs before processing.

## 5. Accessibility (a11y)

- **Keyboard**: Interactive elements must be keyboard focusable and usable.
- **Code Order**: Visual order should match DOM order for screen readers.
- **Contrast**: Text/Background contrast must meet WCAG AA.

---

## Enforcement Checklist

- [ ] HTML validated (W3C or HTMLHint)
- [ ] No inline styles/scripts
- [ ] CSS uses variables
- [ ] JS uses const/let (no var)
- [ ] No innerHTML unsafe usage
- [ ] Accessibility checks pass
