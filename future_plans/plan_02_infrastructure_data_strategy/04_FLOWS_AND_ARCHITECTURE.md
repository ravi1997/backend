# System Flows and Architecture
## Plan 2: Infrastructure & Data Strategy

**Version:** 1.0  
**Date:** 2026-01-09  
**Purpose:** Visual representation of system flows and architecture

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Deployment Architecture](#deployment-architecture)
3. [Request Flow](#request-flow)
4. [Task Processing Flow](#task-processing-flow)
5. [AI Processing Flow](#ai-processing-flow)
6. [Analytics Pipeline Flow](#analytics-pipeline-flow)
7. [Failure Recovery Flows](#failure-recovery-flows)
8. [Security Flows](#security-flows)
9. [Monitoring Flow](#monitoring-flow)

---

## Architecture Overview

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        External Users                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       Nginx (Port 80/443)                    │
│  - SSL Termination                                           │
│  - Static File Serving                                       │
│  - Rate Limiting                                             │
│  - Load Balancing                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway (Gunicorn + Flask)                  │
│  - Request Routing                                           │
│  - Authentication/Authorization                              │
│  - Input Validation                                          │
│  - Response Formatting                                       │
└────┬─────────┬───────────┬───────────────────────┬──────────┘
     │         │           │                       │
     │         │           │                       │
     ▼         ▼           ▼                       ▼
┌─────────┐ ┌──────┐  ┌─────────────────────┐  ┌──────────────┐
│ MongoDB │ │ Redis│  │ Celery Task Queues  │  │ Monitoring   │
│         │ │      │  │  - high-priority    │  │ (Prometheus) │
│ - Forms │ │-Cache│  │  - default          │  └──────────────┘
│ - Data  │ │-Queue│  │  - batched (AI)     │
└─────────┘ └──┬───┘  └──────────┬──────────┘
               │                 │
               │                 ▼
               │      ┌─────────────────────────┐
               │      │   Celery Workers        │
               │      │                         │
               └──────►  ┌─────────────────┐   │
                      │  │ Worker-High (×4)│   │
                      │  │ - Validations   │   │
                      │  │ - Quick tasks   │   │
                      │  └─────────────────┘   │
                      │                         │
                      │  ┌─────────────────┐   │
                      │  │ Worker-Default  │   │
                      │  │ - Emails        │   │
                      │  │ - Webhooks      │   │
                      │  └─────────────────┘   │
                      │                         │
                      │  ┌─────────────────┐   │
                      │  │ Worker-AI (×1)  │   │
                      │  │ - LLM Inference │   │
                      │  │ - Embeddings    │   │
                      │  └─────────────────┘   │
                      └─────────────────────────┘
```

---

## Deployment Architecture

### Docker Compose Stack

```
┌───────────────────────────── Host Server ─────────────────────────────┐
│                                                                         │
│  ┌────────────── Frontend Network ──────────────┐                     │
│  │                                                │                     │
│  │  ┌─────────────┐         ┌────────────────┐  │                     │
│  │  │   Nginx     │◄────────┤  API Container │  │                     │
│  │  │ (Container) │         │  (Gunicorn)    │  │                     │
│  │  └─────────────┘         └────────┬───────┘  │                     │
│  └────────────────────────────────────┼──────────┘                     │
│                                       │                                 │
│  ┌────────────── Backend Network ─────┼──────────────────────────┐    │
│  │                                     │                           │    │
│  │                                     ▼                           │    │
│  │  ┌──────────────────────────────────────────────────────┐     │    │
│  │  │                   Databases                          │     │    │
│  │  │  ┌─────────────────┐    ┌──────────────────┐       │     │    │
│  │  │  │ MongoDB         │    │ Redis            │       │     │    │
│  │  │  │ Volume: db_data │    │ Volume: cache    │       │     │    │
│  │  │  └─────────────────┘    └──────────────────┘       │     │    │
│  │  └──────────────────────────────────────────────────────┘     │    │
│  │                                     │                           │    │
│  │                                     ▼                           │    │
│  │  ┌──────────────────────────────────────────────────────┐     │    │
│  │  │              Celery Workers                          │     │    │
│  │  │  ┌────────────────┐  ┌────────────┐  ┌───────────┐ │     │    │
│  │  │  │ Worker-High    │  │ Worker-Def │  │ Worker-AI │ │     │    │
│  │  │  │ Concurrency: 4 │  │ Concur: 4  │  │ Concur: 1 │ │     │    │
│  │  │  │ CPU: 0.5       │  │ CPU: 0.5   │  │ CPU: 2.0  │ │     │    │
│  │  │  │ Mem: 512MB     │  │ Mem: 512MB │  │ Mem: 4GB  │ │     │    │
│  │  │  └────────────────┘  └────────────┘  └───────────┘ │     │    │
│  │  └──────────────────────────────────────────────────────┘     │    │
│  │                                                                │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌────────────── Monitoring Network ───────────────────────────┐      │
│  │  ┌──────────────┐   ┌─────────────┐   ┌────────────────┐   │      │
│  │  │ Prometheus   │   │ Node        │   │ Grafana        │   │      │
│  │  │              │◄──┤ Exporter    │   │ (Optional)     │   │      │
│  │  └──────────────┘   └─────────────┘   └────────────────┘   │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Container Resource Allocation

```
┌─────────────────────────────────────────────────────────┐
│           Resource Distribution (16-core server)         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Nginx:           [▓] 0.5 CPU,  256 MB                  │
│  API (Gunicorn):  [▓▓▓▓] 4 CPU, 1 GB                    │
│  Worker-High:     [▓] 0.5 CPU,  512 MB                  │
│  Worker-Default:  [▓] 0.5 CPU,  512 MB                  │
│  Worker-AI:       [▓▓▓▓] 4 CPU, 4 GB                    │
│  MongoDB:         [▓▓] 2 CPU,   2 GB                    │
│  Redis:           [▓] 0.5 CPU,  256 MB                  │
│  Monitoring:      [▓] 0.5 CPU,  256 MB                  │
│  System Reserve:  [▓▓▓] 3.5 CPU, 7.2 GB                 │
│                                                          │
│  Total Used:      12.5 / 16 CPU, 8.8 / 16 GB            │
└─────────────────────────────────────────────────────────┘
```

---

## Request Flow

### Standard API Request Flow

```
┌─────────┐                                    ┌──────────────┐
│         │  1. HTTPS Request                  │              │
│ Client  ├──────────────────────────────────► │    Nginx     │
│         │                                    │              │
└─────────┘                                    └──────┬───────┘
                                                      │
                                              2. Forward to API
                                                      │
                                               ┌──────▼───────┐
                                               │              │
                                               │ API Gateway  │
                                               │  (Gunicorn)  │
                                               │              │
                                               └──────┬───────┘
                                                      │
                                    ┌─────────────────┼─────────────────┐
                                    │                 │                 │
                           3a. Check Cache   3b. Authenticate  3c. Validate
                                    │                 │                 │
                              ┌─────▼────┐     ┌─────▼─────┐    ┌─────▼─────┐
                              │          │     │           │    │           │
                              │  Redis   │     │ JWT Token │    │  Schema   │
                              │  (Cache) │     │ Verify    │    │ Validator │
                              │          │     │           │    │           │
                              └─────┬────┘     └─────┬─────┘    └─────┬─────┘
                                    │                 │                 │
                                    └─────────────────┼─────────────────┘
                                                      │
                                               4. Process Request
                                                      │
                                       ┌──────────────┼──────────────┐
                                       │              │              │
                                  Cache Hit?          │              │
                                       │              │              │
                                  ┌────▼───┐     ┌────▼─────┐      │
                                  │        │     │          │      │
                                  │ Return │     │ MongoDB  │      │
                                  │ Cached │     │ Query    │      │
                                  │        │     │          │      │
                                  └────┬───┘     └────┬─────┘      │
                                       │              │              │
                                       │              │ 5. Cache Result
                                       │              │              │
                                       │         ┌────▼─────┐        │
                                       │         │          │        │
                                       │         │  Redis   │        │
                                       │         │  SET     │        │
                                       │         │          │        │
                                       │         └────┬─────┘        │
                                       │              │              │
                                       └──────────────┼──────────────┘
                                                      │
                                               6. Format Response
                                                      │
                                               ┌──────▼───────┐
                                               │              │
                                               │ JSON Builder │
                                               │ + Headers    │
                                               │              │
                                               └──────┬───────┘
                                                      │
                                              7. Return Response
                                                      │
┌─────────┐                                    ┌──────▼──────┐
│         │  8. HTTPS Response                 │             │
│ Client  │◄───────────────────────────────────┤    Nginx    │
│         │                                    │             │
└─────────┘                                    └─────────────┘

Performance Targets:
- Cache Hit: < 50ms
- Cache Miss: < 200ms
- Database Query: < 100ms
- Total (p95): < 500ms
```

---

## Task Processing Flow

### Asynchronous Task Queue Flow

```
┌─────────────────┐
│  API Request    │
│  (Queue Task)   │
└────────┬────────┘
         │
         │ 1. Create Task
         │
    ┌────▼─────────────────────────────┐
    │  Celery Task Created              │
    │  - Generate Task ID               │
    │  - Serialize Arguments            │
    │  - Determine Queue (by routing)   │
    └────┬─────────────────────────────┘
         │
         │ 2. Route to Queue
         │
    ┌────▼────────────────────────────────────┐
    │         Redis Task Broker               │
    │  ┌──────────────┐ ┌──────────────┐     │
    │  │high-priority │ │   default    │     │
    │  │  (Queue 1)   │ │  (Queue 2)   │     │
    │  └──────────────┘ └──────────────┘     │
    │  ┌──────────────┐                      │
    │  │   batched    │                      │
    │  │  (Queue 3)   │                      │
    │  └──────────────┘                      │
    └────┬────┬─────────┬───────────────────┘
         │    │         │
         │    │         │ 3. Workers Poll Queues
         │    │         │
    ┌────▼────▼─────────▼─────────────┐
    │      Worker Pool Selection       │
    │                                  │
    │  Priority Algorithm:             │
    │  1. High-priority (weight: 3)    │
    │  2. Default (weight: 2)          │
    │  3. Batched (weight: 1)          │
    └────┬────┬─────────┬──────────────┘
         │    │         │
         │    │         │ 4. Execute Task
         │    │         │
    ┌────▼────┴─────────▼──────────────┐
    │     Task Execution Context        │
    │                                   │
    │  ┌─────────────────────────────┐ │
    │  │ Pre-execution:              │ │
    │  │ - Load context/config       │ │
    │  │ - Connect to dependencies   │ │
    │  │ - Start timer               │ │
    │  └─────────────────────────────┘ │
    │                                   │
    │  ┌─────────────────────────────┐ │
    │  │ Execution:                  │ │
    │  │ - Run task logic            │ │
    │  │ - Monitor progress          │ │
    │  │ - Handle errors             │ │
    │  └─────────────────────────────┘ │
    │                                   │
    │  ┌─────────────────────────────┐ │
    │  │ Post-execution:             │ │
    │  │ - Store result              │ │
    │  │ - Cleanup resources         │ │
    │  │ - Update metrics            │ │
    │  └─────────────────────────────┘ │
    └────┬──────────────────────────────┘
         │
         │ 5. Store Result
         │
    ┌────▼──────────────────────────┐
    │  Redis Result Backend          │
    │  - Task Status: SUCCESS        │
    │  - Result Data                 │
    │  - Execution Time              │
    │  - TTL: 1 hour                 │
    └────┬──────────────────────────┘
         │
         │ 6. Optional: Trigger Webhook
         │
    ┌────▼──────────────────────────┐
    │  Webhook Notification          │
    │  POST to configured URL        │
    │  {                             │
    │    "task_id": "...",           │
    │    "status": "SUCCESS",        │
    │    "result": {...}             │
    │  }                             │
    └────────────────────────────────┘

Retry Logic on Failure:
┌────────────────────────────────┐
│ Task Failed                    │
└────┬───────────────────────────┘
     │
     ▼
┌─────────────────────┐  No  ┌──────────────────┐
│ Retries < Max (3)?  ├──────► Move to DLQ      │
└────┬────────────────┘      │ Alert Admin      │
     │ Yes                   └──────────────────┘
     ▼
┌─────────────────────┐
│ Exponential Backoff │
│ Wait: 2^retry * 10s │
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ Re-queue Task       │
└─────────────────────┘
```

---

## AI Processing Flow

### CPU-Optimized AI Inference Flow

```
┌──────────────────┐
│  User Request    │
│  "Analyze Form"  │
└────────┬─────────┘
         │
         │ 1. Queue AI Task
         │
    ┌────▼─────────────────────┐
    │  API: Create AI Task     │
    │  - Validate input        │
    │  - Generate task_id      │
    │  - Return 202 Accepted   │
    └────┬─────────────────────┘
         │
         │ 2. Task to Batched Queue
         │
    ┌────▼────────────────────┐
    │  Redis: batched queue   │
    │  Concurrency: 1         │
    │  (Serial processing)    │
    └────┬────────────────────┘
         │
         │ 3. Worker Picks Up Task
         │
    ┌────▼────────────────────────────┐
    │  Worker-AI Container            │
    │  CPU: 4 cores                   │
    │  Memory: 4GB                    │
    │  Concurrency: 1 (no parallel)   │
    └────┬────────────────────────────┘
         │
         │ 4. Load Model (if not cached)
         │
    ┌────▼─────────────────────────────┐
    │  Model Loader                    │
    │  ┌────────────────────────────┐  │
    │  │ Check Model Cache          │  │
    │  │ - In-memory model loaded?  │  │
    │  └────┬───────────────────────┘  │
    │       │                           │
    │       ├─ Cache Hit ──────────┐    │
    │       │                      │    │
    │       └─ Cache Miss          │    │
    │          │                   │    │
    │     ┌────▼─────────────┐     │    │
    │     │ Load Model       │     │    │
    │     │ - llama.cpp      │     │    │
    │     │ - GGUF 4-bit     │     │    │
    │     │ - OpenBLAS       │     │    │
    │     │ Time: ~10s       │     │    │
    │     └────┬─────────────┘     │    │
    │          │                   │    │
    │          └───────────────────┘    │
    └────┬──────────────────────────────┘
         │
         │ 5. Run Inference
         │
    ┌────▼─────────────────────────────┐
    │  llama.cpp Inference             │
    │  ┌────────────────────────────┐  │
    │  │ Input Processing:          │  │
    │  │ - Tokenize prompt          │  │
    │  │ - Apply chat template      │  │
    │  │ - Set generation params    │  │
    │  └────┬───────────────────────┘  │
    │       │                           │
    │  ┌────▼───────────────────────┐  │
    │  │ CPU Inference:             │  │
    │  │ - Thread count: 4          │  │
    │  │ - Quantized weights (4bit) │  │
    │  │ - OpenBLAS acceleration    │  │
    │  │ - Streaming output         │  │
    │  │ Time: 2-10s per token      │  │
    │  └────┬───────────────────────┘  │
    │       │                           │
    │  ┌────▼───────────────────────┐  │
    │  │ Progress Updates:          │  │
    │  │ - Update task state        │  │
    │  │ - Track token count        │  │
    │  │ - Monitor timeout (5 min)  │  │
    │  └────────────────────────────┘  │
    └────┬──────────────────────────────┘
         │
         │ 6. Post-process Result
         │
    ┌────▼────────────────────────────┐
    │  Result Processing              │
    │  - Detokenize output            │
    │  - Apply output filters         │
    │  - Format as JSON               │
    │  - Calculate metrics            │
    └────┬────────────────────────────┘
         │
         │ 7. Store Result & Metrics
         │
    ┌────▼────────────────────────────┐
    │  Redis + MongoDB                │
    │  ┌───────────────────────────┐  │
    │  │ Redis (Task Result):      │  │
    │  │ - task_id: result         │  │
    │  │ - TTL: 1 hour             │  │
    │  └───────────────────────────┘  │
    │  ┌───────────────────────────┐  │
    │  │ MongoDB (Permanent):      │  │
    │  │ - ai_results collection   │  │
    │  │ - Full context + result   │  │
    │  │ - Metrics (time, tokens)  │  │
    │  └───────────────────────────┘  │
    └────┬────────────────────────────┘
         │
         │ 8. Trigger Webhook
         │
    ┌────▼────────────────────────────┐
    │  Webhook Delivery               │
    │  POST webhook_url               │
    │  {                              │
    │    "task_id": "ai-task-123",    │
    │    "status": "completed",       │
    │    "result": {                  │
    │      "analysis": "...",         │
    │      "confidence": 0.87,        │
    │      "inference_time": 8.2      │
    │    }                            │
    │  }                              │
    └────┬────────────────────────────┘
         │
         │ 9. Client Polls or Receives Webhook
         │
    ┌────▼────────────────────────────┐
    │  Client Retrieves Result        │
    │  GET /api/v1/tasks/ai-task-123  │
    │  → 200 OK + AI result           │
    └─────────────────────────────────┘

Performance Characteristics:
- Model Load Time: ~10s (first time)
- Cached Load Time: < 1s
- Inference Time: 5-10s (7B model, ~100 tokens)
- Total Time: 6-20s (depending on cache)
- Memory Usage: ~3-4GB
- CPU Usage: 80-100% (4 cores)
```

---

## Analytics Pipeline Flow

### Lightweight ETL with DuckDB

```
┌────────────────────────────────────┐
│  Scheduled Task (Daily, 2 AM)     │
│  Cron: 0 2 * * *                  │
└────────┬───────────────────────────┘
         │
         │ 1. Extract Data
         │
    ┌────▼─────────────────────────────┐
    │  Data Extraction Task            │
    │  ┌────────────────────────────┐  │
    │  │ MongoDB Aggregation:       │  │
    │  │ - Yesterday's responses    │  │
    │  │ - Form analytics           │  │
    │  │ - User activity            │  │
    │  │ Pipeline: [                │  │
    │  │   {$match: {date: ...}},   │  │
    │  │   {$project: {...}}        │  │
    │  │ ]                          │  │
    │  └────────────────────────────┘  │
    └────┬─────────────────────────────┘
         │
         │ 2. Transform to Parquet
         │
    ┌────▼─────────────────────────────┐
    │  Data Transformation             │
    │  import pyarrow as pa            │
    │  import pyarrow.parquet as pq    │
    │                                  │
    │  # Convert to Arrow Table        │
    │  table = pa.Table.from_pydict({ │
    │    'response_id': [...],         │
    │    'form_id': [...],             │
    │    'created_at': [...],          │
    │    'data': [...]                 │
    │  })                              │
    │                                  │
    │  # Write as Parquet              │
    │  pq.write_table(                 │
    │    table,                        │
    │    f'data/responses_{date}.pq',  │
    │    compression='snappy'          │
    │  )                               │
    └────┬─────────────────────────────┘
         │
         │ 3. Load into DuckDB
         │
    ┌────▼─────────────────────────────┐
    │  DuckDB Loading                  │
    │  import duckdb                   │
    │                                  │
    │  conn = duckdb.connect(':memory:')│
    │                                  │
    │  # Load Parquet files            │
    │  conn.execute("""                │
    │    CREATE TABLE responses AS    │
    │    SELECT * FROM               │
    │    'data/responses_*.pq'        │
    │  """)                            │
    │                                  │
    │  # Create indexes for speed      │
    │  conn.execute("""                │
    │    CREATE INDEX idx_form        │
    │    ON responses(form_id)        │
    │  """)                            │
    └────┬─────────────────────────────┘
         │
         │ 4. Run Analytical Queries
         │
    ┌────▼─────────────────────────────┐
    │  Query Execution                 │
    │                                  │
    │  # Query 1: Daily summary        │
    │  daily_stats = conn.execute("""  │
    │    SELECT                        │
    │      form_id,                    │
    │      COUNT(*) as total,          │
    │      AVG(completion_time) as avg │
    │    FROM responses                │
    │    GROUP BY form_id              │
    │  """).fetchall()                 │
    │                                  │
    │  # Query 2: User activity        │
    │  user_activity = conn.execute("""│
    │    SELECT                        │
    │      DATE_TRUNC('hour', created),│
    │      COUNT(*) as responses       │
    │    FROM responses                │
    │    GROUP BY 1                    │
    │    ORDER BY 1                    │
    │  """).fetchall()                 │
    │                                  │
    │  # Query 3: Custom aggregations  │
    │  # ... more queries ...          │
    └────┬─────────────────────────────┘
         │
         │ 5. Cache Results
         │
    ┌────▼─────────────────────────────┐
    │  Redis Caching                   │
    │  import json                     │
    │                                  │
    │  # Cache for 24 hours            │
    │  redis.setex(                    │
    │    'analytics:daily_stats',      │
    │    86400,  # TTL                 │
    │    json.dumps(daily_stats)       │
    │  )                               │
    │                                  │
    │  redis.setex(                    │
    │    'analytics:user_activity',    │
    │    86400,                        │
    │    json.dumps(user_activity)     │
    │  )                               │
    └────┬─────────────────────────────┘
         │
         │ 6. Serve via API
         │
    ┌────▼─────────────────────────────┐
    │  API Endpoint                    │
    │  GET /api/v1/analytics/daily     │
    │                                  │
    │  # Check cache first             │
    │  cached = redis.get(             │
    │    'analytics:daily_stats'       │
    │  )                               │
    │                                  │
    │  if cached:                      │
    │    return json.loads(cached)     │
    │  else:                           │
    │    # Re-run query (fallback)     │
    │    return run_duckdb_query()     │
    └──────────────────────────────────┘

Query Performance:
┌──────────────────────┬──────────┬───────────┐
│ Query Type           │ DuckDB   │ MongoDB   │
├──────────────────────┼──────────┼───────────┤
│ Simple Aggregation   │ 50ms     │ 200ms     │
│ Complex JOIN         │ 200ms    │ 2000ms    │
│ Window Functions     │ 100ms    │ N/A       │
│ Full Table Scan      │ 500ms    │ 5000ms    │
└──────────────────────┴──────────┴───────────┘
```

---

## Failure Recovery Flows

### Container Failure Recovery

```
┌─────────────────────────────────────┐
│  Container Running Normally          │
└────────┬────────────────────────────┘
         │
         ▼
    ┌─────────────────┐
    │ Failure Occurs  │ ◄──── Examples:
    │ (Container Dies)│       - OOM Kill
    └────────┬────────┘       - Crash
             │                - Manual Kill
             │                - Resource Limit
             │
             ▼
    ┌──────────────────────────────┐
    │ Docker Detects Failure       │
    │ - Health check fails         │
    │ - Process exit detected      │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Restart Policy Activated     │
    │ restart: unless-stopped      │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Exponential Backoff          │
    │ - Attempt 1: Immediate       │
    │ - Attempt 2: 10s delay       │
    │ - Attempt 3: 20s delay       │
    │ - Attempt 4: 40s delay       │
    │ - Max attempts: 10           │
    └────────┬─────────────────────┘
             │
             ├──── Success ─────┐
             │                  │
             ├──── Failed ──────┤
             │                  │
             ▼                  ▼
    ┌─────────────────┐  ┌──────────────────┐
    │ Container       │  │ Alert           │
    │ Restarted       │  │ Administrator   │
    │ Successfully    │  │ (Max retries)   │
    └────────┬────────┘  └─────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Recover State                │
    │ - Reconnect to database      │
    │ - Reload configuration       │
    │ - Re-register with           │
    │   monitoring                 │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Resume Normal Operation      │
    │ - Process pending tasks      │
    │ - Accept new requests        │
    └──────────────────────────────┘

Task Recovery (Worker Failure):
┌──────────────────────────────┐
│ Worker processing task       │
└────────┬─────────────────────┘
         │
         ▼
    ┌─────────────────┐
    │ Worker dies     │
    └────────┬────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Celery Detects Worker Down   │
    │ - Heartbeat timeout          │
    │ - No ACK received            │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Task Re-queued               │
    │ - Task returns to queue      │
    │ - Retry counter incremented  │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ New Worker Picks Up Task     │
    │ - Execute from beginning     │
    │ (Idempotent operations)      │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Task Completes Successfully  │
    └──────────────────────────────┘
```

### Database Connection Recovery

```
┌──────────────────────────────┐
│ Database Connection Lost     │
└────────┬─────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Application Detects Error       │
│ - pymongo.errors.ServerSelection│
│ - Connection timeout            │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Retry Logic (pymongo built-in)  │
│ - max_pool_size: 10             │
│ - serverSelectionTimeoutMS: 5000│
│ - retryWrites: true             │
└────────┬────────────────────────┘
         │
         ├─── Reconnected ────┐
         │                    │
         ├─── Still Failed ───┤
         │                    │
         ▼                    ▼
┌──────────────────┐  ┌────────────────────┐
│ Resume Operation │  │ Return Error       │
│                  │  │ - 503 Unavailable  │
│                  │  │ - Log error        │
│                  │  │ - Alert admin      │
└──────────────────┘  └────────────────────┘
```

---

## Security Flows

### Authentication Flow

```
┌─────────────┐                        ┌──────────────┐
│   Client    │                        │  API Server  │
└─────┬───────┘                        └───────┬──────┘
      │                                        │
      │  1. POST /auth/login                   │
      │  {username, password}                  │
      ├───────────────────────────────────────►│
      │                                        │
      │                                2. Validate
      │                                   Credentials
      │                                        │
      │                            ┌───────────▼────────┐
      │                            │ - Hash password    │
      │                            │ - Compare with DB  │
      │                            │ - Check user status│
      │                            └───────────┬────────┘
      │                                        │
      │                             3. Generate JWT
      │                                        │
      │                            ┌───────────▼────────┐
      │                            │ jwt.encode({       │
      │                            │   user_id: ...,    │
      │                            │   roles: [...],    │
      │                            │   exp: now + 24h   │
      │                            │ }, SECRET_KEY)     │
      │                            └───────────┬────────┘
      │                                        │
      │  4. Return JWT Token                   │
      │◄───────────────────────────────────────┤
      │  {token: "eyJ..."}                     │
      │                                        │
      │                                        │
      │  5. Authenticated Request              │
      │  GET /api/v1/forms                     │
      │  Authorization: Bearer eyJ...          │
      ├───────────────────────────────────────►│
      │                                        │
      │                                6. Verify JWT
      │                                        │
      │                            ┌───────────▼────────┐
      │                            │ - Decode token     │
      │                            │ - Verify signature │
      │                            │ - Check expiration │
      │                            │ - Load user        │
      │                            └───────────┬────────┘
      │                                        │
      │                             7. Authorize
      │                                        │
      │                            ┌───────────▼────────┐
      │                            │ - Check permissions│
      │                            │ - Validate access  │
      │                            └───────────┬────────┘
      │                                        │
      │  8. Return Data                        │
      │◄───────────────────────────────────────┤
      │  {forms: [...]}                        │
      │                                        │
```

### Secret Management Flow

```
┌──────────────────────────────────────────────┐
│  Deployment Time                             │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  1. Load Secrets from Secure Storage         │
│  - .env file (local development)             │
│  - Docker Secrets (production)               │
│  - External vault (optional)                 │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  2. Inject into Container Environment        │
│  docker-compose.yml:                         │
│  environment:                                │
│    - SECRET_KEY=${SECRET_KEY}                │
│  secrets:                                    │
│    - db_password                             │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  3. Application Reads Secrets                │
│  import os                                   │
│  SECRET_KEY = os.getenv('SECRET_KEY')        │
│  DB_PASSWORD = open('/run/secrets/           │
│                     db_password').read()     │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  4. Never Log or Expose Secrets              │
│  - Redact from logs                          │
│  - Don't include in error messages           │
│  - Don't return in API responses             │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  5. Rotate Periodically (Quarterly)          │
│  - Generate new secrets                       │
│  - Update in secure storage                  │
│  - Rolling restart of services               │
└──────────────────────────────────────────────┘
```

---

## Monitoring Flow

### Metrics Collection Flow

```
┌─────────────────────────────────────────────────────────┐
│                   Application Services                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │    API     │  │  Workers   │  │ Databases  │        │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘        │
└────────┼───────────────┼───────────────┼────────────────┘
         │               │               │
         │ Expose        │ Expose        │ Expose
         │ Metrics       │ Metrics       │ Metrics
         │               │               │
         ▼               ▼               ▼
┌──────────────────────────────────────────────────────────┐
│              Prometheus Exporters                         │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Python App      │  │ Redis        │  │ Node        │ │
│  │ Metrics         │  │ Exporter     │  │ Exporter    │ │
│  │ (Custom)        │  │              │  │ (System)    │ │
│  └────────┬────────┘  └──────┬───────┘  └──────┬──────┘ │
└───────────┼──────────────────┼─────────────────┼─────────┘
            │                  │                 │
            │ HTTP :8000/metrics                 │
            │ HTTP :9121/metrics                 │
            │ HTTP :9100/metrics                 │
            │                  │                 │
            └──────────────────┼─────────────────┘
                               │
                               │ Scrape (every 15s)
                               │
                        ┌──────▼─────────┐
                        │                │
                        │  Prometheus    │
                        │  Server        │
                        │                │
                        └──────┬─────────┘
                               │
                               │ Store Time Series
                               │
                        ┌──────▼─────────┐
                        │ Time Series DB │
                        │ Retention: 30d │
                        └──────┬─────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌──────────┐   ┌────────────┐  ┌───────────┐
        │ Alerting │   │  Grafana   │  │ API Query │
        │ Rules    │   │ Dashboard  │  │ (PromQL)  │
        └──────────┘   └────────────┘  └───────────┘
```

### Alert Flow

```
┌──────────────────────────────┐
│  Metrics Exceed Threshold    │
│  e.g., CPU > 90% for 5 min   │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Prometheus Alert Triggered  │
│  - Evaluate alert rule       │
│  - Check for duration        │
│  - Assign severity           │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Alertmanager Receives Alert │
│  - Group similar alerts      │
│  - Deduplicate               │
│  - Apply routing rules       │
└────────┬─────────────────────┘
         │
         ├───────┬───────┬──────┐
         │       │       │      │
         ▼       ▼       ▼      ▼
    ┌──────┐ ┌─────┐ ┌────┐ ┌────┐
    │Email │ │Slack│ │PagerDuty│ │SMS│
    └──────┘ └─────┘ └────┘ └────┘
         │       │       │      │
         └───────┴───────┴──────┘
                 │
                 ▼
        ┌────────────────┐
        │ On-Call Receives│
        │ Notification    │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │ Investigate     │
        │ & Resolve       │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │ Acknowledge     │
        │ Alert           │
        └────────────────┘
```

---

## Summary

This document provides comprehensive visual flows for:

✅ **Architecture:** System components and their interactions  
✅ **Deployment:** Container orchestration and resource allocation  
✅ **Request Flow:** API request processing pipeline  
✅ **Task Processing:** Asynchronous task queue workflow  
✅ **AI Processing:** CPU-optimized inference pipeline  
✅ **Analytics:** ETL and query processing flow  
✅ **Failure Recovery:** Automated recovery procedures  
✅ **Security:** Authentication and secret management  
✅ **Monitoring:** Metrics collection and alerting

These flows serve as architectural documentation and troubleshooting guides for the infrastructure team.

---

**Document Status:** Complete  
**Last Updated:** 2026-01-09  
**Maintained By:** Infrastructure Team
