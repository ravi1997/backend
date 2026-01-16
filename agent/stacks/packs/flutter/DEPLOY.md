# Flutter Deployment Guide

## Mobile Support (iOS/Android)

### Android

```bash
flutter build apk --release
# or
flutter build appbundle --release
```

- **Output**: `build/app/outputs/flutter-apk/app-release.apk`
- **Signing**: Requires `key.properties` and keystore configuration.

### iOS

```bash
flutter build ipa --release
```

- **Requirement**: Must run on macOS with Xcode installed.
- **Output**: Upload via Xcode / Transporter.

## Web Support

```bash
flutter build web --release
```

- **Output**: `build/web/`
- **Hosting**: Serve as static files (Nginx, Firebase Hosting, S3).
- **Caveat**: Ensure `index.html` `<base href>` is correct.

## Docker Deployment (Web)

See `agent/snippets/flutter/Dockerfile.web.md` for a multi-stage Nginx build.

## Desktop Support

- **Linux**: `flutter build linux`
- **Windows**: `flutter build windows`
- **macOS**: `flutter build macos`
