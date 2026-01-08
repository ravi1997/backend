# Subflow: C++ Feature Delivery

**Stack:** C++
**Parent:** `../feature_delivery.md`

## Build & Test

```bash
# Configure
cmake -S . -B build

# Build
cmake --build build

# Test
ctest --test-dir build --output-on-failure
```

## Linting

```bash
# Formatter
clang-format -i **/*.cpp **/*.h

# Linter
clang-tidy **/*.cpp -- -Iinclude
```

## Missing Environment

If the environment cannot run tests (e.g. valid cross-compile toolchain missing):
1. **Reproduce:** Document setup in `REPRODUCE.md`.
2. **Minimal Test:** Create a script to run available tests.
3. **Confidence:** Downgrade confidence until verified on target.

## Role Checklist: Tester

**Reference:** `agent/stacks/packs/cpp/TESTING.md`

- [ ] **Build:** Passes with `-Wall -Werror` (or equivalent).
- [ ] **Unit Tests:** GTest/Catch2 pass (100%).
- [ ] **Memory:** Sanitizers (ASan/TSan) run clean.
- [ ] **Leaks:** Valgrind check (if applicable).
