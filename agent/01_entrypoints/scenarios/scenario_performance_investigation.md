# Scenario: Performance Degradation Investigation

## Purpose

Diagnosing and resolving performance issues (slow response times, high memory usage, CPU spikes).

## Inputs

- Performance complaint or metric alert (e.g., "API response time > 2s").
- Access to profiling tools and logs.

## Measurement Phase (Adopt `profile_tester.md`)

1. **Baseline Capture**: Record current performance metrics:
   - Response time (p50, p95, p99).
   - Memory usage (heap, stack).
   - CPU utilization.
   - Database query times.
2. **Reproduction**: Create a load test that consistently triggers the slow behavior.
3. **Profiling**: Run the application with profiling enabled (e.g., `py-spy`, `node --prof`, `perf`).

## Analysis Phase (Adopt `profile_implementer.md`)

1. **Hotspot Identification**: Identify the top 3 functions consuming the most time/memory.
2. **Query Analysis**: Check for N+1 queries, missing indexes, or full table scans.
3. **Algorithm Review**: Look for O(n²) or worse complexity in critical paths.
4. **Resource Leaks**: Check for unclosed connections, memory leaks, or infinite loops.

## Optimization Phase (Adopt `profile_architect.md`)

1. **Quick Wins**:
   - Add database indexes.
   - Cache frequently accessed data.
   - Use connection pooling.
2. **Algorithmic Improvements**: Replace inefficient algorithms with better ones.
3. **Architectural Changes**: Consider:
   - Moving heavy computation to background jobs.
   - Implementing pagination for large datasets.
   - Using CDN for static assets.

## Verification Phase (Adopt `profile_tester.md`)

1. **Load Testing**: Re-run the load test and compare metrics to baseline.
2. **Regression Check**: Ensure optimizations didn't break functionality.
3. **Documentation**: Update `plans/Architecture/PERFORMANCE_NOTES.md` with findings.

## STOP Condition

- Performance meets the targets defined in `plans/SRS/non_functional_reqs.md`.
- Optimizations are documented and no regressions exist.

## Related Files

- `plans/SRS/non_functional_reqs.md`
- `agent/06_skills/testing/skill_discover_edge_cases.md`
