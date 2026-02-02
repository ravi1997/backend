# Skill: Manage Dependencies

**Role**: Maintenance Engineer  
**Output**: Updated dependency files  
**Complexity**: Medium

---

## Strategy

1. **Audit**: Check for outdated or vulnerable dependencies.
2. **Update**: Upgrade packages while respecting semantic versioning.
3. **Verify**: Ensure build and tests pass after updates.
4. **Lock**: Regenerate lock files.

---

## Stack-Specific Commands

### Node.js (npm)

- **Audit**: `npm audit`
- **Check Outdated**: `npm outdated`
- **Update**: `npm update` (minor/patch) or `npm install <pkg>@latest` (major)
- **Lock**: `package-lock.json` auto-updated.

### Python

- **Audit**: `pip-audit` or `safety check`
- **Check Outdated**: `pip list --outdated`
- **Update**: Edit `requirements.txt` or `pyproject.toml`
- **Lock**: `pip freeze > requirements.txt` or `poetry lock`

### Java (Maven/Gradle)

- **Audit**: `mvn dependency:analyze` / `gradle dependencyCheck`
- **Update**: `mvn versions:use-latest-releases`
- **Lock**: Build tools handle resolution.

### Flutter

- **Audit**: `flutter pub outdated`
- **Update**: `flutter pub upgrade`
- **Lock**: `pubspec.lock` auto-updated.

### C++ (CMake/Conan/Vcpkg)

- **Audit**: Check package manager manifest (conanfile.txt).
- **Update**: Update version numbers in manifest.

---

## Workflow

1. **Create Branch**: `chore/update-deps`.
2. **Review Changes**: Check changelogs for breaking changes.
3. **Apply Updates**: Run update commands.
4. **Run Tests**: **CRITICAL**. If tests fail, rollback specific package.
5. **Commit**: `chore: update dependencies` with list of changes.

---

## Dealing with Vulnerabilities

1. Identify vulnerability via audit.
2. Determine patched version.
3. Update specific package to patched version.
4. If no patch, verify if vulnerability affects usage (not exploitable).
5. Add suppression if false positive (with documentation).

---

## Outputs

- Updated configuration checks (`package.json`, etc.)
- Updated lock files
- Audit report (optional)
