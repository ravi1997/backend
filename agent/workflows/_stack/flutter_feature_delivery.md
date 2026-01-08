# Subflow: Flutter Feature Delivery

**Stack:** Flutter
**Parent:** `../feature_delivery.md`

## Build & Test

```bash
# Get dependencies
flutter pub get

# Generate code (if needed)
flutter pub run build_runner build --delete-conflicting-outputs

# Test
flutter test
```

## Linting

```bash
# Analyze
flutter analyze

# Format
dart format .
```

## Missing Environment

If the environment cannot run tests (e.g. valid cross-compile toolchain missing):
1. **Reproduce:** Document setup in `REPRODUCE.md`.
2. **Minimal Test:** Create a script to run available tests.
3. **Confidence:** Downgrade confidence until verified on target.

## Role Checklist: Tester

**Reference:** `agent/stacks/packs/flutter/TESTING.md`

- [ ] **Analyze:** `flutter analyze` is clean.
- [ ] **Tests:** Widget/Unit tests pass.
- [ ] **Integration:** Device tests pass (or skipped with reason).
- [ ] **Goldens:** UI matches baseline.
