# CHECKLIST: Java Build Failure Evidence

**Purpose:** Systematically collect evidence for Java build failures (Maven or Gradle).
**Source:** `checklists/JAVA_BUILD_EVIDENCE.md`

## 1. Environment & Tooling
- [ ] Record Java version (`java -version`)
- [ ] Record Build tool version (`mvn -v` or `./gradlew -v`)
- [ ] Check `JAVA_HOME` environment variable

## 2. Dependency Resolution
- [ ] Identify if it's a "Dependency Not Found" error
- [ ] Check for repository access (timeout, 401, 403)
- [ ] Check for version conflicts (JAR hell)
  - Maven: `mvn dependency:tree`
  - Gradle: `./gradlew dependencies`

## 3. Compilation Issues
- [ ] Locate the specific class and line number of the error
- [ ] Identify if it's a "Symbol Not Found" or "Incompatible Types" error
- [ ] Check for Annotation Processing (Lombok, MapStruct) issues

## 4. Test Failures
- [ ] Locate Surefire/Failsafe reports (`target/surefire-reports`)
- [ ] Identify falling test cases and stack traces
- [ ] Check for resource loading issues (files missing in `src/test/resources`)

## 5. Metadata for Agent
- [ ] `PROJECT_TYPE`: Java
- [ ] `BUILD_SYSTEM`: [maven/gradle]
- [ ] `FAILURE_STAGE`: [dependencies/compilation/testing]
