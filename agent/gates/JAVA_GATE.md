# GATE: Java Quality Guard

**Purpose:** Final verification gate before merging or completing a Java task.
**Source:** `gates/JAVA_GATE.md`

## 1. Static Analysis & Linting
- [ ] `Checkstyle` or `Google Java Format` compliance
- [ ] `SpotBugs` or `SonarQube` report (no High/Critical issues)
- [ ] No compilation warnings (especially unchecked/deprecation warnings)

## 2. Dependency Health
- [ ] No vulnerable dependencies (`mvn dependency-check:check` or `gradle dependencyCheckAnalyze`)
- [ ] No unused dependencies identified
- [ ] All library versions are explicitly managed (no dynamic `+` versions in Gradle)

## 3. Testing & Coverage
- [ ] Unit tests pass (`mvn test` or `./gradlew test`)
- [ ] Integration tests pass (if applicable)
- [ ] Minimum line coverage (e.g., 80%) met by `JaCoCo`

## 4. JVM & Configuration
- [ ] No `System.gc()` calls in user code
- [ ] Proper use of `Try-with-resources` for all auto-closeable objects
- [ ] Logging uses a standard framework (SLF4J) instead of `System.out.println`

## 5. Metadata for Agent
- [ ] `GATE_TYPE`: QUALITY
- [ ] `LANGUAGE`: JAVA
- [ ] `VERIFIED_BY`: [MAVEN/GRADLE/SONAR]

## Failure Procedure
If any of these fail:
1. Document the failure in `artifacts/BUILD_LOG.md`.
2. Follow `flows/JAVA_RUNTIME_TRIAGE.md` if tests failed.
3. Do NOT mark task as complete.
