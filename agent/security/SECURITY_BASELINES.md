# Security Baselines & Remediation

This document defines the security standards, scanning tools, and remediation playbooks for each supported stack in the polyglot repository.

## Python

### Baseline
*   **Packet Manager**: `pip`, `poetry`, or `uv`.
*   **Vulnerability Scanning**: `pip-audit`.
*   **Static Analysis**: `bandit`.

### Audit Command
```bash
# Pip
pip-audit --desc

# Poetry
poetry export -f requirements.txt | pip-audit --no-deps -r /dev/stdin
```

### Remediation Playbook
1.  **Identify**: Run audit command to find CVEs.
2.  **Assess**: Check if the vulnerable package is a direct or transitive dependency.
3.  **Fix**:
    *   **Direct**: Upgrade in `requirements.txt` / `pyproject.toml`.
    *   **Transitive**: Upgrade the parent package or pinning the transitive dependency to a safe version (if strictly necessary).
4.  **Verify**: Re-run audit command.

---

## Node / Web

### Baseline
*   **Packet Manager**: `npm`, `pnpm`, or `yarn`.
*   **Vulnerability Scanning**: `npm audit`, `pnpm audit`.
*   **Static Analysis**: `eslint-plugin-security`.

### Audit Command
```bash
# NPM
npm audit

# PNPM
pnpm audit
```

### Remediation Playbook
1.  **Identify**: `npm audit` report.
2.  **Fix**:
    *   `npm audit fix` (for non-breaking changes).
    *   Manual upgrade for breaking changes.
    *   For `pnpm`, update `package.json` overrides if necessary.
3.  **Verify**: `npm audit` returns "0 vulnerabilities".

---

## Java / Android

### Baseline
*   **Build System**: Gradle or Maven.
*   **Vulnerability Scanning**: OWASP Dependency Check.
*   **Static Analysis**: SpotBugs / FindSecBugs.

### Audit Command
```bash
# Gradle (requires dependency-check plugin)
./gradlew dependencyCheckAnalyze
```

### Remediation Playbook
1.  **Identify**: Check `build/reports/dependency-check-report.html`.
2.  **Fix**:
    *   Upgrade dependency version in `build.gradle` / `pom.xml`.
    *   If transitive, use `constraints` (Gradle) or `dependencyManagement` (Maven) to force version.
3.  **Verify**: Re-run analysis.

---

## Flutter / Dart

### Baseline
*   **Packet Manager**: `pub`.
*   **Vulnerability Scanning**: `dart pub outdated --no-dev-dependencies`. (Note: Native CVE scanning requires checking Android/iOS folders separately).

### Audit Command
```bash
flutter pub outdated
# For complete security, audit the android/ and ios/ directories using their respective baselines.
```

### Remediation Playbook
1.  **Identify**: Outdated packages with constraints preventing upgrades.
2.  **Fix**:
    *   `flutter pub upgrade`
    *   Manually relax version constraints in `pubspec.yaml` if needed.
3.  **Verify**: `flutter pub outdated` shows up-to-date versions.

---

## General Remediation Procedures

### Verification Step
**EVERY** security fix must be verified:
1.  Run the stack-specific audit command.
2.  Run the application test suite (`make test` or equivalent).
3.  Verify no regression in related features.

### Rollback Plan
If a security fix breaks functionality:
1.  Revert the dependency upgrade.
2.  If the vulnerability is blocked (Critical) and cannot be fixed without breaking changes:
    *   Implement a **Temporary Mitigation** (e.g., disable affected code path, add WAF rule).
    *   Document in `security_exemptions.md` (or equivalent) with an expiration date.
