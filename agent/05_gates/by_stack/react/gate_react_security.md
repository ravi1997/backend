# React Gate: Security

## Purpose

Frontend security best practices.

## Rules

1. **Dependencies**: `npm audit`.
2. **XSS**: No `dangerouslySetInnerHTML` without explicit justification.
3. **Deps**: Avoid abandonware packages.

## Check Command

```bash
npm audit
grep -r "dangerouslySetInnerHTML" src/ || true
```

## Failure criteria

- Critical vulnerabilities.
- Unjustified XSS risks.
