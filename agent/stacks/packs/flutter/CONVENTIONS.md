# Flutter Conventions

## File Structure
- `lib/`: Main source code.
    - `src/`: Implementation details (hidden from public API).
    - `widgets/`: Reusable UI components.
    - `models/`: Data classes.
    - `screens/` or `pages/`: Full-screen views.
- `test/`: Unit and widget tests.
- `integration_test/`: End-to-end tests.

## Naming
- **Classes/Enums**: UpperCamelCase.
- **Files/Libraries**: snake_case.
- **Variables/Constants**: lowerCamelCase.

## Code Style
- Use trailing commas for better formatting.
- Prefer `const` constructors where possible.
- Separate UI code from business logic (BLoC, Riverpod).
- Use strict typing; avoid `dynamic`.
