# GATE: C++ Quality Guard

**Purpose:** Final verification gate before merging or completing a C++ task.
**Source:** `gates/CPP_GATE.md`

## 1. Static Analysis
- [ ] No compiler warnings (`-Wall -Wextra -Werror` recommended)
- [ ] `clang-tidy` checks passed (no critical warnings)
- [ ] `cppcheck` performed for common mistakes

## 2. Memory Safety
- [ ] No leaks reported by `Valgrind` or `LSAN`
- [ ] No out-of-bounds access reported by `ASAN`
- [ ] Smart pointers (`std::unique_ptr`, `std::shared_ptr`) used instead of raw `new/delete` where applicable

## 3. Build & Portability
- [ ] Clean build in a fresh build directory
- [ ] `CMakeLists.txt` uses `target_*` commands (Modern CMake)
- [ ] Headers are self-contained (no missing includes when used elsewhere)

## 4. Performance
- [ ] No obvious unnecessary copies (use `const&` for large objects)
- [ ] No redundant allocation in hot loops
- [ ] Big-O complexity for core algorithms is documented or optimal

## 5. Testing
- [ ] Unit tests cover new functionality
- [ ] Code coverage has not significantly decreased
- [ ] Thread safety verified if using concurrency (TSAN)

## Failure Procedure
If any of these fail:
1. Document the failure in `artifacts/BUILD_LOG.md`.
2. Re-route to `flows/CPP_DEBUGGING_FLOW.md`.
3. Do NOT mark task as complete.
