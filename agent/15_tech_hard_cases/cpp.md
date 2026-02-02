# C++ (17/20/23) Hard Cases & Failure Scenarios

Use Issue-Key format `Issue-Key: CPP-<hash>`. Suggested prompt: `prompts/hard_cases/cpp_hard_cases.txt`.

## Toolchain & Stdlib

### HC-CPP-001: GCC vs Clang Mismatch
**Symptom:**
```
error: unknown warning option '-Wextra'
```
**Likely Causes:** mixed compiler flags between GCC/Clang.
**Fast Diagnosis:** `c++ --version`; inspect build logs for compiler id.
**Fix Steps:** align toolchain in CMake `set(CMAKE_CXX_COMPILER clang++)` or GCC; adjust flags accordingly.
**Prevention:** pin compiler in CI; share `compile_commands.json` from same compiler.

### HC-CPP-002: Stdlib Mismatch (libstdc++ vs libc++)
**Symptom:**
```
undefined reference to `std::__1::basic_string`
```
**Likely Causes:** linking Clang-compiled objects (libc++) with GCC defaults (libstdc++).
**Fast Diagnosis:** `strings libfoo.a | head`; check `-stdlib` flag.
**Fix Steps:** compile all TU with same `-stdlib=libc++` or `-lstdc++`; rebuild deps.
**Prevention:** enforce consistent toolchain config in CMake toolchain file.

### HC-CPP-003: Missing -std=c++XX Flag
**Symptom:**
```
error: 'optional' is not a member of 'std'
```
**Likely Causes:** default C++98 mode.
**Fast Diagnosis:** inspect compiler invocation for `-std`.
**Fix Steps:** set `set(CMAKE_CXX_STANDARD 20)` and `CXX_STANDARD_REQUIRED ON`.
**Prevention:** add configure gate that fails without CXX standard set.

### HC-CPP-004: Wrong ABI (GLIBCXX)
**Symptom:**
```
GLIBCXX_3.4.26 not found
```
**Likely Causes:** binary built on newer libstdc++ than runtime.
**Fast Diagnosis:** `strings libstdc++.so | grep GLIBCXX`; `ldd` on binary.
**Fix Steps:** build on oldest supported distro or static link libstdc++ where allowed.
**Prevention:** use containerized toolchain matching prod baseline.

### HC-CPP-005: Architecture/ISA Mismatch
**Symptom:**
```
illegal instruction (core dumped)
```
**Likely Causes:** built with `-march=native` on newer CPU than target.
**Fast Diagnosis:** `objdump -d binary | head`; check `-march` flag.
**Fix Steps:** compile with conservative `-march=x86-64-v2` or target baseline.
**Prevention:** define portable `CMAKE_CXX_FLAGS_RELEASE` with safe ISA.

## Build System & Linking

### HC-CPP-006: Undefined Reference to Symbol
**Symptom:**
```
undefined reference to `foo()`
```
**Likely Causes:** missing object/library in link; wrong order of libs.
**Fast Diagnosis:** `nm -C libfoo.a | grep foo`; check link command order.
**Fix Steps:** add target_link_libraries with correct scope and ordering; rebuild static libs.
**Prevention:** use CMake target-based linking, avoid manual `LDFLAGS` strings.

### HC-CPP-007: ODR Violation / Multiple Definition
**Symptom:**
```
multiple definition of `MyClass::value`
```
**Likely Causes:** non-inline variables defined in headers; duplicated objects.
**Fast Diagnosis:** `nm -C *.o | grep MyClass::value`; search for definitions.
**Fix Steps:** move definitions to single TU or mark inline/constexpr.
**Prevention:** header-only pieces must use `inline` for globals; enforce IWYU.

### HC-CPP-008: Missing Include Directories
**Symptom:**
```
fatal error: mylib/api.h: No such file or directory
```
**Likely Causes:** include path not exported or incorrect relative include.
**Fast Diagnosis:** inspect compile command; `rg "api.h"`.
**Fix Steps:** add `target_include_directories(<tgt> PUBLIC include)`; fix include paths.
**Prevention:** use interface targets exporting include dirs.

