# WORKFLOW: Java Development Loop

**Purpose:** Standard flow for Java feature delivery.

## 1. Context
- [ ] Determine build system: Maven (`pom.xml`) or Gradle (`build.gradle`).
- [ ] Verify JDK version.

## 2. Dependencies
- [ ] Update dependencies if needed (`./mvnw dependency:resolve` or `./gradlew build`).

## 3. Implementation
- [ ] Apply code changes in `src/main/java`.
- [ ] Add tests in `src/test/java`.

## 4. Build & Test
- [ ] **Maven:** `./mvnw clean test`
- [ ] **Gradle:** `./gradlew clean test`
- [ ] Record results in `artifacts/BUILD_LOG.md`.

## 5. Documentation
- [ ] Update Javadocs.
- [ ] Verify `artifacts/DOCS_MANIFEST.md`.

## 6. Completion
- [ ] Run `spotless:apply` or `checkstyle`.
- [ ] Propose PR via `artifacts/PR_SUMMARY.md`.
