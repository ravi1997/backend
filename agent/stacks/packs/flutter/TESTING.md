# Flutter Testing Strategy

## Overview

Cross-platform UI testing including widget tests and golden files.

## Recommended Tools

| Type | Tool | Notes |
| :--- | :--- | :--- |
| **Unit/Widget** | `flutter test` | Built-in test runner. |
| **Integration** | `integration_test` | Built-in (runs on device/emulator). |
| **Golden Tests** | Golden Toolkit | Pixel-perfect UI regression testing. |
| **Linting** | `flutter analyze` | Dart analyzer. |

## QA Gates Profile

### 1. Analyze
- `flutter analyze` must return "No issues found!".
- `dart format --set-exit-if-changed .`

### 2. Tests
- **Blockers:** Widget tests failing.
- **Goldens:** Visual diffs must be reviewed manually if changed.

## Sample Command Pattern

```bash
# Run Unit & Widget Tests
flutter test

# Run Analyzer
flutter analyze

# Update Goldens (if intentional change)
flutter test --update-goldens
```

## Missing Emulator Strategy
If no emulator available for integration tests:
- Rely on Widget tests.
- Mark Integration gate as `[SKIPPED: NO EMULATOR]` in PR.
