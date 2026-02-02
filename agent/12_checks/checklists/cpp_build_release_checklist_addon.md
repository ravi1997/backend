# C++ Build & Release Checklist (Add-On)

- Confirm compiler/stdlib baseline pinned (GCC/Clang version, `CMAKE_CXX_STANDARD` set, `-stdlib` consistent).
- Build matrix covers C++17/20/23 (where claimed) with ASAN/UBSAN and at least one TSAN job.
- LTO/`-march` settings validated against target hardware; avoid `-march=native` for release artifacts.
- Packaging test passes: `cmake --install <build> --prefix <staging>` and binaries run on clean env.
- RPATH/SONAME verified; avoid ABI changes without version bump.
- Link interfaces audited: public targets export includes and PUBLIC deps; no manual `-l` strings.
- Security flags: `-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`, `-fPIE -pie` for executables where applicable.
