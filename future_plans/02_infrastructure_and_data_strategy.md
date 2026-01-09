# Future Upgrade Plan 2: Efficient Infrastructure & Data Strategy (CPU-Optimized)

**Document Version:** 1.1  
**Dependent On:** Plan 1 (Backend v2.0)  
**Constraint:** CPU-Only Environment (No GPU, No Heavy Orchestration)  
**Goal:** Establish a robust, scalable backend foundation optimized for limited resource environments.

---

## 1. Executive Summary

With the application logic evolving in Plan 1 (AI, Workflows), Plan 2 focuses on **Backend Reliability and Efficiency**. Given the constraint of a CPU-only environment without heavy clusters (like Kubernetes), strict resource management and efficient process orchestration are paramount. We will leverage lightweight containerization and vertically scalable worker pools to handle "Enterprise" logic on standard hardware.

**Core Objectives:**
1.  **Lightweight Orchestration:** Use Docker Compose or Systemd for robust process management without the overhead of K8s.
2.  **CPU-Optimized AI:** Run quantized LLM models suitable for CPU inference.
3.  **Queue-Based Resiliency:** Decouple all heavy processing (AI, Email, Webhooks) to prevent API blocking.
4.  **Operational Intelligence:** Practical logging and monitoring that doesn't eat up all available RAM.

---

## 2. Infrastructure Strategy (No-K8s)

### 2.1 The Need
*   **Low Overhead:** Kubernetes requires significant CPU/RAM just to run its control plane. On standard CPU servers, this waste is unacceptable.
*   **Simplicity:** Deployment should be a simple `git pull && docker compose up` or systemd reload.
*   **Vertical Scaling:** Maximize the usage of all available cores on the host machine.

### 2.2 Deployment Architecture (Docker Compose / Swarm)

#### A. Service Architecture
Instead of hundreds of pods, we run optimized containers:
*   **Container A (Gunicorn/Flask):** The API Gateway. Scaled via Gunicorn workers (`2 * CPU_CORES + 1`).
*   **Container B (Celery Worker - High Priority):** Handles "User-Waiting" tasks (e.g., immediate validations).
*   **Container C (Celery Worker - Low Priority):** Handles batched background tasks (Analytics, Webhooks).
*   **Container D (Nginx):** Reverse proxy for caching and static files.

#### B. Scaling Strategy
*   **Process-Based Scaling:** Instead of adding more servers, we auto-scale the *number of worker processes* within the container based on load, using a minimal supervisor (like `supervisord` or simply managing concurrency limits).
*   **Resource Limits:** Hard limits in `docker-compose.yml` (`cpus: '0.5'`, `mem_limit: '512m'`) to ensure no single service crashes the server.

#### C. Load Balancing
*   **Nginx Upstream:** Configure Nginx to balance requests across multiple local Gunicorn ports if necessary, though a single Gunicorn master is usually sufficient for single-node setups.

---

## 3. CPU-Optimized AI & Data Pipeline

### 3.1 The Need
*   **No GPU:** Standard LLMs (like GPT-4-sized local models) are impossibly slow on CPU.
*   **Data Insight:** We still need analytics, but cannot afford a heavy data warehouse setup.

### 3.2 AI Strategy: Quantization & Distillation
*   **Model Selection:** Use **Quantized Models** (GGUF format via `llama.cpp` or `CTranslate2`).
    *   *Target:* 4-bit quantized 7B (Mistral/Llama-3) or smaller models (Phi-2, TinyLlama).
*   **ONNX Runtime:** Convert Embeddings models to ONNX to run 5-10x faster on CPU than standard PyTorch.
*   **Asynchronous Inference:** AI tasks *never* Block. They go to a specific "Slow Queue". Users got a "Processing..." notification, and a webhook alerts them when the CPU finishes the task.

### 3.3 Light ETL Pipeline
*   **Storage:** Continue using MongoDB for operational data.
*   **Analytics:** Instead of a separate Data Warehouse, use **MongoDB Aggregation Pipeline** or a lightweight, in-process analytical engine like **DuckDB**.
    *   *Flow:* Scheduled task creates a parquet file from Mongo -> Loads into DuckDB for fast analytical queries -> Caches result in Redis.

---

## 4. Security & Process Isolation

### 4.1 The Need
*   **Host Security:** Since everything shares one kernel/host, process isolation is critical.
*   **Secret Management:** Secure credentials without complex vaults.

### 4.2 Implementation
*   **Environment Injection:** Use `.env` files loaded *only* at runtime, never committed. For higher security, use **Docker Secrets**.
*   **Network Isolation:** Use Docker internal networks. The Database container should *not* expose ports to the host (127.0.0.1 only), only reachable by the API container.
*   **AppArmor/Seccomp:** Apply default security profiles to containers to limit system call access.

---

## 5. Observability (Lightweight Stack)

### 5.1 The Need
*   **Visibility:** We need to know if the CPU is pegged at 100% or if Redis is OOM.
*   **Efficiency:** Monitoring tools shouldn't take more than 5% of system resources.

### 5.2 The Stack
*   **Glances:** Lightweight, terminal-based system monitoring.
*   **Prometheus Node Exporter:** Minimal process to expose metrics.
*   **Log Rotate:** Aggressive log rotation to prevent disk overflow. Analyze logs via `grep/awk` scripts or a lightweight forwarder (Vector) to a remote SaaS (free tier of Datadog/NewRelic) if local storage is tight.

---

## 6. Implementation Guide (Step-by-Step)

### Phase 2.1: Optimized Containerization
1.  **Docker Compose**: Define `services` with explicit `deploy.resources.limits`.
2.  **Gunicorn Config**: Auto-tune worker count based on `multiprocessing.cpu_count()`.
3.  **Base Image**: Switch to `python:3.12-slim` or `alpine` to reduce RAM footprint.

### Phase 2.2: The CPU-AI Setup
1.  **Llama.cpp**: Compile `llama-cpp-python` with OpenBLAS (CPU math acceleration).
2.  **Worker Queues**: Configure Celery routes:
    *   `task.ai.*` -> `queue:batched` (concurrency: 1 - process serially to save RAM).
    *   `task.email.*` -> `queue:default` (concurrency: 4).

### Phase 2.3: Analytics with DuckDB
1.  **Ingest Task**: Create a periodic Celery task to dump yesterday's responses to JSONL.
2.  **Query Engine**: Use DuckDB (Python lib) to query that JSONL for complex stats ("Avg response length by user").

---

## 7. Migration & Testing Plan

| Component | Test Strategy | Tool |
|:---|:---|:---|
| **Resource Limits** | Stress test CPU to 100%. Ensure API stays responsive (prioritized). | **stress-ng** |
| **Integrity** | Kill the generic worker container in the middle of a task. Verify task re-queues. | **Docker Kill** |
| **AI Speed** | Benchmark inference time on CPU. Adjust model quantization (q4_k_m vs q5_k_m) to balance speed/quality. | **Pytest Benchmark** |

---

## 8. Summary
Plan 2 adapts the "Enterprise" goals for a **Resource-Constrained, CPU-Only Environment**. By trading the complexity of Kubernetes for the efficiency of Docker Compose and optimized binaries (ONNX/DuckDB/Quantization), we achieve a high-performance system capable of intelligent processing without requiring a massive cloud budget or GPU hardware.
