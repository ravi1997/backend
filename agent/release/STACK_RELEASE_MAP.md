# Stack Release Map

This document maps generic release concepts to stack-specific implementations.

| Stack | Build Artifact | Packaging Format | Publishing Target | Key Verification Steps |
| :--- | :--- | :--- | :--- | :--- |
| **C++** | Binary Executable / Lib | `.tar.gz`, `.deb`, `.rpm` | GitHub Releases, Artifactory | `ldd` check, Symbol stripping, RPATH validation |
| **Java** | JAR / WAR | `.jar`, `.war` | Maven Repository, Docker Hub | `mvn verify`, Shadow JAR checking, Manifest check |
| **Python** | Distribution Package | `.whl` (Wheel), `.tar.gz` (sdist) | PyPI, Private Repo | `twine check`, `pip install <art>` smoke test |
| **Flutter**| App Bundle / APK / IPA| `.aab`, `.apk`, `.ipa` | App Store, Play Store | Signing config validation, Key store checks |
| **Web** | Static Assets / SSR | Directory (`dist/`, `build/`) | AWS S3, Vercel, Docker | Asset optimization check, Source map handling |

## Stack-Specific Details

### C++
*   **Artifacts**: Store debug symbols (`.debug`) separately from release binaries.
*   **Compression**: Use `tar.gz` for Linux, `zip` for Windows.
*   **Versioning**: Embed version in binary using compile-time defines (`-DVERSION=...`).

### Java
*   **Shading**: If building a fat JAR, ensure dependencies are relocated to avoid classpath conflicts.
*   **Compatibility**: Verify bytecode level (e.g., Java 17 target).

### Python
*   **Checks**: Strict `twine check` for metadata validity.
*   **Environment**: Test installation in a clean `venv`.

### Flutter
*   **Flavors**: Explicitly build `dev`, `staging`, `prod` flavors.
*   **Signing**: CI must access encrypted signing keys securely. Never commit keys to repo.

### Web
*   **CDN**: Upload assets with long-term caching headers (immutable).
*   **HTML**: Ensure `index.html` references the hashed asset filenames.
