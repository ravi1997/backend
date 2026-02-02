# Rules: Flutter & Dart

**Stack**: Flutter / Dart  
**Management**: Pub

---

## 1. Project Structure

- **Feature-First**: Organize code by feature (auth, feed, profile) rather than type (widgets, controllers).
- **Clean Architecture**: Separate Domain (Entities), Data (Repositories, Sources), and Presentation (Widgets, BLoC/Providers).

## 2. Code Quality

- **Linter**: Use `flutter_lints` or `very_good_analysis`.
- **Const**: Use `const` constructors for widgets wherever possible to optimize rebuilds.
- **Async**: Use `async/await` over raw `Future.then`.
- **Typing**: Avoid `dynamic`. Be explicit with types.
- **Null Safety**: Code MUST be sound null safe.

## 3. State Management

- **Standard**: Stick to ONE state management solution per project (BLoC, Riverpod, or Provider).
- **Logic Separation**: UI Widgets MUST NOT contain business logic. Delegate to State classes/controllers.

## 4. Testing

- **Unit Tests**: Test logic/BLoCs (`flutter test`).
- **Widget Tests**: Test UI components (`flutter test`).
- **Integration Tests**: Critical flows (`integration_test` package).
- **Mocks**: Use `mockito` or `mocktail` for dependencies.

## 5. Performance & Hygiene

- **Build Methods**: Keep `build()` pure and fast. No heavy computation or async calls in build.
- **Disposal**: Dispose controllers (TextEditingController, AnimationController) in `dispose()`.
- **Assets**: Define assets as constants or use code gen (FlutterGen) to avoid string typos.

---

## Enforcement Checklist

- [ ] `flutter analyze` returns zero issues
- [ ] No `print()` calls (use Logger)
- [ ] Const used for static widgets
- [ ] Tests cover logic and UI
- [ ] Null safety enabled
