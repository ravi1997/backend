# Gate: Static Web Style

**Stack**: Static Web  
**Type**: Code Style & Formatting  
**Purpose**: Enforce consistent HTML/CSS/JS formatting and best practices

---

## Checks

### 1. HTML Style

- [ ] Consistent indentation (2 or 4 spaces)
- [ ] Lowercase tag names and attributes
- [ ] Proper attribute quoting (double quotes)
- [ ] Self-closing tags for void elements
- [ ] Semantic HTML5 elements used appropriately
- [ ] Accessibility attributes (alt, aria-*, role)

**Tool**: `prettier` with HTML plugin or `html-validate`

### 2. CSS Style

- [ ] Consistent indentation
- [ ] Alphabetical property ordering (optional)
- [ ] No duplicate selectors
- [ ] BEM or consistent naming convention
- [ ] No !important overuse
- [ ] Mobile-first media queries

**Tool**: `stylelint` with standard config

### 3. JavaScript Style

- [ ] Consistent indentation (2 or 4 spaces)
- [ ] Semicolons (consistent usage)
- [ ] Single or double quotes (consistent)
- [ ] camelCase for variables and functions
- [ ] PascalCase for constructors/classes
- [ ] No unused variables
- [ ] Proper error handling

**Tool**: `eslint` with standard config or `prettier`

### 4. File Naming

- [ ] Lowercase filenames with hyphens (kebab-case)
- [ ] Descriptive names (no `file1.html`, `style2.css`)
- [ ] Consistent extensions (.html, .css, .js)

### 5. Comments

- [ ] HTML comments for major sections
- [ ] CSS comments for complex rules
- [ ] JSDoc comments for functions (optional)
- [ ] No commented-out code in production

---

## Commands

### Format HTML/CSS/JS

```bash
npx prettier --write "**/*.{html,css,js}"
```

### Lint HTML

```bash
npx html-validate "**/*.html"
```

### Lint CSS

```bash
npx stylelint "**/*.css" --fix
```

### Lint JavaScript

```bash
npx eslint "**/*.js" --fix
```

---

## Configuration Files

### `.prettierrc`

```json
{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "htmlWhitespaceSensitivity": "css"
}
```

### `.stylelintrc.json`

```json
{
  "extends": "stylelint-config-standard",
  "rules": {
    "indentation": 2,
    "color-hex-case": "lower",
    "color-hex-length": "short"
  }
}
```

### `.eslintrc.json`

```json
{
  "extends": "eslint:recommended",
  "env": {
    "browser": true,
    "es6": true
  },
  "parserOptions": {
    "ecmaVersion": 2020,
    "sourceType": "module"
  },
  "rules": {
    "indent": ["error", 2],
    "quotes": ["error", "single"],
    "semi": ["error", "always"]
  }
}
```

---

## Pass Criteria

✅ **PASS** if:

- All files formatted consistently
- No style violations
- Linters pass with 0 errors

❌ **FAIL** if:

- Inconsistent formatting
- Style violations present
- Linters report errors

---

## Exceptions

- **Warnings allowed**: Minor style preferences
- **Auto-fix**: Most style issues can be auto-fixed
- **Strict**: Accessibility violations always fail

---

## Related Files

- `gate_static_web.md` (master gate)
- `gate_static_web_build.md`
