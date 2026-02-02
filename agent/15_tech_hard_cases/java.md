# Java Hard Cases & Failure Scenarios

Issue-Key example: `Issue-Key: JAVA-1c2d3e`. Prompt: `prompts/hard_cases/java_hard_cases.txt`.

## Build & Dependency Management (Maven/Gradle)

### HC-JAVA-001: Dependency Version Hell
**Symptom:**
```
ClassNotFoundException: org.slf4j.LoggerFactory
```
**Likely Causes:** conflicting transitive versions; eviction.
**Fast Diagnosis:** `mvn dependency:tree -Dincludes=slf4j` or `./gradlew dependencies --configuration runtimeClasspath`.
**Fix Steps:** align versions with BOM; add dependency constraints; exclude duplicates.
**Prevention:** use dependencyManagement/BOM; run version alignment in CI.

### HC-JAVA-002: Plugin Incompatibility
**Symptom:**
```
Execution default-cli of goal org.apache.maven.plugins:... failed
```
**Likely Causes:** plugin version incompatible with Java version.
**Fast Diagnosis:** check plugin versions; `java -version` vs plugin docs.
**Fix Steps:** upgrade/downgrade plugin; pin plugin versions.
**Prevention:** centralize plugin versions; use Maven Wrapper/Gradle Wrapper.

### HC-JAVA-003: Gradle Daemon Cache Corruption
**Symptom:** unexplained build failures resolved by clean.
**Likely Causes:** corrupt gradle cache.
**Fast Diagnosis:** `./gradlew --status`; check `~/.gradle/caches` size.
**Fix Steps:** `./gradlew --stop && ./gradlew clean`; delete caches if needed.
**Prevention:** CI uses isolated GRADLE_USER_HOME; periodic cache prune.

### HC-JAVA-004: Maven Snapshot Resolution Fails
**Symptom:**
```
Could not find artifact ...-SNAPSHOT
```
**Likely Causes:** snapshots not deployed or repo auth missing.
**Fast Diagnosis:** check settings.xml; `mvn -U dependency:resolve`.
**Fix Steps:** deploy snapshot; ensure credentials; refresh snapshots with `-U`.
**Prevention:** CI deploys snapshots automatically; avoid snapshot dependencies in release builds.

### HC-JAVA-005: Test Discovery Failures
**Symptom:**
```
No tests were found!
```
**Likely Causes:** wrong package naming, missing junit-vintage/launcher, ignored tests.
**Fast Diagnosis:** check surefire/surefire includes; `./gradlew test --tests '*MyTest'`.
**Fix Steps:** correct naming (`*Test.java`), add JUnit platform dependencies, configure includes.
**Prevention:** template test suites; CI gate ensures tests >0.

### HC-JAVA-006: Jacoco Coverage Missing
**Symptom:** coverage report empty.
**Likely Causes:** tests run in forked JVM without agent, multi-module misconfigured.
**Fast Diagnosis:** check surefire argLine/jacoco plugin settings.
**Fix Steps:** apply Jacoco plugin to all modules; set `jacoco.exec` merge; pass `-javaagent` in tests.
**Prevention:** CI stage to verify coverage threshold.

## Spring & Application Config

### HC-JAVA-007: Bean Definition/Wiring Errors
**Symptom:**
```
Unsatisfied dependency expressed through field ...
```
**Likely Causes:** missing @Component scan path, circular deps.
**Fast Diagnosis:** `--debug` logs; check package structure vs @SpringBootApplication location.
**Fix Steps:** adjust component scan base package; refactor to constructor injection; break cycles.
**Prevention:** use constructor injection only; modularize configs.

### HC-JAVA-008: Profile/Env Misconfiguration
**Symptom:** wrong properties loaded; `Environment` missing values.
**Likely Causes:** missing `spring.profiles.active`, wrong YAML indentation.
**Fast Diagnosis:** `--debug` to view active profiles; inspect YAML.
**Fix Steps:** set `SPRING_PROFILES_ACTIVE`; validate YAML; use profile-specific files.
**Prevention:** default profile config committed; document env vars.

