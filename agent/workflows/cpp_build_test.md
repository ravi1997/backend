# WORKFLOW: C++ Build & Test Loop

**Purpose:** Ensure C++ code compiles and passes tests before proposal.

## 1. Environment Check
- [ ] Verify `CMakeLists.txt` exists.
- [ ] Check for `compiler` (gcc/clang).

## 2. Configuration
- [ ] Create build directory: `mkdir -p build`.
- [ ] Run CMake: `cmake -B build -S .`.
- [ ] Capture configuration errors in `artifacts/BUILD_LOG.md`.

## 3. Compilation
// turbo
- [ ] Run build: `cmake --build build -j$(nproc)`.
- [ ] If fail: Run `checklists/CPP_BUILD_ERROR_EVIDENCE.md` and fix.

## 4. Testing
// turbo
- [ ] Run CTest: `ctest --test-dir build --output-on-failure`.
- [ ] If fail: Analyze log, fix, and repeat from Step 3.

## 5. Quality
- [ ] Run `clang-format` on changed files.
- [ ] Check for memory leaks if `valgrind` is available.

## 6. Cleanup
- [ ] Ensure `build/` is in `.gitignore`.
- [ ] Produce `artifacts/PR_SUMMARY.md`.
