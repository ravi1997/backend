# Flutter Diagnostics Bundle

- SDK info: `flutter doctor -v`; `flutter --version`.
- Dependencies: `flutter pub get` (capture output); `flutter pub outdated` for constraints.
- Analyzer/tests: `flutter analyze`; `flutter test` (with `--machine` optionally).
- Android: `./android/gradlew --version`; inspect `android/build.gradle` for AGP; `sdkmanager --list | head` if available.
- iOS: `pod --version`; `pod repo update` if stale; `xcodebuild -version` on macOS.
- Assets: `grep -n "assets:" -A5 pubspec.yaml`; verify files exist via `find assets -type f`.
- Flavors: list product flavors in `android/app/build.gradle`; check schemes in `ios/Runner.xcodeproj/project.pbxproj`.
- Size/perf: `flutter build appbundle --analyze-size` (dry-run), `flutter run --profile --trace-skia` for jank traces.
