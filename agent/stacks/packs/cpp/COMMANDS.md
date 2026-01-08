# C++ Command Map

## Toolchain Selection Rules
1. **CMakePresets.json**: If exists, use `cmake --preset`.
2. **toolchain.cmake**: If exists, use `-DCMAKE_TOOLCHAIN_FILE=...`.
3. **Default**: GCC, then Clang if installed.

## Canonical Commands

### Build
**CMake (Recommended)**
```bash
cmake -S . -B build -G Ninja  # Configuration
cmake --build build           # Compilation
```

**Make**
```bash
make -j$(nproc)
```

### Test
**CTest**
```bash
cd build && ctest --output-on-failure
```

**GoogleTest**
```bash
./build/tests/my_test_executable
```

### Lint/Format
**Clang-Format**
```bash
find . -name "*.cpp" -o -name "*.h" | xargs clang-format -i
```

**Clang-Tidy**
```bash
clang-tidy src/*.cpp -- -Iinclude
```

### Run
**Executable**
```bash
./build/bin/my_app
```

### Package
**CPack**
```bash
cd build && cpack -G TGZ
```

### CI
**GitHub Actions (Example)**
```yaml
- run: cmake -S . -B build && cmake --build build
- run: cd build && ctest
```
