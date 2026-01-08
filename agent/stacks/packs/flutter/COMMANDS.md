# Flutter Command Map

## Toolchain Selection
1. **FVM**: If `.fvm/` exists, prefix commands with `fvm`.
2. **Default**: Use `flutter` directly.

## Canonical Commands

### Build
**Android APK**
```bash
flutter build apk --release
```

**iOS (Mac only)**
```bash
flutter build ios --release --no-codesign
```

**Web**
```bash
flutter build web --release
```

### Test
**Unit/Widget Tests**
```bash
flutter test
```

**Integration Tests**
```bash
flutter test integration_test
```

### Lint/Format
**Format**
```bash
dart format .
```

**Analyze**
```bash
flutter analyze
```

### Run
**Mobile/Simulator**
```bash
flutter run
```

**Web Server**
```bash
flutter run -d chrome
```

### Package
**Pub Get**
```bash
flutter pub get
```

### CI
**GitHub Actions (Example)**
```yaml
- uses: subosito/flutter-action@v2
  with:
    code-coverage: true
- run: flutter pub get
- run: flutter test --coverage
```
