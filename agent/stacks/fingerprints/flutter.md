# Flutter/Dart Project Fingerprint

## Signatures

| File / Pattern | Type | Confidence | Notes |
| :--- | :--- | :--- | :--- |
| `pubspec.yaml` | Config | 1.0 | Dart/Flutter project definition |
| `pubspec.lock` | Lockfile | 1.0 | Dart/Flutter lockfile |
| `analysis_options.yaml` | Config | 0.8 | Dart analyzer options |
| `ios/Runner.xcodeproj` | Platform | 1.0 | iOS native shell (implies Flutter if pubspec present) |
| `android/build.gradle` | Platform | 0.9 | Android native shell (implies Flutter if pubspec present) |
| `*.dart` | Source Code | 0.3 | Dart source files |

## Related Tools

-   **Build**: `flutter build`, `dart compile`
-   **Run**: `flutter run`, `dart run`
-   **Test**: `flutter test`, `dart test`
