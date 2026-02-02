# CMake Hard Cases & Failure Scenarios

Issue-Key example: `Issue-Key: CMAKE-93af10`. Use prompt `prompts/hard_cases/cmake_hard_cases.txt`.

## Configuration & Generators

### HC-CMAKE-001: Generator Mismatch (Ninja vs Make)
**Symptom:**
```
The build directory was generated with "Unix Makefiles" but the current generator is "Ninja"
```
**Likely Causes:** reusing build dir with different generator.
**Fast Diagnosis:** check `CMakeCache.txt | grep CMAKE_GENERATOR`.
**Fix Steps:** delete/recreate build dir or use distinct build dirs per generator.
**Prevention:** script builds with `-B build-ninja -G Ninja` to avoid reuse.

### HC-CMAKE-002: Toolchain File Ignored
**Symptom:**
```
Using default compiler instead of cross toolchain
```
**Likely Causes:** passing toolchain without `-DCMAKE_TOOLCHAIN_FILE` on first configure.
**Fast Diagnosis:** inspect `CMakeCache.txt` for `CMAKE_TOOLCHAIN_FILE`.
**Fix Steps:** wipe cache; configure with `cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=...`.
**Prevention:** enforce toolchain flag in build scripts.

### HC-CMAKE-003: Stale Cache Variables
**Symptom:** unexpected paths/flags after config change.
**Likely Causes:** cache retains removed vars.
**Fast Diagnosis:** `grep VAR CMakeCache.txt`; compare to CMakeLists.
**Fix Steps:** remove cache or `cmake -U VAR -B build`.
**Prevention:** clean cache when toggling options; use presets.

### HC-CMAKE-004: Wrong Build Directory
**Symptom:**
```
CMake Error: The source directory "/tmp/build" does not appear to contain CMakeLists.txt
```
**Likely Causes:** swapped -S/-B.
**Fast Diagnosis:** check command history.
**Fix Steps:** run `cmake -S . -B build`.
**Prevention:** wrap commands in scripts to avoid manual mistakes.

## Dependency Discovery

### HC-CMAKE-005: find_package Fails (Missing Config)
**Symptom:**
```
Could NOT find Foo (missing: Foo_DIR)
```
**Likely Causes:** package not installed, wrong prefix, missing config files.
**Fast Diagnosis:** `cmake --find-package -DNAME=Foo -DMODE=EXIST`.
**Fix Steps:** install dev package; set `Foo_DIR`/`CMAKE_PREFIX_PATH`; vendor via FetchContent.
**Prevention:** document dependencies; add CI that installs required packages.

### HC-CMAKE-006: Custom Find Module Wrong
**Symptom:**
```
Imported target Foo::Foo not found
```
**Likely Causes:** module returns inconsistent variables/targets.
**Fast Diagnosis:** inspect `cmake/FindFoo.cmake`; print variables during configure.
**Fix Steps:** align variables (`Foo_INCLUDE_DIRS`, `Foo_LIBRARIES`) and create imported targets; add REQUIRED components handling.
**Prevention:** write find modules using modern imported targets only.

### HC-CMAKE-007: pkg-config Not Honored
**Symptom:** pkg-config packages ignored.
**Likely Causes:** `PKG_CONFIG_PATH` missing; pkg-config not installed.
**Fast Diagnosis:** `pkg-config --modversion foo`.
**Fix Steps:** install pkg-config; set `ENV{PKG_CONFIG_PATH}` before configure.
**Prevention:** check pkg-config availability in configure script.

### HC-CMAKE-008: Incorrect include_directories Usage
**Symptom:** unexpected include ordering, global pollution.
**Likely Causes:** using global `include_directories` instead of target-level.
**Fast Diagnosis:** search `include_directories(` in CMakeLists.
**Fix Steps:** replace with `target_include_directories` and proper scope.
**Prevention:** forbid directory-scope include_directories in reviews.