### HC-CPP-009: Transitive Dependency Not Linked
**Symptom:**
```
undefined reference to `sqlite3_open`
```
**Likely Causes:** dependency of dependency not linked due to PRIVATE scope.
**Fast Diagnosis:** `cmake --graphviz=deps.dot` or `ldd binary`.
**Fix Steps:** mark dependency as PUBLIC/INTERFACE in `target_link_libraries`.
**Prevention:** audit link interfaces; add link tests.

### HC-CPP-010: Build Dir/Cache Stale
**Symptom:** weird compiler errors disappearing after clean.
**Likely Causes:** stale CMake cache or switching generators.
**Fast Diagnosis:** check `CMakeCache.txt` timestamps; generator type.
**Fix Steps:** remove build dir, rerun CMake with correct generator/toolchain.
**Prevention:** scripted clean when switching generators; set `-B build-<gen>` per generator.

### HC-CPP-011: LTO/ThinLTO Link Failures
**Symptom:**
```
undefined reference during LTO link
```
**Likely Causes:** mixing non-LTO libs; incompatible ar/ranlib.
**Fast Diagnosis:** `nm -o libfoo.a | head`; check `-flto` presence.
**Fix Steps:** disable LTO for incompatible libs or rebuild them with LTO; use gold/ld.lld.
**Prevention:** gate LTO to Release builds with compatible toolchain only.

### HC-CPP-012: CMake Target Export/Install Broken
**Symptom:**
```
CMake Error: install(EXPORT ...) references target not built
```
**Likely Causes:** missing install rules or incorrect export set.
**Fast Diagnosis:** inspect `install(TARGETS ...)` blocks; `cmake --install . --component` dry run.
**Fix Steps:** add install rules for all public targets; ensure same export set name.
**Prevention:** test `cmake --install` in CI; provide package config tests.

## Language Standard Pitfalls

### HC-CPP-013: std::filesystem Link Errors
**Symptom:**
```
undefined reference to `std::filesystem::path::...`
```
**Likely Causes:** missing `-lstdc++fs` on older GCC; wrong C++ version.
**Fast Diagnosis:** check compiler version; link line for `-lstdc++fs`.
**Fix Steps:** add `target_link_libraries(foo PRIVATE stdc++fs)` for GCC < 9; ensure C++17 enabled.
**Prevention:** require GCC>=9 or Clang>=9 for filesystem; add configure check.

### HC-CPP-014: Coroutine Compilation Errors (C++20)
**Symptom:**
```
error: 'std::coroutine_traits' is not a class template
```
**Likely Causes:** missing `<coroutine>` include; compiler lacking coroutine TS.
**Fast Diagnosis:** `c++ --version`; confirm `-std=c++20` present.
**Fix Steps:** include `<coroutine>`; upgrade compiler; use `-fcoroutines` if required.
**Prevention:** CI matrix covers coroutine builds; guard coroutine code with feature detection.

### HC-CPP-015: Modules Experimental Failures
**Symptom:**
```
error: module interface unit is unsupported
```
**Likely Causes:** compiler not built with modules; build system missing BMI handling.
**Fast Diagnosis:** check compiler support (`c++ -fmodules-ts --version`); inspect CMake module rules.
**Fix Steps:** disable modules on unsupported compilers; use `CMAKE_EXPERIMENTAL_CXX_MODULE_CMAKE_API` properly; ensure BMI directory unique per config.
**Prevention:** keep modules opt-in; document compiler versions tested.

### HC-CPP-016: Constexpr Differences Across Standards
**Symptom:**
```
constexpr variable not usable in switch case under C++17
```
**Likely Causes:** code assumes C++20 constexpr rules.
**Fast Diagnosis:** check `CMAKE_CXX_STANDARD`; compile under C++17 to reproduce.
**Fix Steps:** adjust constexpr usage; add `constexpr` constructors or move to `constexpr if` patterns.
**Prevention:** run CI across C++17/20/23 profiles.

