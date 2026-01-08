# Java Release & Packaging

## Packaging Formats
- **Fat/Uber JAR**: Contains all dependencies (standard for Spring Boot).
- **WAR**: For deployment to Servlet containers (Tomcat/Jetty) - *legacy*.
- **Docker**: Jib or Dockerfile. (Jib allows building images without Docker daemon).

## Release Checklist
- [ ] Update version in `build.gradle` or `pom.xml`.
- [ ] Verify reproducible builds.
- [ ] Publish artifacts to Maven Central or internal Nexus/Artifactory.
- [ ] Tag git commit.

## Command Example
```bash
# Spring Boot Executable JAR
./gradlew bootJar

# Publish to Maven Local
./gradlew publishToMavenLocal
```
