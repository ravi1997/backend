# Java Command Map

## Toolchain Selection Rules
1. **Wrapper Scripts**: Prefer `./gradlew` or `./mvnw` if present.
2. **System Build Tools**: Fallback to `gradle` or `mvn` in PATH.

## Canonical Commands

### Build
**Gradle**
```bash
./gradlew build
```

**Maven**
```bash
./mvnw package
```

### Test
**Gradle**
```bash
./gradlew test
```

**Maven**
```bash
./mvnw test
```

### Lint/Format
**Gradle (Spotless/Checkstyle)**
```bash
./gradlew spotlessApply
./gradlew check
```

**Maven (Spotless)**
```bash
./mvnw spotless:apply
```

### Run
**Spring Boot**
```bash
./gradlew bootRun
# OR
./mvnw spring-boot:run
```

**Jar Execution**
```bash
java -jar build/libs/app.jar
```

### Package
**Gradle**
```bash
./gradlew bootJar # Spring Boot
./gradlew jar     # Standard Library
```

**Maven**
```bash
./mvnw package
```

### CI
**GitHub Actions (Example)**
```yaml
- uses: actions/setup-java@v3
  with:
    distribution: 'temurin'
    java-version: '17'
- run: ./gradlew build
```
