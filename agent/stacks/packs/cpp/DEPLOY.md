# C++ Deployment Guide

## Build Strategy

C++ requires compilation for the specific target architecture and OS.

## Static vs Dynamic Linking

- **Static**: Larger binary, no dependency issues.
- **Dynamic**: Smaller binary, requires shared libraries (`.so`, `.dll`) on target.

## Build Wrapper (CMake)

```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
make install
```

## Docker Deployment

See `agent/snippets/cpp/Dockerfile.md`.

- Use **Multi-stage builds** to keep compiler tools out of runtime image.

## Runtime Dependencies

If dynamically linked, verify libraries with `ldd ./my_app`.
Install missing system libraries in the runtime environment.
