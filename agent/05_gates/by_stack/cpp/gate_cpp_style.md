# C++ Gate: Style

## Purpose

Maintain consistent code formatting and readability.

## Rules

1. **Formatter**: Must satisfy `.clang-format` rules.
2. **Naming**: Variables `snake_case`, Classes `PascalCase`, Constants `UPPER_SNAKE`.
3. **Headers**: Include guards (`#pragma once`) present in all `.h` / `.hpp` files.

## Check Command

```bash
find . -name "*.cpp" -o -name "*.h" | xargs clang-format --dry-run --Werror
```

## Failure criteria

- `clang-format` reports diffs.
- Missing function documentation in headers.
