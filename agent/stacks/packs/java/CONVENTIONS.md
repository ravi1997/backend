# Java Conventions

## File Structure
- `src/main/java`: Application source code.
- `src/main/resources`: Configuration and static resources.
- `src/test/java`: Test source code.
- `build.gradle` / `pom.xml`: Build configuration.

## Naming
- **Classes**: PascalCase
- **Methods**: camelCase
- **Variables**: camelCase
- **Constants**: SCREAMING_SNAKE_CASE
- **Packages**: lowercase (e.g., `com.example.project`)

## Code Style
- Follow Google Java Style Guide or project-specific Checkstyle rules.
- Prefer constructor injection over field injection.
- Use `Optional` only for return types, not for fields or parameters.
- Handle exceptions specifically; avoid `catch (Exception e)`.
