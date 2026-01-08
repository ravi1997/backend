# C++ Conventions

## File Structure
- `src/`: Implementation files (.cpp, .cc)
- `include/`: Header files (.h, .hpp)
- `tests/`: Unit and integration tests
- `libs/`: Third-party libraries (if not using a package manager)
- `CMakeLists.txt`: Root build definition

## Naming
- **Classes**: PascalCase
- **Functions/Methods**: camelCase or snake_case (project dependent, consistent)
- **Variables**: snake_case
- **Constants**: SCREAMING_SNAKE_CASE
- **Members**: `m_` prefix or trailing `_` (optional, consistency is key)

## Code Style
- Use `clang-format` with Google or LLVM style by default.
- Header guards: `#pragma once` or standard `#ifndef` guards.
- Prefer `std::unique_ptr` and `std::shared_ptr` over raw pointers.
- Use `auto` where type is deduced and clear.
