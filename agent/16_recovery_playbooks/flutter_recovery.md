# Flutter Recovery Playbook

Issue-Key `Issue-Key: FLUTTER-<hash>`. Map to HC-FLUTTER-XXX.

## RECOVERY-FLUTTER-001: SDK/Dependency Issues
- Check `flutter --version` and pubspec.lock; align via FVM or pinned SDK.
- Repair pub cache: `flutter pub cache repair`; rerun `flutter pub get`.
- Validate: `flutter analyze` clean; `flutter test` passes.

## RECOVERY-FLUTTER-002: Android/iOS Tooling
- Android: align AGP/Gradle versions; run `./android/gradlew tasks`; enable multidex if needed.
- iOS: `pod repo update && pod install --repo-update`; ensure signing/team IDs set; run `flutter build ios --no-codesign` for CI smoke.
- Validate: platform builds succeed locally/CI with correct runners.

## RECOVERY-FLUTTER-003: Platform Channels/Permissions
- Rebuild after `flutter clean`; confirm `GeneratedPluginRegistrant` called; match channel names.
- Add required permissions to AndroidManifest/Info.plist; handle runtime requests.
- Validate: integration test invoking channel methods passes.

## RECOVERY-FLUTTER-004: Assets/Localization
- Ensure assets/fonts declared in pubspec with correct paths; run `flutter pub get`.
- Regenerate localization with `flutter gen-l10n`; add missing ARB entries.
- Validate: assets load and localization works in app/golden tests.

## RECOVERY-FLUTTER-005: CI/Headless Builds
- Install Android SDK/NDK on runners; accept licenses; route iOS builds to macOS.
- Configure env vars (JAVA_HOME, ANDROID_HOME, PATH) before builds.
- Validate: CI build/test pipeline green across targets.

## RECOVERY-FLUTTER-006: Performance/Release Issues
- Profile with DevTools; reduce rebuilds; dispose controllers.
- For release crashes, adjust proguard/r8 rules; ensure signing credentials correct.
- Validate: run `flutter build appbundle` size analysis; release smoke test on device/emulator.
