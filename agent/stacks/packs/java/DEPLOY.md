# Java Deployment Guide

## Build Artifacts

- **JAR**: Self-contained executable (Spring Boot).
- **WAR**: For deployment to Tomcat/Jetty.

## Build Command (Maven)

```bash
./mvnw clean package -DskipTests
# Artifact is usually in target/*.jar
```

## Build Command (Gradle)

```bash
./gradlew build -x test
# Artifact is usually in build/libs/*.jar
```

## Docker Deployment

See `agent/snippets/java/Dockerfile.md`.

## JVM Options

- **Memory**: Always configure heap (e.g., `-Xmx512m`).
- **Container Awareness**: Use `-XX:+UseContainerSupport` (standard in Java 10+).
