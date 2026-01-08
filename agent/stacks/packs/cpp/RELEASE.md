# C++ Release & Packaging

## Packaging Formats
- **Tarball/Zip**: Simplified distribution (source or binary).
- **DEB/RPM**: Linux system packages.
- **Docker**: Containerized application.
- **Conan/Vcpkg**: Library distribution.

## Release Checklist
- [ ] Build in Release mode (`cmake -DCMAKE_BUILD_TYPE=Release`).
- [ ] Strip symbols from executables (or keep debug symbols separate).
- [ ] Run full test suite.
- [ ] Verify shared library dependencies (`ldd` on Linux).
- [ ] Generate documentation (Doxygen).

## CPack Example
```cmake
# CMakeLists.txt
include(CPack)
```
Then run:
```bash
cpack -G DEB
```
