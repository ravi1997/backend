# Java Gate: Security

## Purpose

Identify vulnerabilities in dependencies and code patterns.

## Rules

1. **Dependencies**: No usage of libs with CVEs (score > 7).
2. **SQL Injection**: No concatenation in SQL queries (use PreparedStatement).
3. **Secrets**: No hardcoded API keys.

## Check Command

```bash
# Maven Dependency Check
mvn org.owasp:dependency-check-maven:check
```

## Failure criteria

- OWASP Dependency Check failure.
- Detected hardcoded credentials.
