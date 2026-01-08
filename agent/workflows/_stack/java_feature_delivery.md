# Subflow: Java Feature Delivery

**Stack:** Java
**Parent:** `../feature_delivery.md`

## Build & Test

```bash
# Maven
./mvnw clean install
./mvnw test

# Gradle
./gradlew build
./gradlew test
```

## Linting

```bash
# Checkstyle / Spotless
./mvnw checkstyle:check
# or
./gradlew spotlessCheck
```

## Missing Environment

If the environment cannot run tests (e.g. valid cross-compile toolchain missing):
1. **Reproduce:** Document setup in `REPRODUCE.md`.
2. **Minimal Test:** Create a script to run available tests.
3. **Confidence:** Downgrade confidence until verified on target.

## Role Checklist: Tester

**Reference:** `agent/stacks/packs/java/TESTING.md`

- [ ] **Build:** Maven/Gradle build passes.
- [ ] **Unit Tests:** JUnit tests pass (100%).
- [ ] **Integration:** `@SpringBootTest` or TestContainers pass.
- [ ] **Coverage:** Jacoco report generated.
