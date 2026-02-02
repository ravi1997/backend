# Java Diagnostics Bundle

- Java info: `java -version`, `mvn -v`, `./gradlew --version`.
- Dependency graph: `mvn dependency:tree -Dverbose` or `./gradlew dependencies --configuration runtimeClasspath`.
- Test discovery: run `mvn -Dtest=*Test test -DfailIfNoTests=false` or Gradle equivalent; check Surefire reports.
- Spring diagnostics: run app with `--debug` and `SPRING_PROFILES_ACTIVE`; hit `/actuator/health` if available.
- GC/heap: enable `-Xlog:gc*` (Java 11+) or `-verbose:gc`; `jmap -heap <pid>` (where allowed).
- Jar inspection: `jar tf build/libs/*.jar | head` and verify main class/paths.
- TLS: `openssl s_client -connect host:port -servername host` to check chain; `keytool -list -keystore` for truststore.
- Container: `docker run --rm image java -version && ls -la /app` to confirm jar locations.
