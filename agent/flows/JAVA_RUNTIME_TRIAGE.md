# FLOW: Java Runtime & JVM Triage

**Purpose:** Route Java runtime issues to the correct debugging or optimization path.
**Source:** `flows/JAVA_RUNTIME_TRIAGE.md`

```mermaid
graph TD
    Start[Runtime Issue Detected] --> Type{Issue Category}
    
    Type -->|Exception / Crash| Exception[Analyze Stacktrace]
    Type -->|Memory / OOM| OOM[Analyze Heap]
    Type -->|Slow Performance| Perf[Analyze CPU/Threads]
    
    Exception --> LogCheck[Check App Logs / Sentry]
    LogCheck --> Fix[Propose Fix]
    
    OOM --> HeapDump{Heap Dump exists?}
    HeapDump -->|Yes| MAT[Analyze with MAT/VisualVM]
    HeapDump -->|No| EnableDump[Enable -XX:+HeapDumpOnOutOfMemoryError]
    
    Perf --> Profiler[Run JProfiler / Async Profiler]
    Profiler --> Hotspot[Identify Busy Threads]
    
    MAT --> Leak[Identify Memory Leak]
    Hotspot --> Optimization[Propose Optimization]
    
    Leak --> Fix
    Optimization --> Fix
```

## 1. Exception Triage
1. **Root Cause:** Find the bottom-most `Caused by:` in the stack trace.
2. **Context:** Identify the failing component (Spring Bean, Hibernate Query, etc.).
3. **Reproducer:** Write a failing `@Test` case.

## 2. JVM Memory Triage
1. **GC Logs:** Check for frequent full GCs.
2. **Heap Histogram:** `jmap -histo:live <pid>`.
3. **Leak Identification:** Look for static collections or unclosed resources (Streams, Connections).

## 3. Performance Triage
1. **Thread Dump:** `jstack <pid>` to find deadlocks or blocked threads.
2. **Sampling:** Use `jvisualvm` or `jconsole` for real-time monitoring.

## 4. Metadata
- `TRIAGE_TYPE`: RUNTIME
- `PLATFORM`: JVM
- `TOOLS`: [JVisualVM, JConsole, JStack, JMap]
