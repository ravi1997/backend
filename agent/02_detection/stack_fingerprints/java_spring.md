# Stack Fingerprint: Java Spring

## Purpose

Identifies and configures for a Java Spring Boot application.

## Signals

- `spring-boot-starter-web` in `pom.xml` or `build.gradle`.
- `@SpringBootApplication` annotation.

## Configuration

- **Build**: `mvn clean install` or `./gradlew build`.
- **Test**: `mvn test` or `./gradlew test`.
- **Environment**: JVM (JDK 17+).
