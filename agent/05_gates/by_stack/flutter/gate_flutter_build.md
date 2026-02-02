# Flutter Gate: Build

## Purpose

Ensure the Flutter app builds for target platforms.

## Rules

1. **Clean**: `flutter clean` before final build check.
2. **Target**: Must build for at least one platform (Android/iOS/Web) without error.
3. **Dependencies**: `pubspec.yaml` must be valid.

## Check Command

```bash
flutter pub get
flutter build apk --debug
# OR
flutter build web
```

## Failure criteria

- Build command fails.
- Dependency resolution (`pub get`) fails.
