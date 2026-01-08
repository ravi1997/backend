# Java Project Fingerprint

## Signatures

| File / Pattern | Type | Confidence | Notes |
| :--- | :--- | :--- | :--- |
| `pom.xml` | Build Definition | 1.0 | Maven project |
| `build.gradle` | Build Definition | 1.0 | Gradle project |
| `build.gradle.kts` | Build Definition | 1.0 | Gradle (Kotlin DSL) project |
| `settings.gradle` | Config | 0.9 | Gradle settings |
| `gradlew` | Wrapper | 1.0 | Gradle wrapper present |
| `mvnw` | Wrapper | 1.0 | Maven wrapper present |
| `*.java` | Source Code | 0.3 | Presence of source files only |

## Related Tools

-   **Build**: `mvn`, `gradle`, `./mvnw`, `./gradlew`
-   **Test**: `junit`, `testng`
