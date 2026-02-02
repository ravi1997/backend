# Flutter Gate: Security

## Purpose

Identify insecure packages and configuration.

## Rules

1. **Network**: Ensure HTTPS usage (no cleartext traffic) in `Info.plist`/`AndroidManifest.xml`.
2. **Permissions**: Request minimal permissions required.
3. **Obfuscation**: Use `--obfuscate` for release builds.

## Check Command

```bash
# Analyze code for risks
flutter analyze .
```

## Failure criteria

- Usage of deprecated insecure plugins.
- Hardcoded secrets in Dart code.
