# Java Troubleshooting

## Common Issues

### ClassNotFoundException / NoClassDefFoundError
- **Symptom**: Application fails at runtime finding classes.
- **Fix**: Check classpath, verify dependency scope (e.g., `implementation` vs `compileOnly`), check for shaded jar issues.

### OutOfMemoryError
- **Symptom**: `java.lang.OutOfMemoryError: Java heap space` or `Metaspace`.
- **Fix**: Analyze heap dump, tune JVM flags (`-Xmx`, `-Xms`), check for memory leaks.

### Gradle/Maven Build Failures
- **Symptom**: Dependency resolution errors.
- **Fix**: Run with stacktrace (`./gradlew build --stacktrace`) or debug info (`-d`). Check network/proxy settings if behind firewall.

### Encoding Issues
- **Symptom**: Weird characters in input/output.
- **Fix**: Ensure `-Dfile.encoding=UTF-8` is set for JVM.
