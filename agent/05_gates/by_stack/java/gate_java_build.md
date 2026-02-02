# Java Gate: Build

## Purpose

Ensure Java artifact compilation.

## Rules

1. **Tool**: Maven (`pom.xml`) or Gradle (`build.gradle`).
2. **JDK**: Version must match `java_rules.md` (LTS versions preferred).
3. **No Skip**: Tests should not be skipped during build verification.

## Check Command

```bash
# Maven
mvn clean verify -DskipTests=false

# Gradle
./gradlew build
```

## Failure criteria

- Compilation failure.
- Dependency resolution failure.