### HC-JAVA-009: CORS/Security Misconfig
**Symptom:**
```
CORS policy error in browser
```
**Likely Causes:** missing CORS config or WebSecurity override blocking.
**Fast Diagnosis:** inspect SecurityConfig; logs for rejected origins.
**Fix Steps:** add `@Bean CorsConfigurationSource`; configure allowed origins/methods; ensure CSRF config matches API type.
**Prevention:** integration test hitting API with browser-like requests.

### HC-JAVA-010: Missing Actuator/Health Endpoints
**Symptom:** readiness/liveness probes failing.
**Likely Causes:** actuator not on classpath or endpoints disabled.
**Fast Diagnosis:** check dependencies; `management.endpoints.web.exposure.include`.
**Fix Steps:** add `spring-boot-starter-actuator`; enable endpoints.
**Prevention:** healthcheck contract test; document probe URLs.

### HC-JAVA-011: Database Connection Pool Exhausted
**Symptom:**
```
Timeout waiting for connection from pool
```
**Likely Causes:** unclosed connections, insufficient pool size.
**Fast Diagnosis:** pool metrics/logs; thread dump.
**Fix Steps:** ensure try-with-resources; tune pool sizes; add leak detection.
**Prevention:** connection leak detector in lower envs; metrics alerts.

### HC-JAVA-012: Lazy Initialization Exceptions
**Symptom:**
```
failed to lazily initialize a collection of role
```
**Likely Causes:** JPA session closed; DTO mapping done outside transaction.
**Fast Diagnosis:** enable SQL logs; check transactional boundaries.
**Fix Steps:** fetch joins or DTO projections; adjust transactional scope.
**Prevention:** avoid lazy collections in responses; use fetch profiles.

## Runtime & Packaging

### HC-JAVA-013: Classpath Conflicts
**Symptom:**
```
java.lang.NoSuchMethodError: method exists in different version
```
**Likely Causes:** multiple versions of same lib on classpath.
**Fast Diagnosis:** `mvn dependency:tree -Dverbose` or `jdeps -cp app.jar`.
**Fix Steps:** use dependency exclusion/constraints; shade or relocate when needed.
**Prevention:** CI gate for dependency convergence; prefer BOMs.

### HC-JAVA-014: OOM (Heap/Metaspace)
**Symptom:**
```
java.lang.OutOfMemoryError: Java heap space / Metaspace
```
**Likely Causes:** insufficient Xmx/Metaspace, leak.
**Fast Diagnosis:** GC logs, `jmap -heap <pid>`; analyze heap dump if possible.
**Fix Steps:** tune `-Xmx`, `-XX:MaxMetaspaceSize`; fix leaks; reduce caching.
**Prevention:** load tests with realistic traffic; set sane defaults in container args.

### HC-JAVA-015: GC Thrashing
**Symptom:** high CPU, long GC pauses.
**Likely Causes:** wrong GC for workload, small heap.
**Fast Diagnosis:** GC logs; `jstat -gcutil`.
**Fix Steps:** choose appropriate GC (G1/ZGC); adjust heap; reduce allocation hotspots.
**Prevention:** benchmark GC configs; set defaults in deployment manifests.

### HC-JAVA-016: Fat Jar Creation Fails
**Symptom:**
```
zip END header not found
```
**Likely Causes:** Gradle shadow/maven shade misconfig; duplicate files.
**Fast Diagnosis:** inspect build logs; run `jar tf build/libs/app-all.jar`.
**Fix Steps:** fix shadow/shade plugin config; merge service files; exclude duplicates.
**Prevention:** add integration test launching shaded jar.

### HC-JAVA-017: Container Image Build Errors
**Symptom:**
```
Could not find or load main class
```
**Likely Causes:** wrong ENTRYPOINT/CMD; jar path mismatch.
**Fast Diagnosis:** `docker run --rm image ls /app`; inspect Dockerfile.
**Fix Steps:** set correct `ENTRYPOINT ["java","-jar","/app/app.jar"]`; ensure jar copied to right path.
**Prevention:** add container smoke test in CI.

