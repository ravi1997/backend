# Flutter Release & Packaging

## Release Checklist
- [ ] Update version in `pubspec.yaml` (format: `1.0.0+1`).
- [ ] Configure signing configs (keystore for Android, certificates for iOS).
- [ ] Review app permissions limits (AndroidManifest, Info.plist).
- [ ] Run `flutter clean` before build.

## Command Example
```bash
# Obfuscate Dart code (recommended for production)
flutter build apk --obfuscate --split-debug-info=./debug-info
```

## Platform Specifics
- **Android**: Generate App Bundle (`.aab`) for Play Store.
- **iOS**: Archive via Xcode for App Store Connect.
- **Web**: `flutter build web --release` produces static files in `build/web`.
