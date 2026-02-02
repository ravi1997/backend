# CMake Diagnostics Bundle

- Show generator/cache: `grep CMAKE_GENERATOR build/CMakeCache.txt` (adjust path) and `cmake -LA -N build | head`.
- Clean configure: `cmake -S . -B build-diag -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`.
- Dependency search: `cmake --find-package -DNAME=<Pkg> -DMODE=EXIST -DCMAKE_PREFIX_PATH="$CMAKE_PREFIX_PATH"`.
- Trace configure: `cmake -S . -B build-diag --trace-expand --warn-uninitialized` (short runs only).
- Inspect FetchContent: `rg "FetchContent_" CMakeLists.txt cmake`.
- Graph deps: `cmake --graphviz=deps.dot build-diag && dot -Tpng deps.dot -o deps.png` (optional if dot available).
- Install dry-run: `cmake --install build-diag --prefix /tmp/cmake-diag --component default --dry-run`.
- Cross/Toolchain: print `CMAKE_TOOLCHAIN_FILE`, `CMAKE_SYSROOT`, `CMAKE_FIND_ROOT_PATH_MODE_*` from cache.
