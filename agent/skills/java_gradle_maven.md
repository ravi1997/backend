# SKILL: Java & JVM Troubleshooting

**Purpose:** Comprehensive guide for agents to manage Java/JVM projects.
**Source:** `skills/java_gradle_maven.md`

## 1. Build System Mastery
- **Maven:**
  - `mvn clean install -DskipTests` (Fast build)
  - `mvn dependency:tree` (Debug conflicts)
  - `mvn help:effective-pom` (Resolve inheritance)
- **Gradle:**
  - `./gradlew build --info` (Verbosity)
  - `./gradlew dependencies` (Map graph)
  - `./gradlew clean build -x test` (Skip tests)

## 2. JVM Tuning & Performance
- **Heap sizing:** `-Xms` and `-Xmx`.
- **GC selection:** `-XX:+UseG1GC` (Default modern) or `-XX:+UseZGC` (Low latency).
- **Diagnostics:** `-XX:+UnlockDiagnosticVMOptions`.

## 3. Threading & Concurrency
- Use `java.util.concurrent` (Executors, CompletableFuture) instead of raw `Thread`.
- **Virtual Threads (Java 21+):** Use for high-concurrency IO tasks.
- Debug deadlocks with `jstack`.

## 4. Common Framework Patterns
- **Spring Boot:** Debug autoconfiguration with `--debug` flag.
- **Hibernate/JPA:** Monitor SQL with `spring.jpa.show-sql=true`.
- **Lombok:** Ensure annotation processing is enabled in the IDE/Compiler.

## 5. Tooling Reference
| Tool | Purpose | Command |
|------|---------|---------|
| `jps` | List Java processes | `jps -lm` |
| `jstack` | Thread dump | `jstack <pid>` |
| `jmap` | Heap summary | `jmap -heap <pid>` |
| `jcmd` | Diagnostic commands | `jcmd <pid> help` |
| `jstat` | GC monitoring | `jstat -gc <pid> 1000` |

## 6. Common Pitfalls
- **Memory leaks in static collections:** Maps that never clear.
- **Unclosed resources:** DB connections not in try-with-resources.
- **Incorrect equals/hashCode:** Breaking `HashSet` or `HashMap` behavior.
