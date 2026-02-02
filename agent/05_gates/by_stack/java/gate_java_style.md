# Java Gate: Style

## Purpose

Enforce Java coding standards.

## Rules

1. **Style Guide**: Google Java Style or Sun Checks.
2. **Linter**: Checkstyle or Spotless.
3. **Javadocs**: Public methods must have Javadoc.

## Check Command

```bash
mvn checkstyle:check
```

## Failure criteria

- Checkstyle errors > 0.
