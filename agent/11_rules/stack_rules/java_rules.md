# Rules: Java & Spring Development

**Stack**: Java / Spring Boot  
**Build System**: Maven / Gradle

---

## 1. Project Structure

- **Standard**: Follow Standard Directory Layout (`src/main/java`, `src/test/java`).
- **Package Naming**: Lowercase, reverse domain (e.g., `com.company.project`).
- **Layered Architecture**: Controller → Service → Repository → Model.

## 2. Spring Patterns

- **Dependency Injection**: Use Constructor Injection over Field Injection (`@Autowired` on private fields is discouraged).
- **Configuration**: Prefer Java Configuration (`@Configuration`) over XML.
- **Profiles**: Use Profiles (`dev`, `prod`, `test`) for environment-specific config.
- **REST**: Use `@RestController` and `ResponseEntity` for API consistency.

## 3. Code Quality

- **Lombok**: Use Lombok for boilerplate (`@Data`, `@Slf4j`, `@Builder`) but be aware of pitfalls (toString recursion).
- **Streams**: Use Java Streams API for collection processing where readable.
- **Optional**: Use `Optional<T>` for return types that might be empty, avoid returning `null`.
- **Exceptions**: Use unchecked exceptions (runtime) for most business logic. Catch explicit exceptions at boundaries.

## 4. Testing

- **Framework**: JUnit 5 + Mockito.
- **Integration**: Use `@SpringBootTest` and Testcontainers for integration tests.
- **Coverage**: Minimum 80% line coverage for business logic.
- **Naming**: Test classes must end in `Test` or `IT` (Integration Test).

## 5. Security (Java Specific)

- **SQL Injection**: ALWAYS use JPA Repositories or Parameterized Queries. Never concat strings for SQL.
- **Logging**: Clean logs of sensitive data (PII, credentials) before writing.
- **Dependencies**: Monitor dependencies for vulnerabilities (OWASP Dependency Check).

---

## Enforcement Checklist

- [ ] Maven/Gradle build passes
- [ ] No Field Injection used
- [ ] JUnit 5 tests present
- [ ] Controller/Service/Repo layers respected
- [ ] No System.out.println (use Slf4j)
