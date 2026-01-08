# SKILL: Flutter Development

Patterns:
- Use `pubspec.yaml` for dependency and asset management.
- Organize code into `lib/models`, `lib/views`, `lib/controllers` or similar.
- Prefer `StatelessWidget` where possible; use `StatefulWidget` or state management (Provider/Riverpod/Bloc) for dynamic parts.
- Run `flutter analyze` frequently to catch linting issues.
- Use `flutter format .` for consistent styling.
- Ensure `assets/` are correctly declared in `pubspec.yaml`.

Common Commands:
- Get Dependencies: `flutter pub get`
- Run App (Dev): `flutter run`
- Run Tests: `flutter test`
- Build APK: `flutter build apk`
- Build Web: `flutter build web`
- Analyze: `flutter analyze`

Troubleshooting:
- `Null check on a null value`: Check for uninitialized variables or missing null-safety operators.
- `A RenderFlex overflowed`: Check layout constraints, use `Flexible` or `Expanded`.
- `MissingPluginException`: Run `flutter clean` and rebuild; check plugin registration.

Evidence Checklist:
- `checklists/FLUTTER_ERROR_EVIDENCE.md`
