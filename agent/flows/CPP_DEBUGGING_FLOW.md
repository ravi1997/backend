# FLOW: C++ Debugging Decision Tree

**Purpose:** Route C++ runtime issues to the correct triaging strategy.
**Source:** `flows/CPP_DEBUGGING_FLOW.md`

```mermaid
graph TD
    Start[Runtime Issue Detected] --> Type{Issue Category}
    
    Type -->|Crash / Segfault| Segfault[Triage Crash]
    Type -->|Hang / Infinite Loop| Hang[Triage Performance]
    Type -->|Logic Error / Incorrect Output| Logic[Triage Logic]
    
    Segfault --> CoreDump{Core Dump exists?}
    CoreDump -->|Yes| GDB[Run GDB on Core]
    CoreDump -->|No| ASAN[Rebuild with AddressSanitizer]
    
    GDB --> Backtrace[Identify Faulty Function]
    ASAN --> MemError[Locate Memory Violation]
    
    Hang --> Profiler[Run profiler/perf/valgrind]
    Profiler --> Bottleneck[Locate Hot Path]
    
    Logic --> UnitTests[Run specific Test Suite]
    UnitTests --> Logging[Enable Debug Logs]
    
    MemError --> Fix[Propose Fix]
    Backtrace --> Fix
    Bottleneck --> Optimization[Propose Optimization]
    Logging --> Analysis[Analyze Execution Trace]
    Analysis --> Fix
```

## 1. Crash Triage (SIGSEGV, SIGABRT)
1. **Identify signal:** Was it a `Segmentation Fault` (memory) or `Abort` (assertion/uncaught exception)?
2. **Backtrace:** Use `gdb` or `lldb` to get the stack trace.
3. **Check pointers:** Look for NULL dereference or use-after-free.

## 2. Memory Triage
1. **ASAN:** `set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address")`.
2. **Valgrind:** `valgrind --leak-check=full ./binary`.

## 3. Logic Triage
1. **Reproducer:** Create a minimal test case that fails.
2. **Assertions:** Add `assert()` or `CHECK()` macros to verify invariants.

## 4. Metadata
- `TRIAGE_TYPE`: RUNTIME
- `LANGUAGE`: CPP
- `TOOLS`: [GDB, LLDB, ASAN, VALGRIND]
