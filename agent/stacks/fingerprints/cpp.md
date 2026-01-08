# C++ Project Fingerprint

## Signatures

| File / Pattern | Type | Confidence | Notes |
| :--- | :--- | :--- | :--- |
| `CMakeLists.txt` | Build Definition | 1.0 | Standard CMake project |
| `Makefile` | Build Definition | 0.8 | Generic Make project (could be used for others, check content) |
| `meson.build` | Build Definition | 1.0 | Meson build system |
| `conanfile.txt` | Package Manager | 1.0 | Conan package manager |
| `conanfile.py` | Package Manager | 1.0 | Conan package manager |
| `vcpkg.json` | Package Manager | 1.0 | vcpkg package manager |
| `*.cpp`, `*.h`, `*.cc` | Source Code | 0.3 | Presence of source files only (weak signal) |

## Related Tools

-   **Build**: `cmake`, `make`, `ninja`, `meson`
-   **Test**: `ctest`, `gtest`, `catch2`