## Runtime & Sanitizers

### HC-CPP-017: Dangling Reference/Use-After-Free
**Symptom:**
```
ASAN: heap-use-after-free
```
**Likely Causes:** returning references to temporaries; container invalidation.
**Fast Diagnosis:** run with `-fsanitize=address -g`; check stack trace.
**Fix Steps:** fix ownership semantics; use smart pointers or value semantics; add lifetimes tests.
**Prevention:** enable ASAN/UBSAN in CI; code review checklist for ownership.

### HC-CPP-018: Data Race (TSAN)
**Symptom:**
```
WARNING: ThreadSanitizer: data race
```
**Likely Causes:** unsynchronized shared state; missing mutex/atomics.
**Fast Diagnosis:** run with `-fsanitize=thread`; inspect trace.
**Fix Steps:** add proper synchronization; avoid shared mutable globals.
**Prevention:** TSAN jobs in CI; prefer immutable data structures.

### HC-CPP-019: UB from Uninitialized Memory
**Symptom:**
```
==UBSAN== uninitialized value
```
**Likely Causes:** missing initialization, misuse of memcpy, placement new without ctor.
**Fast Diagnosis:** UBSAN/valgrind memcheck.
**Fix Steps:** initialize aggregates; replace raw arrays with std::array/vector; fix memcpy sizes.
**Prevention:** static analyzers (clang-tidy) with `cppcoreguidelines-init-variables`.

### HC-CPP-020: Segfault in Release Only
**Symptom:**
```
Segmentation fault in optimized build
```
**Likely Causes:** undefined behavior masked in Debug; iterator invalidation; missing virtual destructor.
**Fast Diagnosis:** enable `-fno-omit-frame-pointer`; run under ASAN/UBSAN on Release with `-O2 -g`.
**Fix Steps:** fix UB; add tests covering release code paths; ensure polymorphic bases have virtual destructors.
**Prevention:** run sanitizers regularly even for Release flags.

## Packaging & Deployment

### HC-CPP-021: RPATH Missing
**Symptom:**
```
error while loading shared libraries: libfoo.so: cannot open shared object file
```
**Likely Causes:** installed binaries cannot find shared libs.
**Fast Diagnosis:** `ldd bin/app`; inspect `readelf -d bin/app | grep RPATH`.
**Fix Steps:** set `INSTALL_RPATH` or use `RUNPATH` pointing to lib dir; consider static linking where allowed.
**Prevention:** packaging test that runs installed binaries on clean env.

### HC-CPP-022: Install Rules Missing Headers
**Symptom:** users cannot include headers from installed package.
**Likely Causes:** headers not installed/exported.
**Fast Diagnosis:** check `install(DIRECTORY include/ DESTINATION include)` presence.
**Fix Steps:** add install commands; export targets with proper include dirs.
**Prevention:** add packaging CI job verifying installed tree.

### HC-CPP-023: ABI Breakage Across Versions
**Symptom:** runtime crashes mixing old/new libraries.
**Likely Causes:** changed class layout without SONAME bump.
**Fast Diagnosis:** `readelf -Ws libfoo.so | sha1sum`; compare SONAME.
**Fix Steps:** bump SONAME; provide upgrade notes; avoid inline ABI changes in patch releases.
**Prevention:** ABI compliance checker in CI; semantic versioning for libraries.

### HC-CPP-024: Static vs Shared Mismatch
**Symptom:** duplicate symbols or missing exported symbols depending on build type.
**Likely Causes:** toggling BUILD_SHARED_LIBS without consistent export macros.
**Fast Diagnosis:** check `BUILD_SHARED_LIBS` and symbol visibility macros.
**Fix Steps:** use `-fvisibility=hidden` + explicit export macros; rebuild all deps with consistent setting.
**Prevention:** fix build type in toolchain; provide both targets separately.

