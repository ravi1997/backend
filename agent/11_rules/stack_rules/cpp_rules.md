# Rules: C++ Development

**Stack**: C/C++  
**Standards**: C++17 / C++20 / C++23  
**Build System**: CMake

---

## 1. Modern C++ Standards

- **Standard Version**: Projects MUST explicitly define the standard version in `CMakeLists.txt` (17, 20, or 23).
- **No Raw Pointers**: Use smart pointers (`std::unique_ptr`, `std::shared_ptr`) for ownership. Raw pointers only for non-owning views.
- **Auto Usage**: Use `auto` for complex types or when the type is obvious (AAA rule: Almost Always Auto).
- **Const Correctness**: Mark methods and variables `const` wherever possible.
- **Move Semantics**: Prefer pass-by-value and move over pass-by-const-reference for sink arguments.

## 2. CMake Build System

- **Modern CMake**: Use CMake 3.15+ features.
- **Target-Based**: Use `target_include_directories`, `target_compile_options`, etc., over global variables.
- **Exporting**: Libraries MUST export their targets properly for downstream consumption.
- **Out-of-Source Builds**: NEVER build in the source directory. Always use a `build/` folder.

## 3. Safety & Hygiene

- **Sanitizers**: Development builds MUST have ASan (AddressSanitizer) and UBSan (UndefinedBehaviorSanitizer) optional/enabled.
- **Warnings**: Enable `-Wall -Wextra -Wpedantic` (or MSVC equivalents). Treat warnings as errors in CI.
- **Static Analysis**: Run `clang-tidy` or `cppcheck` as part of the pipeline.
- **Formatting**: Enforce `clang-format` on all source files.

## 4. Testing

- **Framework**: Use Google Test (GTest) or Catch2.
- **Unit Tests**: Every class/module MUST have accompanying unit tests.
- **Integration Tests**: CTest MUST be used to run the test suite.

## 5. Security (C++ Specific)

- **Bounds Checking**: Use `std::array` or `std::vector` with `.at()` or iterators over C-style arrays.
- **String Handling**: Avoid `strcpy`, `strcat`, `sprintf`. Use `std::string` and `std::format` (C++20).
- **Memory Safety**: NO use of `new` and `delete` explicitly (use `std::make_unique`, etc.).

---

## Enforcement Checklist

- [ ] CMakeLists.txt defines CXX_STANDARD
- [ ] No raw "new/delete" found
- [ ] Sanitizers configured in build options
- [ ] clang-format file exists
- [ ] Tests match source structure
