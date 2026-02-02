# Java Recovery Playbook

Use Issue-Key `Issue-Key: JAVA-<hash>`. Map to HC-JAVA-XXX.

## RECOVERY-JAVA-001: Dependency/Build Failures
- Run `mvn dependency:tree` or `./gradlew dependencies` to locate conflicts; align versions via BOM/constraints and exclusions.
- Clear caches (`./gradlew --stop && ./gradlew clean`, remove `~/.m2/repository/<group>/<artifact>/<version>` if poisoned).
- Pin plugin versions; ensure Maven/Gradle wrapper matches CI.
- Validate with clean build and test run.

## RECOVERY-JAVA-002: Test Discovery & Coverage
- Confirm naming conventions; add JUnit platform dependencies; run `./gradlew test --tests` to target missing tests.
- Fix Jacoco configuration; merge coverage for multi-module builds.
- Validate: tests count >0 and coverage reports generated.

## RECOVERY-JAVA-003: Spring Wiring/Config Issues
- Enable `--debug` and review bean definitions; adjust component scan and constructor injection.
- Set profiles explicitly via `SPRING_PROFILES_ACTIVE`; correct YAML indentation; verify env vars present.
- Fix CORS/security configs and health endpoints; retest with curl/postman and health probes.

## RECOVERY-JAVA-004: Runtime Classpath/OOM/GC
- Inspect classpath conflicts; enforce dependency convergence; rebuild shaded/fat jar if needed.
- For OOM/GC, capture heap/GC logs; tune `-Xmx/-Xms`, choose GC (G1/ZGC); fix leaks.
- Validate: application starts with expected heap usage; no GC thrash.

## RECOVERY-JAVA-005: Packaging & Containers
- Inspect jar contents (`jar tf`); fix ENTRYPOINT/CMD; ensure config packaged or mounted.
- Rebuild container with correct jar path; run smoke test `docker run image java -jar /app/app.jar --help`.
- Validate: container healthcheck/actuator endpoints respond; image uses pinned base.

## RECOVERY-JAVA-006: Security & Logging
- Replace native serialization; remove logging of secrets; add masking filters.
- Ensure TLS truststores configured; set timezone explicitly if needed.
- Validate: security scans clean; logs free of sensitive data.
