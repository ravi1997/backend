# Gate: Static Web Build

**Stack**: Static Web  
**Type**: Build Validation  
**Purpose**: Validate HTML/CSS/JS and optimize assets

---

## Checks

### 1. HTML Validation

- [ ] All `.html` files are valid HTML5
- [ ] No broken internal links
- [ ] All required meta tags present
- [ ] Proper DOCTYPE declaration
- [ ] Valid semantic structure

**Tool**: `html-validate` or W3C validator

### 2. CSS Validation

- [ ] All `.css` files are valid CSS3
- [ ] No syntax errors
- [ ] No unused selectors (optional)
- [ ] Proper vendor prefixes where needed

**Tool**: `stylelint` or W3C CSS validator

### 3. JavaScript Validation

- [ ] All `.js` files are valid JavaScript
- [ ] No syntax errors
- [ ] ES5/ES6 compatibility as required
- [ ] No console.log in production (warning)

**Tool**: `eslint` or `jshint`

### 4. Asset Optimization

- [ ] Images optimized (< 500KB per image recommended)
- [ ] CSS minified for production (optional)
- [ ] JS minified for production (optional)
- [ ] Gzip/Brotli compression enabled (server-side)

**Tool**: `imagemin`, `cssnano`, `terser`

### 5. File Structure

- [ ] `index.html` exists in root
- [ ] Assets organized (css/, js/, images/, fonts/)
- [ ] No broken file references
- [ ] Proper relative/absolute paths

---

## Commands

### HTML Validation

```bash
npx html-validate "**/*.html"
```

### CSS Validation

```bash
npx stylelint "**/*.css"
```

### JavaScript Validation

```bash
npx eslint "**/*.js"
```

### Link Checking

```bash
npx broken-link-checker http://localhost:8000
```

---

## Pass Criteria

✅ **PASS** if:

- All HTML/CSS/JS files are valid
- No critical errors
- All assets accessible

❌ **FAIL** if:

- Invalid HTML/CSS/JS syntax
- Broken links
- Missing critical assets

---

## Exceptions

- **Warnings allowed**: Minor CSS compatibility warnings
- **Warnings allowed**: console.log in development
- **Strict**: Invalid HTML/JS syntax always fails

---

## Related Files

- `gate_static_web.md` (master gate)
- `gate_static_web_style.md`
