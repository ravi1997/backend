# WORKFLOW: Flutter Development Loop

**Purpose:** Rapid UI/Logic iteration for Flutter apps.

## 1. Setup
- [ ] Run `flutter pub get`.
- [ ] Check `flutter doctor` for environment issues.

## 2. Implement
- [ ] Modify widgets in `lib/`.
- [ ] Add/Update tests in `test/`.

## 3. Validate
- [ ] Run `flutter analyze`.
- [ ] If fail: Fix and repeat.
- [ ] Run `flutter test`.
- [ ] Produce `artifacts/FLUTTER_ANALYSIS.md`.

## 4. Visual Check
- [ ] Request user to run `flutter run` and provide screenshot/feedback if needed.
- [ ] Iterate based on visual feedback.

## 5. Finish
- [ ] Run `flutter format .`.
- [ ] Update `artifacts/DOCS_MANIFEST.md`.
- [ ] Complete `artifacts/PR_SUMMARY.md`.
