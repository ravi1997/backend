# Checklist: Performance Regression Evidence

**Purpose:** Collect diagnostic evidence for performance issues
**When to use:** When application is slow, has high latency, or resource exhaustion
**Prerequisites:** Access to application, database, and monitoring tools
**Estimated time:** 10-15 minutes

---

## CRITICAL: Collect ALL Evidence Before Fixing

Do NOT skip any section. Incomplete evidence leads to wrong diagnosis.

---

## Section A: Baseline Metrics

### Commands to Run
```bash
# 1. Response time test
time curl -I https://myapp.com/api/endpoint

# 2. Multiple requests
for i in {1..10}; do time curl -s -o /dev/null https://myapp.com/api/endpoint; done

# 3. Load test (if ab available)
ab -n 100 -c 10 https://myapp.com/api/endpoint
```

### Expected Information
- [ ] Average response time
- [ ] Min/max response time
- [ ] Requests per second
- [ ] Error rate

### Performance Benchmarks
- Good: < 100ms
- Acceptable: 100-500ms
- Slow: 500ms-2s
- Very slow: > 2s

---

## Section B: Application Metrics

### Commands to Run
```bash
# 1. CPU usage
top -b -n 1 | grep python
# OR
ps aux | grep python | awk '{print $3}'

# 2. Memory usage
free -h
ps aux | grep python | awk '{print $4, $6}'

# 3. Process count
ps aux | grep python | wc -l

# 4. Open connections
ss -s
netstat -an | grep ESTABLISHED | wc -l
```

### Expected Information
- [ ] CPU usage percentage
- [ ] Memory usage (MB and %)
- [ ] Number of worker processes
- [ ] Number of open connections

### Red Flags
- ❌ CPU > 80% sustained
- ❌ Memory > 90%
- ❌ Too many processes
- ❌ Connection pool exhausted

---

## Section C: Database Performance

### Commands to Run
```bash
# PostgreSQL
psql mydb << EOF
-- Slow queries
SELECT query, calls, mean_exec_time, max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Active queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Missing indexes
SELECT schemaname, tablename, attname
FROM pg_stats
WHERE n_distinct > 100 AND correlation < 0.1;
EOF
```

### Expected Information
- [ ] Slowest queries documented
- [ ] Query execution times
- [ ] Active/blocked queries
- [ ] Table sizes
- [ ] Missing indexes identified

### Red Flags
- ❌ Queries taking > 1s
- ❌ Sequential scans on large tables
- ❌ Missing indexes on frequently queried columns
- ❌ Blocked queries
- ❌ Lock waits

---

## Section D: Application Profiling

### Commands to Run
```bash
# Python profiling (add to code temporarily)
python -m cProfile -o profile.stats app.py

# Analyze profile
python -m pstats profile.stats
# Then: sort cumulative, stats 20

# OR use py-spy (if installed)
sudo py-spy top --pid $(pgrep -f python)
sudo py-spy record -o profile.svg --pid $(pgrep -f python) --duration 30
```

### Expected Information
- [ ] Hottest functions identified
- [ ] Time spent in each function
- [ ] Call counts
- [ ] Cumulative time

### Red Flags
- ❌ Single function taking > 50% time
- ❌ Excessive function calls (N+1 pattern)
- ❌ Blocking I/O in hot path
- ❌ Inefficient algorithms (O(n²))

---

## Section E: Network and I/O

### Commands to Run
```bash
# 1. Network latency
ping -c 10 database-host
ping -c 10 api-endpoint

# 2. Disk I/O
iostat -x 1 5

# 3. Network throughput
iftop -t -s 10
# OR
nethogs

# 4. Open files
lsof -p $(pgrep -f python) | wc -l
```

### Expected Information
- [ ] Network latency to dependencies
- [ ] Disk I/O wait times
- [ ] Network bandwidth usage
- [ ] Number of open files

### Red Flags
- ❌ High network latency (> 100ms)
- ❌ Disk I/O wait > 10%
- ❌ Network saturation
- ❌ Too many open files

---

## Section F: Code Analysis

### Commands to Run
```bash
# 1. Check for N+1 queries (in logs)
grep "SELECT" app.log | wc -l

# 2. Check for missing eager loading
grep -r "lazy='select'" app/models/

# 3. Check for inefficient loops
grep -r "for.*in.*query" app/

# 4. Check for missing caching
grep -r "@cache" app/ | wc -l
```

### Expected Information
- [ ] Number of queries per request
- [ ] Use of eager loading
- [ ] Caching strategy
- [ ] Algorithm complexity

### Common Performance Issues
- N+1 queries (query in loop)
- Missing database indexes
- No caching
- Inefficient algorithms
- Blocking I/O
- Large result sets

---

## Section G: Recent Changes

### Questions to Answer
- [ ] When did performance degrade?
- [ ] What changed recently?
  - Code deployment?
  - Database migration?
  - Traffic increase?
  - Data growth?
- [ ] Is it affecting all requests or specific endpoints?
- [ ] Is it constant or intermittent?

---

## Section H: Common Root Causes Checklist

Based on evidence, check which applies:

- [ ] **N+1 queries** (many queries in loop)
- [ ] **Missing index** (sequential scan on large table)
- [ ] **Slow query** (complex join or aggregation)
- [ ] **No caching** (repeated expensive operations)
- [ ] **Memory leak** (memory usage growing)
- [ ] **CPU bottleneck** (inefficient algorithm)
- [ ] **I/O bottleneck** (slow disk or network)
- [ ] **Connection pool exhausted** (too many connections)
- [ ] **Large result set** (returning too much data)
- [ ] **Blocking operation** (synchronous I/O in async context)

---

## Output Summary

After collecting all evidence, write a 10-line summary:

```
DIAGNOSIS SUMMARY
=================
Symptom: [slow response / high CPU / high memory]
Affected: [all requests / specific endpoint]
Baseline: [Xms before, Yms now]

Root Cause (most likely): [specific cause]
Evidence: [key evidence]
Bottleneck: [database / application / network]

Recommended Fix: [specific action]
Expected Improvement: [X% faster]
Risk Level: [low/medium/high]
```

---

## Validation

Before proceeding to fix:
- [ ] All sections A-H completed
- [ ] Bottleneck identified
- [ ] Evidence supports diagnosis
- [ ] Fix is clear
- [ ] Expected improvement estimated

**If any checkbox is unchecked → Collect more evidence.**

---

## See Also

- [`../workflows/performance_profiling.md`](../workflows/performance_profiling.md) - Profiling workflow
- [`../workflows/performance.md`](../workflows/performance.md) - Optimization workflow
