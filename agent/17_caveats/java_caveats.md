# Java Caveats & Footguns

Issue-Key example: `Issue-Key: JAVA-fc12ab`.

- Always use Maven/Gradle wrappers; mismatched versions cause plugin/runtime failures.
- Dependency convergence matters: enforce BOMs and `mvn -DskipTests dependency:analyze` gate; avoid unpinned SNAPSHOTs in release builds.
- Spring component scan is package-based; moving @SpringBootApplication changes scan roots—verify after refactors.
- CORS/security defaults deny cross-origin; explicitly configure allowed origins and CSRF for APIs.
- Actuator endpoints are disabled by default; enable minimally and protect sensitive ones.
- Container images must set `-Djava.security.egd=file:/dev/urandom` to avoid entropy stalls.
- Logging frameworks can leak secrets; mask structured fields and avoid logging request bodies by default.
- Native serialization is unsafe—prefer JSON; if using, restrict allowed classes.
- Keep timezone consistent (prefer UTC); tests should use fixed clock.
- For GC tuning, avoid copying prod flags blindly; base on workload measurements.
