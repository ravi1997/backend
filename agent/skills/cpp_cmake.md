# SKILL: C++ & Modern CMake Troubleshooting

**Purpose:** Comprehensive guide for agents to manage C++ projects.
**Source:** `skills/cpp_cmake.md`

## 1. Modern CMake Patterns
- **Target-based configuration:**
  ```cmake
  target_include_directories(my_target PUBLIC include)
  target_link_libraries(my_target PRIVATE external_lib)
  target_compile_features(my_target PUBLIC cxx_std_20)
  ```
- **Finding Dependencies:**
  - `find_package(PkgName REQUIRED)`
  - Use `FetchContent` for header-only or simple git dependencies.

## 2. Build Optimization
- Use `ccache` for faster rebuilds.
- Use `ninja` instead of `make` where possible.
- Unity builds: `set(CMAKE_UNITY_BUILD ON)`.

## 3. Profiling and Performance
- **Perf:** `perf record -g ./binary` -> `perf report`.
- **Valgrind Callgrind:** `valgrind --tool=callgrind ./binary` -> `kcachegrind`.
- **Flamegraphs:** Generate to visualize bottlenecks.

## 4. Memory Management & Safety
- Prefer `RAII` (Resource Acquisition Is Initialization).
- **Rule of Zero/Three/Five:** Ensure proper copy/move semantics.
- Use `std::span` (C++20) or `string_view` for efficient slicing.

## 5. Tooling Reference
| Tool | Purpose | Command |
|------|---------|---------|
| `gdb` | Debugger | `gdb --args ./bin` |
| `clang-format` | Formatting | `clang-format -i main.cpp` |
| `clang-tidy` | Linting | `clang-tidy main.cpp --` |
| `nm` | Symbol check | `nm -C lib.so` |
| `ldd` | Dynamic deps | `ldd ./binary` |

## 6. Common Pitfalls
- **ODR (One Definition Rule) violations:** Inline functions or multiple definitions.
- **Dangling references:** Returning `const&` to a local variable.
- **Linker errors:** Library order in `target_link_libraries`.
