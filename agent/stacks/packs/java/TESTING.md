# Java Testing Strategy

## Overview

Enterprise-grade testing focusing on JVM stability and integration.

## Recommended Tools

| Type | Tool | Notes |
| :--- | :--- | :--- |
| **Unit Testing** | JUnit 5 | The standard. |
| **Mocking** | Mockito | Standard mocking framework. |
| **Integration** | TestContainers | For spinning up Docker dependencies (DB, Redis) in tests. |
| **Runner** | Maven Surefire | Standard test runner. |
| **Coverage** | Jacoco | Code coverage reports. |

## QA Gates Profile

### 1. Build
- Maven/Gradle build success.
- `checkstyle` or `spotbugs` (optional but recommended).

### 2. Tests
- **Unit:** 100% pass.
- **Integration:** `@SpringBootTest` or equivalent verified.

## Sample Command Pattern (Maven)

```bash
# Run Unit Tests
./mvnw test

# Run Integration Tests
./mvnw verify -Pintegration

# Check Coverage
./mvnw jacoco:report
```

## Anti-Patterns
- Using `System.out.println` in tests (Use Assertions).
- `Thread.sleep` in tests (Use Awaitility).
