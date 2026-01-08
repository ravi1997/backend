# C++ Troubleshooting

## Common Issues

### Linker Errors (Undefined Reference)
- **Symptom**: `undefined reference to 'Symbol'`
- **Fix**: Check if the library is linked (`target_link_libraries`), if the function is implemented, or if there's a name mangling issue (extern "C").

### Segmentation Faults
- **Symptom**: Program crashes with SIGSEGV.
- **Fix**: Use a debugger (GDB/LLDB) or AddressSanitizer (`-fsanitize=address`) to find out-of-bounds access or use-after-free.

### Header Dependency Cycles
- **Symptom**: Compiler errors about incomplete types.
- **Fix**: Use forward declarations where possible; include headers only in `.cpp` files if full definition isn't needed in header.

### CMake Configuration Failures
- **Symptom**: `Could not find ...`
- **Fix**: Verify paths in `CMakeLists.txt`, check `CMAKE_PREFIX_PATH`, or ensure dependencies are installed.
