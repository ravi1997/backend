# Gate: Static Web Tests

**Stack**: Static Web  
**Type**: Testing & Validation  
**Purpose**: Validate functionality and user experience

---

## Checks

### 1. Link Validation

- [ ] All internal links work (no 404s)
- [ ] All external links work (or gracefully handle failures)
- [ ] All anchor links (#) point to valid IDs
- [ ] No broken image/CSS/JS references

**Tool**: `broken-link-checker`, `linkinator`

### 2. Accessibility Testing

- [ ] All images have alt text
- [ ] Proper heading hierarchy (h1 → h2 → h3)
- [ ] Form labels associated with inputs
- [ ] Sufficient color contrast (WCAG AA minimum)
- [ ] Keyboard navigation works
- [ ] ARIA attributes used correctly

**Tool**: `axe-core`, `pa11y`, `lighthouse`

### 3. Cross-Browser Compatibility

- [ ] Works in Chrome/Edge (Chromium)
- [ ] Works in Firefox
- [ ] Works in Safari (if applicable)
- [ ] No browser-specific bugs
- [ ] Graceful degradation for older browsers

**Tool**: Manual testing or BrowserStack

### 4. Responsive Design

- [ ] Mobile viewport (320px - 480px)
- [ ] Tablet viewport (768px - 1024px)
- [ ] Desktop viewport (1280px+)
- [ ] No horizontal scroll on mobile
- [ ] Touch targets ≥ 44px × 44px

**Tool**: Browser DevTools, `lighthouse`

### 5. Performance

- [ ] Page load time < 3 seconds
- [ ] First Contentful Paint < 1.5 seconds
- [ ] Largest Contentful Paint < 2.5 seconds
- [ ] Cumulative Layout Shift < 0.1
- [ ] Total page size < 2MB

**Tool**: `lighthouse`, WebPageTest

### 6. JavaScript Functionality

- [ ] All interactive elements work
- [ ] Form validation works
- [ ] No JavaScript errors in console
- [ ] Works with JavaScript disabled (graceful degradation)

**Tool**: Manual testing, browser console

---

## Commands

### Link Checking

```bash
# Start local server first
npx http-server . -p 8000

# Check links
npx broken-link-checker http://localhost:8000 -ro
```

### Accessibility Audit

```bash
npx pa11y http://localhost:8000
```

### Lighthouse Audit

```bash
npx lighthouse http://localhost:8000 --output html --output-path ./lighthouse-report.html
```

### HTML Validation

```bash
npx html-validate "**/*.html"
```

---

## Lighthouse Score Requirements

| Category | Minimum Score |
|----------|---------------|
| Performance | 85 |
| Accessibility | 90 |
| Best Practices | 90 |
| SEO | 85 |

---

## Pass Criteria

✅ **PASS** if:

- All links work
- Accessibility score ≥ 90
- No critical JavaScript errors
- Responsive on all viewports
- Lighthouse scores meet minimums

❌ **FAIL** if:

- Broken links found
- Accessibility violations (WCAG A/AA)
- JavaScript errors present
- Not responsive
- Lighthouse scores below minimums

---

## Exceptions

- **External links**: May fail if third-party site is down (warning only)
- **Performance**: May vary by network conditions (use throttling)
- **Browser support**: Define minimum supported browsers in README

---

## Test Checklist

```markdown
## Static Web Test Checklist

### Links
- [ ] All internal links tested
- [ ] All external links tested
- [ ] All anchor links tested
- [ ] All resource links tested (images, CSS, JS)

### Accessibility
- [ ] Alt text on all images
- [ ] Heading hierarchy correct
- [ ] Form labels present
- [ ] Color contrast sufficient
- [ ] Keyboard navigation works
- [ ] Screen reader tested (optional)

### Responsive
- [ ] Mobile (320px) tested
- [ ] Tablet (768px) tested
- [ ] Desktop (1280px) tested
- [ ] No horizontal scroll

### Performance
- [ ] Lighthouse audit run
- [ ] Performance score ≥ 85
- [ ] Page load < 3s

### Functionality
- [ ] All interactive elements work
- [ ] Forms validate correctly
- [ ] No console errors
```

---

## Related Files

- `gate_static_web.md` (master gate)
- `gate_static_web_build.md`
- `gate_static_web_security.md`
