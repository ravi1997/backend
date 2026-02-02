# C++ Diagnostics Bundle

Run when builds/linking/runtime crash.

- Toolchain info: `c++ --version`, `cmake --version`, `ninja --version || make --version`.
- Build flags: inspect `compile_commands.json` for `-std`, `-stdlib`, `-march`.
- Clean configure: `cmake -S . -B build-dbg -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`.
- Linking: `ninja -C build-dbg -v <target>` to capture full link line; `ldd build-dbg/<bin>`.
- Symbols: `nm -C build-dbg/<bin> | head`; `readelf -d build-dbg/<bin> | grep RPATH`.
- Sanitizers: run binary with `ASAN_OPTIONS=detect_leaks=1 UBSAN_OPTIONS=print_stacktrace=1`.
- Packaging: `cmake --install build-dbg --prefix /tmp/pkg && find /tmp/pkg -maxdepth 3 -type f`.
- Performance: `perf record --call-graph=dwarf ./build-dbg/<bin>` (if available) to locate copy hot spots.
