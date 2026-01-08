# Meta-Workflow: Performance Profiling

**Purpose:** Diagnose and fix performance issues across stacks.
**When to use:** App is slow, high latency, resource exhaustion.
**Prerequisites:** Access to server, profiling tools, stack identified.
**Type:** Universal Meta-Workflow

---

## Workflow Contract

| Attribute | Details |
| :--- | :--- |
| **Inputs** | Baseline metrics, `PROJECT_FINGERPRINT` |
| **Outputs** | Profiling report, Fix PR |
| **Policy** | Do not profile in prod without approval |
| **Stop Conditions** | No reproduceable issue |

---

## Step 0: Context Detection

Identify stack to select the correct profiler.

```bash
cat agent/contracts/PROJECT_FINGERPRINT.md
```

### Profiler Selection

- **Python:** `cProfile` (internal), `py-spy` (external).
- **Java:** `VisualVM`, `JProfiler`, `Java Flight Recorder`.
- **C++:** `gprof`, `Valgrind`, `perf`.
- **Web:** Chrome DevTools, Lighthouse, Web Vitals.

### Decision Trace

> [!NOTE]
> Record the chosen profiler and why.

---

## Step 1: Collect Baseline (Universal)

1.  **Latency:** `curl` timing.
2.  **Resources:** `top`, `docker stats`.
3.  **DB:** Slow query logs.

---

## Step 2: Profile (Stack-Specific)

**Python:**
```bash
py-spy record -o profile.svg --pid <pid>
```

**Java:**
```bash
jcmd <pid> JFR.start duration=60s filename=profile.jfr
```

**C++:**
```bash
perf record -g -p <pid>
```

**Web:**
Run Lighthouse audit in Chrome.

---

## Step 3: Analyze & Fix (Universal)

1.  **Identify:** Find the "hot path" (N+1 queries, tight loops).
2.  **Fix:** Optimize algorithms, add cache, add indexes.
3.  **Verify:** Re-run Step 1 and compare.

---

## Completion Criteria

- ✅ Bottleneck identified
- ✅ Fix applied
- ✅ Performance improved (measurable)
