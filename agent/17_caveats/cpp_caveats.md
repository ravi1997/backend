# C++ Caveats & Footguns

Issue-Key example: `Issue-Key: CPP-a1b2c3`.

## Toolchain
- Mixing GCC/Clang artifacts silently causes ABI/stdlib mismatches—pin compiler per project and cache container images.
- `-march=native` breaks on older CPUs; set explicit baseline ISA.
- Missing `CMAKE_CXX_STANDARD` defaults to C++98 on some toolchains—always require standard.

## Build System
- Avoid manual `CMAKE_CXX_FLAGS` concatenation; prefer target properties and generator expressions.
- Link interface scope matters: dependencies needed by consumers must be PUBLIC/INTERFACE.
- Re-run CMake after switching generators; caches do not translate across Make/Ninja.

## Language/Stdlib
- `std::filesystem` requires linking tweaks on GCC<9; guard with feature tests.
- Coroutines/modules are compiler-version sensitive; keep them opt-in and tested.
- constexpr rules differ between C++17/20/23; validate across standards if you claim multi-standard support.

## Runtime/Sanitizers
- Sanitizers change ABI; avoid mixing sanitized and non-sanitized objects.
- TSAN on libc++ vs libstdc++ may differ; align stdlib and compiler when reading reports.

## Security/Quality
- Enforce `-Werror` selectively; allow opt-out for third-party code to reduce noise.
- Use `-fvisibility=hidden` with explicit exports to avoid accidental ABI surface.
- Prefer fmt/{fmt} over printf-style logging; forbid user-controlled format strings.
