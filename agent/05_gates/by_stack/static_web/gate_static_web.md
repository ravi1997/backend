# Gate: Static Web

**Stack**: Static Web (HTML/CSS/JS)  
**Type**: Master Gate  
**Purpose**: Ensure static web projects meet quality standards

---

## Overview

This gate validates static web projects (HTML, CSS, JavaScript) without build systems.

---

## Sub-Gates

This master gate requires passing:

1. **Build Gate** (`gate_static_web_build.md`) - Validation and asset optimization
2. **Style Gate** (`gate_static_web_style.md`) - HTML/CSS/JS linting and formatting
3. **Tests Gate** (`gate_static_web_tests.md`) - Link checking and validation
4. **Security Gate** (`gate_static_web_security.md`) - Security headers and best practices

---

## Pass Criteria

✅ **PASS** if:

- All sub-gates pass
- No critical issues found
- All files are valid HTML/CSS/JS

❌ **FAIL** if:

- Any sub-gate fails
- Critical security issues found
- Invalid HTML/CSS/JS syntax

---

## Enforcement

**Strict**: This gate MUST pass before:

- Deployment
- Release
- PR merge (if configured)

---

## Related Files

- `gate_static_web_build.md`
- `gate_static_web_style.md`
- `gate_static_web_tests.md`
- `gate_static_web_security.md`
