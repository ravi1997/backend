# Flutter Release Checklist (Add-On)

- Flutter SDK version pinned (FVM or wrapper) and matches pubspec.lock; `flutter doctor -v` clean.
- Android: AGP/Gradle aligned; keystore env vars set; `flutter build appbundle --release` passes with size analysis reviewed; multidex enabled if needed; mapping file saved.
- iOS (macOS only): `pod install --repo-update` successful; correct team/provisioning; `flutter build ios --release --no-codesign` or archive smoke test.
- Assets/fonts declared and present; localization regenerated; golden tests updated intentionally.
- Platform channels tested; permissions declared; runtime checks for critical permissions.
- Performance: profile for jank; dispose controllers/streams; app size within target budgets.
- Security: secrets not hardcoded; env config uses dart-define; network cert pinning/HTTPS enforced where required.