### HC-CMAKE-009: target_link_libraries Wrong Scope/Order
**Symptom:** missing symbols for consumers.
**Likely Causes:** deps marked PRIVATE; order wrong for static libs.
**Fast Diagnosis:** inspect link line; `cmake --graphviz=graph.dot`.
**Fix Steps:** mark consumer deps PUBLIC/INTERFACE; ensure order for static libs (dependents before dep libs).
**Prevention:** target-based linking only; add interface tests.

### HC-CMAKE-010: Compile Commands Missing
**Symptom:** IDE tooling lacks compile_commands.json.
**Likely Causes:** not enabling export.
**Fast Diagnosis:** check for `compile_commands.json` in build dir.
**Fix Steps:** configure with `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; copy file to project root if needed.
**Prevention:** default ON in presets.

## Build & Install

### HC-CMAKE-011: Multi-config vs Single-config Mixups
**Symptom:**
```
Ninja: error: unknown target 'install/strip'
```
**Likely Causes:** using `--config` incorrectly with single-config generator.
**Fast Diagnosis:** check generator type.
**Fix Steps:** use `cmake --build build --config Release` only for multi-config; separate build dirs otherwise.
**Prevention:** document generator expectations in README/presets.

### HC-CMAKE-012: Exported Targets Missing
**Symptom:** downstream cannot `find_package` installed project.
**Likely Causes:** install(EXPORT) incomplete; namespaces missing.
**Fast Diagnosis:** inspect installed `*Config.cmake`; check exported target names.
**Fix Steps:** add `install(EXPORT <name> NAMESPACE Foo:: DESTINATION lib/cmake/Foo)` and configure_package_config_file.
**Prevention:** add packaging test using `find_package(Foo CONFIG REQUIRED)` in CI.

### HC-CMAKE-013: FetchContent Network Failures
**Symptom:**
```
fatal: unable to access https://...: Could not resolve host
```
**Likely Causes:** offline builds, proxy missing.
**Fast Diagnosis:** check network; `git config --global http.proxy`.
**Fix Steps:** vendor deps in advance; use mirrors; allow `FETCHCONTENT_FULLY_DISCONNECTED` with pre-populated source.
**Prevention:** cache dependencies; mirror artifacts internally.

### HC-CMAKE-014: FetchContent Version Drift
**Symptom:** different versions fetched on CI vs dev.
**Likely Causes:** missing `GIT_TAG` lock; using `GIT_REPOSITORY` default branch.
**Fast Diagnosis:** inspect FetchContent declarations.
**Fix Steps:** pin `GIT_TAG` to commit; add `UPDATE_DISCONNECTED TRUE`.
**Prevention:** centralize versions; run `cmake -DFETCHCONTENT_FULLY_DISCONNECTED=ON` in CI to ensure vendored.

### HC-CMAKE-015: install(RUNTIME/LIBRARY) Paths Wrong
**Symptom:**
```
Binary not found after install; libs in unexpected dir
```
**Likely Causes:** using hardcoded `bin/lib` paths with custom `CMAKE_INSTALL_LIBDIR`.
**Fast Diagnosis:** inspect `GNUInstallDirs` settings.
**Fix Steps:** include `GNUInstallDirs` and use variables (`${CMAKE_INSTALL_BINDIR}` etc.).
**Prevention:** always include `GNUInstallDirs` in install rules.

### HC-CMAKE-016: Component Install Breaks
**Symptom:** component install missing files.
**Likely Causes:** targets not assigned COMPONENT or inconsistent names.
**Fast Diagnosis:** `cmake --install build --component <name> --dry-run`.
**Fix Steps:** assign COMPONENT on install commands; align component names.
**Prevention:** test component installs in CI.

### HC-CMAKE-017: Cross-Compile Sysroot Not Used
**Symptom:** host includes/libs leaked into cross build.
**Likely Causes:** toolchain file missing `CMAKE_SYSROOT` and search path tweaks.
**Fast Diagnosis:** check `CMAKE_FIND_ROOT_PATH_MODE_*` in cache; inspect compile commands for host paths.
**Fix Steps:** set `CMAKE_SYSROOT` and find root path modes to ONLY; verify pkg-config path uses sysroot.
**Prevention:** validated cross toolchain file; CI job for cross build.

### HC-CMAKE-018: Generator Expressions Misused
**Symptom:**
```
CMake Error: Error evaluating generator expression
```
**Likely Causes:** using target properties not available at configure time; malformed `$<IF:>`.
**Fast Diagnosis:** read expression; check property availability.
**Fix Steps:** simplify expressions; move logic to target properties; use `cmake --trace-expand`.
**Prevention:** avoid nesting generator expressions; test configure with `-Wdev`.

### HC-CMAKE-019: Policy Warnings Elevated
**Symptom:**
```
Policy CMP0074 is not set: find_package uses <Package>_ROOT variables.
```
**Likely Causes:** relying on old behavior without setting policy.
**Fast Diagnosis:** read warnings; check `cmake --version` policy docs.
**Fix Steps:** set `cmake_policy(SET CMP0074 NEW)` (or OLD) consciously; update code.
**Prevention:** add minimum CMake version and set policies explicitly.

### HC-CMAKE-020: In-source Build Pollution
**Symptom:** build artifacts inside source tree.
**Likely Causes:** running `cmake .` accidentally.
**Fast Diagnosis:** check for `CMakeFiles/` in root.
**Fix Steps:** delete generated files; enforce out-of-source builds with guard at top of CMakeLists.
**Prevention:** add guard:
```cmake
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
  message(FATAL_ERROR "In-source builds not allowed")
