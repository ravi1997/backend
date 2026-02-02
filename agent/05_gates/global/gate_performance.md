# Gate: Performance

## Purpose

Prevent regressions in latency, memory usage, and load times.

## Explicit Pass/Fail Rubric

| Criterion | Methodology | Pass Threshold | Fail Trigger |
| --- | --- | --- | --- |
| **Response Time** | `lighthouse` / `curl -w "%{time_total}"` | < 200ms (API) | > 500ms spike |
| **Bundle Size** | `source-map-explorer` / `size-limit` | No increase > 5% | Large unoptimized blob |
| **Memory usage** | `heap snapshot` / `ps aux` | Within SRS limits | Memory leak detection |
| **SQL Efficiency** | `EXPLAIN ANALYZE` | No sequential scans | N+1 Query patterns |

## Related Files

- `agent/06_skills/implementation/skill_performance.md`
- `agent/04_workflows/07_testing_and_validation.md`