## Testing & Tooling

### HC-CPP-025: gtest Discovery Issues
**Symptom:**
```
[==========] Running 0 tests
```
**Likely Causes:** tests not linked with gtest_main; wrong TEST macro; filtering excludes tests.
**Fast Diagnosis:** check test binary symbols `nm -C test_binary | grep TEST`; run with `--gtest_list_tests`.
**Fix Steps:** link `gtest_main`; ensure TEST names correct; remove overly broad filters.
**Prevention:** CI step listing tests; template test target linking gtest_main by default.

### HC-CPP-026: Coverage Tools Failing with Templates
**Symptom:** coverage missing templated code.
**Likely Causes:** templates header-only not instantiated in tested TU.
**Fast Diagnosis:** check object files include template instantiation; coverage report excludes headers.
**Fix Steps:** add explicit instantiations or tests in TU; configure coverage to include headers.
**Prevention:** require minimal explicit instantiation for template-heavy libs.

## Performance

### HC-CPP-027: Excessive Copies, Missing Move
**Symptom:** high CPU/memory, perf drop after refactor.
**Likely Causes:** pass-by-value, missing move constructors.
**Fast Diagnosis:** enable `-fno-elide-constructors` in debug; inspect profiler for copy ctor hotspots.
**Fix Steps:** add `std::move`, emplace, use `std::string_view`; implement move constructors.
**Prevention:** clang-tidy `performance-*` checks; benchmarks in CI.

### HC-CPP-028: NRVO Disabled by Build Flags
**Symptom:** extra copies in Release unexpectedly.
**Likely Causes:** `-fno-elide-constructors` or debug flags in Release.
**Fast Diagnosis:** inspect compile flags; compiler optimization report.
**Fix Steps:** remove anti-NRVO flags; rely on `-O2` or `-O3`.
**Prevention:** enforce flag baseline via toolchain file.

### HC-CPP-029: Oversized Binary from Debug Symbols
**Symptom:** release artifacts huge.
**Likely Causes:** shipping with debug symbols or static linking all deps.
**Fast Diagnosis:** `du -h build/bin/app`; `readelf -S app | grep debug`.
**Fix Steps:** strip binaries (`-s` or `llvm-strip`); split debug symbols; use shared libs where acceptable.
**Prevention:** release packaging step strips and archives debug symbols separately.

## Security

### HC-CPP-030: Unsafe printf/format Strings
**Symptom:**
```
format string contains '%n'
```
**Likely Causes:** user-controlled format strings; mixing fmt/printf.
**Fast Diagnosis:** clang-tidy `security.insecureAPI.printf`; grep for `printf(` with user data.
**Fix Steps:** use `fmt::format` with format string literals; sanitize user input; enable `-Wformat -Werror`.
**Prevention:** static analysis gate; forbid `%n` usage via lint.

### HC-CPP-031: Integer Overflow in Bounds
**Symptom:**
```
UBSAN: signed integer overflow
```
**Likely Causes:** unchecked arithmetic for sizes/indexing.
**Fast Diagnosis:** UBSAN; review code for unbounded multiplication of sizes.
**Fix Steps:** use `std::size_t`, checked arithmetic, saturating helpers.
**Prevention:** enable `-ftrapv` or sanitizer builds; code review checklist item.

### HC-CPP-032: Lifetime Bugs with raw pointers
**Symptom:** crashes after container reallocation when storing raw pointers.
**Likely Causes:** storing pointers to vector elements that move.
**Fast Diagnosis:** enable ASAN; code review for raw pointer caches.
**Fix Steps:** store indices or iterators that remain valid; use smart pointers/owners.
**Prevention:** prefer `std::span`/`std::reference_wrapper`; forbid long-lived raw pointers in policy.

## Issue-Key and Prompt Mapping

- Example Issue-Key: `Issue-Key: CPP-12ab9c`
- Use prompt: `prompts/hard_cases/cpp_hard_cases.txt`
