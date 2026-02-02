# Flutter Gate: Style

## Purpose

Enforce Dart linting rules.

## Rules

1. **Linter**: `flutter_lints` or `very_good_analysis` package.
2. **Formatting**: `dart format` must be applied.
3. **Warnings**: Zero warnings policy recommended.

## Check Command

```bash
dart format --output=none --set-exit-if-changed .
flutter analyze .
```

## Failure criteria

- Formatting required.
- Analyzer errors/warnings.
