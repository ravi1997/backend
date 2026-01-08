# C++ Testing Strategy

## Overview

High-performance/system-level testing requiring rigorous memory safety checks.

## Recommended Tools

| Type | Tool | Notes |
| :--- | :--- | :--- |
| **Unit Testing** | GTest (GoogleTest) | Standard for most C++ projects. |
| **Unit Testing** | Catch2 | Header-only, good for modern C++ (C++14+). |
| **Memory Safety** | Valgrind (Memcheck) | Detects memory leaks/errors. Slow but thorough. |
| **Sanitizers** | ASan, TSan, UBsan | Compile-time flags (`-fsanitize=address`) for real-time checks. |
| **Mocking** | GMock | Bundled with GTest. |

## QA Gates Profile

### 1. Build
- Flag: `-Wall -Wextra -Werror` (stop on warnings).
- Standard: C++17 or C++20 (defined in `CMakeLists.txt`).

### 2. Tests
- **Unit:** 100% coverage of business logic.
- **Integration:** Test binary with input/output fixtures.

### 3. Memory Safety (Critical)
- **Sanitizers:** CI build **MUST** run with ASan (AddressSanitizer) enabled for tests.
- **Valgrind:** Nightly run recommended for deep leak detection.

## Sample Command Pattern
```bash
# Build with ASan
cmake -B build -DCMAKE_BUILD_TYPE=Debug -DENABLE_ASAN=ON
cmake --build build

# Run Tests
ctest --test-dir build --output-on-failure
```
