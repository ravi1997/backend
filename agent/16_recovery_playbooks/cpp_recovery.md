# C++ Recovery Playbook

Map errors to `HC-CPP-XXX`. Use Issue-Key `Issue-Key: CPP-<hash>` in notes.

## RECOVERY-CPP-001: Toolchain/Stdlib Alignment
- When: compiler flag errors, std::filesystem link errors, ABI/ISA mismatches.
- Steps: verify compiler with `c++ --version`; set `CMAKE_CXX_STANDARD` and toolchain file; rebuild deps with matching `-stdlib` and `-march`; avoid mixing GCC/Clang artifacts.
- Validate: clean rebuild succeeds; `ldd` shows expected libstdc++/libc++.

## RECOVERY-CPP-002: Linking Failures
- When: undefined references, multiple definitions, transitive deps missing.
- Steps: inspect link line; ensure target_link_libraries scopes PUBLIC/INTERFACE; check order; remove duplicate definitions; add missing libs (stdc++fs, pthread, dl) per hard case.
- Validate: link completes; nm/ldd show correct symbols.

## RECOVERY-CPP-003: CMake/Build Cache Problems
- When: generator mismatch, stale cache, install/export errors.
- Steps: remove build dir; rerun `cmake -S . -B build -G Ninja` (or intended generator) with toolchain; regenerate compile_commands; fix install/export blocks.
- Validate: configure + build + `cmake --install build --prefix /tmp/pkg` succeeds.

## RECOVERY-CPP-004: Runtime UB/Crashes
- When: ASAN/UBSAN/TSAN findings, segfault in Release.
- Steps: rebuild with `-g -O1 -fsanitize=address,undefined` (or thread); reproduce and read stack; fix ownership/race; add tests; consider `-fno-omit-frame-pointer` for perf builds.
- Validate: sanitizer run clean; release build runs without crash.

## RECOVERY-CPP-005: Performance Regressions
- When: excessive copies, NRVO disabled, oversized binaries.
- Steps: profile (perf/VTune); check copy/move counts; add `std::move`, `string_view`, reserve/emplace; ensure no `-fno-elide-constructors`; strip binaries or split debug symbols.
- Validate: benchmark target meets baseline; binary size within budget.

## RECOVERY-CPP-006: Security Findings
- When: unsafe format strings, integer overflow, lifetime bugs.
- Steps: run clang-tidy security/performance checks; enable `-Wformat -Werror` and UBSAN; replace printf with fmt; add bounds checks; refactor ownership to smart pointers/spans.
- Validate: static analysis clean; sanitizer runs clean.
