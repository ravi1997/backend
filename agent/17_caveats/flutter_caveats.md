# Flutter Caveats & Footguns

Issue-Key example: `Issue-Key: FLUTTER-2fa310`.

- Pin Flutter SDK version (FVM or wrapper); mismatches between dev/CI cause lockfile conflicts.
- Pub cache corruption is common on CI; repair or isolate cache per run.
- Keep null-safety enforced; set SDK constraints accordingly and run analyzer with `--fatal-infos` in CI.
- Android: keep AGP/Gradle aligned; enable multidex when approaching 64K methods; monitor method count.
- iOS: CocoaPods must use pinned versions via Gemfile; iOS builds require macOS runners only.
- Flavors: define consistently across Android/iOS; keep bundle identifiers and dart-defines in sync.
- Platform channels must register on both sides; channel names are case-sensitive.
- Assets/fonts need pubspec entries; watch case sensitivity on filesystems.
- Golden tests vary across environments; pin fonts/device pixel ratio and run in deterministic env.
- Release signing artifacts (keystore/profiles) must be stored securely and referenced via env vars; never commit secrets.
- Proguard/R8 can break plugins; maintain keep rules and upload mapping files.
