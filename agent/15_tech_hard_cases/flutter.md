# Flutter Hard Cases & Failure Scenarios

Issue-Key example: `Issue-Key: FLUTTER-d1e2f3`. Prompt: `prompts/hard_cases/flutter_hard_cases.txt`.

## Build/Tooling

### HC-FLUTTER-001: Flutter SDK Version Drift
**Symptom:**
```
Because flutter_test from sdk depends on ... version solving failed
```
**Likely Causes:** sdk version mismatch; missing `flutter --version` alignment.
**Fast Diagnosis:** `flutter --version`; check `fvm` config.
**Fix Steps:** use FVM or pin version in `FVM_CONFIG`/`flutter_wrapper`; upgrade/downgrade SDK to match lockfile.
**Prevention:** commit `flutter --version` output; CI uses same version.

### HC-FLUTTER-002: Pub Cache Corruption
**Symptom:** repeated pub get failures.
**Likely Causes:** corrupted pub cache.
**Fast Diagnosis:** `flutter pub cache repair` output; check `PUB_CACHE`.
**Fix Steps:** run `flutter pub cache repair`; delete offending packages.
**Prevention:** isolate cache per CI runner; use `--offline` only with verified cache.

### HC-FLUTTER-003: Null-safety Migration Issues
**Symptom:**
```
Null check operator used on a null value
```
**Likely Causes:** mixed null-safety/non-null-safe deps; unchecked code.
**Fast Diagnosis:** `dart analyze`; check `pubspec.yaml` sdk constraints.
**Fix Steps:** upgrade deps to null-safe; add `!/?` handling; use `dart migrate`.
**Prevention:** enforce min SDK >=2.17; run analyzer in CI.

### HC-FLUTTER-004: Android Gradle Plugin Mismatch
**Symptom:**
```
Minimum supported Gradle version is ...
```
**Likely Causes:** plugin/gradle wrapper mismatch.
**Fast Diagnosis:** check `android/build.gradle` plugin version; `./android/gradlew --version`.
**Fix Steps:** align AGP and Gradle versions per compatibility matrix; update wrapper.
**Prevention:** pin AGP/Gradle; CI Android build job.

### HC-FLUTTER-005: iOS CocoaPods Failures
**Symptom:**
```
[!] CocoaPods could not find compatible versions
```
**Likely Causes:** pod repo stale; Ruby version issues.
**Fast Diagnosis:** `pod --version`; `pod repo update`.
**Fix Steps:** update pods; run `pod install --repo-update`; ensure Ruby/bundler versions pinned.
**Prevention:** use Gemfile for CocoaPods; cache Pods per lockfile.

### HC-FLUTTER-006: Xcode Signing Errors
**Symptom:** provisioning profile/cert errors.
**Likely Causes:** missing signing configs.
**Fast Diagnosis:** open Runner.xcodeproj settings; `xcodebuild -showBuildSettings`.
**Fix Steps:** set team ID, provisioning profiles; use automatic signing for dev.
**Prevention:** document signing setup; store profiles securely for CI.

### HC-FLUTTER-007: Android multidex/64K Limit
**Symptom:**
```
DexArchiveMergerException: Unable to merge dex
```
**Likely Causes:** hitting method limit without multidex.
**Fast Diagnosis:** check gradle logs; app/build.gradle for multidex.
**Fix Steps:** enable multidex; minSdk >=21 or add support lib.
**Prevention:** monitor method count; remove unused deps with R8.

### HC-FLUTTER-008: Flavor Build Misconfig
**Symptom:** wrong API endpoints or assets per flavor.
**Likely Causes:** missing flavor definitions; inconsistent bundle ids.
**Fast Diagnosis:** check `flutter build` args; inspect `android/app/src/<flavor>` and `ios` schemes.
**Fix Steps:** define flavors in Android/iOS configs; set bundle ids; configure dart defines.
**Prevention:** CI builds all flavors; document env mappings.

## Runtime/Platform Channels

### HC-FLUTTER-009: Platform Channel Method Not Found
**Symptom:**
```
MissingPluginException(No implementation found for method ...)
```
**Likely Causes:** plugin not registered; wrong channel name.
**Fast Diagnosis:** ensure `GeneratedPluginRegistrant` called; check method channel strings.
**Fix Steps:** rebuild after `flutter clean`; ensure plugin registration; match channel names on native side.
**Prevention:** integration tests invoking platform channels; keep plugin versions pinned.

### HC-FLUTTER-010: Platform Channel Type Mismatch
**Symptom:** runtime type errors crossing channel.
**Likely Causes:** sending non-JSON-serializable types.
**Fast Diagnosis:** add logging on native and dart sides; check codecs.
**Fix Steps:** convert to standard types; update codec (JSON/StandardMethodCodec).
**Prevention:** define schemas; validate payloads.

### HC-FLUTTER-011: Permissions Not Declared
**Symptom:**
```
PERMISSION_DENIED
```
**Likely Causes:** missing AndroidManifest/iOS plist entries.
**Fast Diagnosis:** inspect manifest/Info.plist.
**Fix Steps:** add permissions; request runtime permissions.
**Prevention:** permission checklist per feature; tests verifying permission prompts.

### HC-FLUTTER-012: Assets/Fonts Missing
**Symptom:**
```
Unable to load asset: assets/images/logo.png
```
**Likely Causes:** assets not listed in pubspec or path wrong.
**Fast Diagnosis:** check `pubspec.yaml` assets/fonts entries.
**Fix Steps:** add assets/fonts to pubspec; run `flutter pub get`; ensure correct paths/case.
**Prevention:** asset smoke tests; CI to run `flutter test` with golden images where applicable.