endif()
```

### HC-CMAKE-021: Mixed Debug/Release Linking
**Symptom:** linking debug libs into release binary (and vice versa).
**Likely Causes:** incorrect `CMAKE_BUILD_TYPE` or generator multi-config confusion.
**Fast Diagnosis:** inspect library paths for `/debug/` or `/release/` segments.
**Fix Steps:** rebuild all deps for same config; use `--config` correctly; separate build dirs.
**Prevention:** configure distinct output directories per config.

### HC-CMAKE-022: No Warnings-as-Errors Control
**Symptom:** CI passes locally but fails with `-Werror` flags in pipeline.
**Likely Causes:** developers not building with same warning set.
**Fast Diagnosis:** inspect `CMAKE_CXX_FLAGS`/target properties for warnings.
**Fix Steps:** centralize warnings and `WERROR` option; allow opt-out for third-party.
**Prevention:** gate PRs on warning-clean builds; enforce consistent warning set.

### HC-CMAKE-023: Custom Command Rebuild Storms
**Symptom:** custom command runs every build.
**Likely Causes:** missing OUTPUT/DEPENDS; uses `COMMAND` without outputs.
**Fast Diagnosis:** inspect `add_custom_command`; check ninja log.
**Fix Steps:** declare OUTPUT and DEPENDS properly; mark BYPRODUCTS; avoid touching source dir.
**Prevention:** design custom commands with explicit outputs and dep chains.

### HC-CMAKE-024: Package Config Path Collisions
**Symptom:** wrong project found by `find_package` due to same package name.
**Likely Causes:** multiple versions installed in PATH.
**Fast Diagnosis:** `cmake --debug-find -DFoo_DIR=` to see search order.
**Fix Steps:** set `CMAKE_PREFIX_PATH` and `Foo_ROOT` explicitly; remove old packages.
**Prevention:** use project-specific namespaces to reduce collisions.

### HC-CMAKE-025: Testing Not Discovered (CTest)
**Symptom:**
```
No tests were found!!!
```
**Likely Causes:** missing `enable_testing()` or `add_test` not called.
**Fast Diagnosis:** check CTestTestfile.cmake.
**Fix Steps:** add `enable_testing()` near top-level; register tests; ensure working directory set correctly.
**Prevention:** template test registration; CI `ctest --output-on-failure` gate.

## Issue-Key and Prompt Mapping
- Example Issue-Key: `Issue-Key: CMAKE-6b71dd`
- Use prompt: `prompts/hard_cases/cmake_hard_cases.txt`
- See recovery: `agent/16_recovery_playbooks/cmake_recovery.md`