### HC-JAVA-018: Classpath at Runtime Missing Config
**Symptom:** env-specific props not loaded in container.
**Likely Causes:** config files not packaged; volume mount missing.
**Fast Diagnosis:** `jar tf app.jar | grep application`; `docker exec env`.
**Fix Steps:** package config or mount config map; set `SPRING_CONFIG_LOCATION`.
**Prevention:** containerized config tests; document config mounting.

### HC-JAVA-019: Insecure Deserialization
**Symptom:** security review flags usage of native Java serialization.
**Likely Causes:** using ObjectInputStream on untrusted data.
**Fast Diagnosis:** `rg "ObjectInputStream" src`.
**Fix Steps:** avoid Java serialization; use JSON/CBOR; if unavoidable, use validation filter.
**Prevention:** lint rule banning native serialization; security review checklist.

### HC-JAVA-020: Logging Secrets
**Symptom:** sensitive values in logs.
**Likely Causes:** logging full request bodies/config.
**Fast Diagnosis:** scan logs for keywords; `rg "password|secret|token" logs`.
**Fix Steps:** mask in logging frameworks; avoid logging secrets; use structured logging filters.
**Prevention:** logging policy; unit tests to assert masking; add log scrubbing in appender.

### HC-JAVA-021: TLS/Cert Errors
**Symptom:**
```
PKIX path building failed
```
**Likely Causes:** missing truststore, wrong hostname.
**Fast Diagnosis:** check cert chain with `openssl s_client`; inspect truststore path.
**Fix Steps:** add CA certs to truststore; set `-Djavax.net.ssl.trustStore`.
**Prevention:** manage trust via standard truststore image; rotate certs before expiry.

### HC-JAVA-022: Timezone/Locale Bugs
**Symptom:** timestamps wrong in production.
**Likely Causes:** default timezone not set; JVM running UTC vs local.
**Fast Diagnosis:** log `ZoneId.systemDefault()`; inspect container TZ.
**Fix Steps:** set `-Duser.timezone=UTC` (or target); audit date handling.
**Prevention:** enforce UTC in services; tests using fixed clock.

### HC-JAVA-023: Reflection/Module Access Errors
**Symptom:**
```
InaccessibleObjectException: module java.base does not "open java.lang" to unnamed module
```
**Likely Causes:** Java 17 strong encapsulation; missing `--add-opens`.
**Fast Diagnosis:** read stack; identify offending package.
**Fix Steps:** add `--add-opens` flags or upgrade library using reflection; avoid deep reflection.
**Prevention:** test on latest LTS; avoid reflective hacks.

### HC-JAVA-024: Slow Startup in Container
**Symptom:** cold start latency high.
**Likely Causes:** classpath scanning, entropy blocking.
**Fast Diagnosis:** `-Xlog:class+load=info`; check `/dev/random` usage.
**Fix Steps:** enable classpath indexing (spring-context-indexer), use `-Djava.security.egd=file:/dev/urandom`, trim classpath.
**Prevention:** measure startup in CI; use native image if appropriate.

### HC-JAVA-025: Native Library Load Failures
**Symptom:**
```
java.lang.UnsatisfiedLinkError: no foo in java.library.path
```
**Likely Causes:** missing native libs or wrong architecture.
**Fast Diagnosis:** check `java -XshowSettings:properties | grep java.library.path`; `ldd` on native lib.
**Fix Steps:** place native libs on java.library.path; package correct arch; use `System.loadLibrary` with full path.
**Prevention:** include native dep validation in container build; multi-arch testing.

## Issue-Key and Prompt Mapping
- Example Issue-Key: `Issue-Key: JAVA-77c1af`
- Use prompt: `prompts/hard_cases/java_hard_cases.txt`