### HC-FLUTTER-013: Intl/Localization Failures
**Symptom:** missing translations; format errors.
**Likely Causes:** ARB missing locale; not rebuilding generated l10n.
**Fast Diagnosis:** check `l10n.yaml`; regenerate with `flutter gen-l10n`.
**Fix Steps:** add missing locale ARB; rerun gen; update delegates.
**Prevention:** l10n CI step; enforce translation completeness.

## CI & Headless Builds

### HC-FLUTTER-014: Headless CI Android Build Fails
**Symptom:** sdk/ndk missing.
**Likely Causes:** CI image lacks Android SDK components.
**Fast Diagnosis:** check ANDROID_HOME; run `sdkmanager --list`.
**Fix Steps:** install required platforms/build-tools; accept licenses; cache ~/.android.
**Prevention:** provision CI images; script sdkmanager install.

### HC-FLUTTER-015: iOS CI Build Fails (non-macOS)
**Symptom:** building iOS on non-macOS not supported.
**Likely Causes:** running on Linux/Windows.
**Fast Diagnosis:** check runner OS.
**Fix Steps:** use macOS runner or build via Codemagic/remote mac.
**Prevention:** CI matrix routes iOS jobs to macOS only.

### HC-FLUTTER-016: Flutter Test Widget Binding Errors
**Symptom:**
```
NoSuchMethodError: The method 'pumpWidget' was called on null.
```
**Likely Causes:** missing `TestWidgetsFlutterBinding.ensureInitialized()`.
**Fast Diagnosis:** inspect test setup.
**Fix Steps:** add binding initialization; use proper testWidgets wrappers.
**Prevention:** test template includes binding init.

### HC-FLUTTER-017: Golden Test Failures Across Platforms
**Symptom:** golden diffs inconsistent between CI/dev.
**Likely Causes:** font/Skia differences; device pixel ratio mismatches.
**Fast Diagnosis:** ensure fonts bundled; set `GoldenToolkit.runWithConfiguration`.
**Fix Steps:** pin fonts; set consistent surface size; use `flutter test --update-goldens` when intentional.
**Prevention:** deterministic golden config shared; run goldens in Dockerized env.

## Performance/UI

### HC-FLUTTER-018: Jank/Rebuild Storms
**Symptom:** dropped frames; debug shows many rebuilds.
**Likely Causes:** rebuilding heavy widgets; using setState broadly.
**Fast Diagnosis:** `flutter run --profile --trace-skia`; use Flutter DevTools rebuild profiler.
**Fix Steps:** memoize widgets; use ValueListenable/Provider/BLoC; split widgets.
**Prevention:** perf budget checks; DevTools captures in PRs.

### HC-FLUTTER-019: Excessive App Size
**Symptom:** APK/AAB too large.
**Likely Causes:** unused assets, debug symbols, no split per abi.
**Fast Diagnosis:** `flutter build appbundle --analyze-size`.
**Fix Steps:** enable split per abi; remove unused assets; shrink via R8.
**Prevention:** size analysis in release checklist; asset hygiene.

### HC-FLUTTER-020: Hot Reload Not Working
**Symptom:** changes not reflected.
**Likely Causes:** running in release/profile; code outside hot reload scope.
**Fast Diagnosis:** check mode; logs show "Hot reload was rejected".
**Fix Steps:** run in debug; avoid changes to main method signatures; restart if necessary.
**Prevention:** use hot restart when required; understand hot reload limits.

### HC-FLUTTER-021: State Management Bugs
**Symptom:** UI not updating on state change.
**Likely Causes:** not calling notifyListeners/emit; using wrong provider scope.
**Fast Diagnosis:** logs; check provider/bloc wiring.
**Fix Steps:** ensure state updates notify listeners; wrap widgets with correct providers.
**Prevention:** state management patterns documented; widget tests for state flows.

### HC-FLUTTER-022: Memory Leaks (Streams/Controllers)
**Symptom:** memory usage climbs over time.
**Likely Causes:** controllers/streams not disposed.
**Fast Diagnosis:** `flutter doctor`? (not), use DevTools memory; check for dispose methods.
**Fix Steps:** dispose controllers in `dispose`; use `StatefulWidget` lifecycle properly.
**Prevention:** lint rule (dart_code_metrics) to require dispose; tests with leak checks.

## Release

### HC-FLUTTER-023: Code Signing/Keystore Issues (Android)
**Symptom:**
```
Keystore was tampered with or password incorrect
```
**Likely Causes:** wrong keystore/password env.
**Fast Diagnosis:** verify keystore path/password; `keytool -list -keystore ...`.
**Fix Steps:** correct credentials; ensure env vars set in CI; re-import keystore.
**Prevention:** store keystore securely; document env vars; release checklist.

### HC-FLUTTER-024: iOS Archive/Upload Failures
**Symptom:** App Store upload errors re bitcode/provisioning.
**Likely Causes:** bitcode settings, missing provisioning.
**Fast Diagnosis:** Xcode archive logs; transporter output.
**Fix Steps:** disable bitcode for Flutter; ensure correct provisioning profiles; increment build numbers.
**Prevention:** release checklist; CI building archives with correct profiles.

### HC-FLUTTER-025: Crash in Release Only (Obfuscation/R8)
**Symptom:** crashes with missing stack traces.
**Likely Causes:** minification/obfuscation stripping symbols; missing proguard rules.
**Fast Diagnosis:** check proguard/r8 configs; reproduce with release profile.
**Fix Steps:** add keep rules for plugins; disable obfuscation temporarily; upload mapping files.
**Prevention:** maintain proguard rules; run release build smoke tests.

## Issue-Key and Prompt Mapping
- Example Issue-Key: `Issue-Key: FLUTTER-5c6a7b`
- Use prompt: `prompts/hard_cases/flutter_hard_cases.txt`
