# C++ Gate: Build

## Purpose

Ensure the C++ project compiles without errors or critical warnings.

## Rules

1. **Toolchain**: Must use `cmake` (standard) or `make` if legacy.
2. **Compiler Flags**: `-Wall -Wextra` are minimum required. `-Werror` recommended.
3. **Clean Build**: Build must succeed from a clean state (no artifacts).

## Check Command

```bash
mkdir -p build && cd build
cmake ..
make -j$(nproc)
```

## Failure criteria

- Compiler error (Exit code != 0).
- Linker error.
