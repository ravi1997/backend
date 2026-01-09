# Future Upgrade Plan 2: Infrastructure Scaling, Security & Data Strategy

**Document Version:** 1.0  
**Dependent On:** Plan 1 (Backend v2.0)  
**Goal:** Establish a hyperscale, secure, and data-intelligent backend foundation.

---

## 1. Executive Summary

With the application logic evolving in Plan 1 (AI, Workflows), Plan 2 focuses exclusively on **Backend Reliability, Scalability, and Data Intelligence**. We are stripping away the UI concerns to focus on the "Engine Room" — ensuring the API can handle 100k+ concurrent requests, data is secure at a banking standard, and raw data is transformed into actionable business intelligence.

**Core Objectives:**
1.  **Hyperscale Architecture:** Move from simple containerization to orchestrator-managed, auto-scaling clusters.
2.  **Data Engineering:** Establish ETL pipelines to transform operational MongoDB data into Analytical insights (Data Warehouse).
3.  **Zero-Trust Security:** Implement advanced backend security (mTLS, Vault, WAF).
4.  **Backend Observability:** Full visibility into API performance and distributed traces.

---

## 2. Infrastructure & Orchestration Strategy

### 2.1 The Need
*   **Resource Efficiency:** Static VMs waste money. We need compute that scales to zero during nights and scales up during surges.
*   **Resiliency:** If a worker node dies, the system must self-heal without human intervention.
*   **Traffic Management:** We need sophisticated load balancing (L7) for our new Event-Driven microservices.

### 2.2 Kubernetes (K8s) Implementation
Shift deployment target to a Kubernetes Cluster (EKS/GKE/AKS or generic K8s).

#### A. Microservices Decomposition
Refactor the monolithic backend into scalable operational units:
*   **Service A (API Gateway):** Handles REST requests, Auth, and Routing.
*   **Service B (Workflow Worker):** Scalable consumer for "Workflow" tasks.
*   **Service C (AI Processor):** GPU-optimized pods for Vector embedding/LLM tasks.
*   **Service D (Webhook Dispatcher):** I/O bound pods for outbound HTTP requests.

#### B. Autoscaling Policies
*   **HPA (Horizontal Pod Autoscaler):** Scale API pods based on CPU utilization (>70%).
*   **KEDA (Kubernetes Event-Driven Autoscaling):** Scale Worker pods based on **Redis List Length**.
    *   *Logic:* If pending_tasks > 1000, spin up 50 extra workers instantly.

#### C. Traffic Management (Istio / Nginx Ingress)
*   **Rate Limiting:** Protect backend from abuse (e.g., limit 100 req/min per Tenant).
*   **Circuit Breaking:** If the Vector DB is slow, fail fast instead of hanging all threads.

---

## 3. Data Engineering & Analytics Pipeline

### 3.1 The Need
*   **OLTP vs OLAP:** MongoDB is great for storing Forms (OLTP), but terrible for complex aggregations like "Average response time per sector over last year" (OLAP).
*   **Data Silos:** We have data in Mongo, Logs, and potentially external integrations.

### 3.2 Strategy: The ELT Pipeline
Extract data from the operational backend and load it into a Data Warehouse (Snowflake / BigQuery / ClickHouse).

#### A. Extraction Layer (Airflow / Dagster)
*   **Job:** Nightly batch jobs (or CDC - Change Data Capture) to pull new `FormResponses` and `AuditLogs`.
*   **Transformation:** Flatten nested JSON structures into tabular formats (SQL-friendly).

#### B. Analytical Storage
*   **Target:** A Columnar Database suitable for analytics.
*   **Schema modeling:** Star Schema (Fact Tables: *Responses*, Dimension Tables: *Users, Forms, Time*).

#### C. Analytics API Service
*   **New Service:** `internal-analytics-api`.
*   **Purpose:** Serve aggregated stats back to the main API (for "Dashboards") without hitting the primary MongoDB.
*   **Caching:** Heavy use of Redis for pre-calculated stats.

---

## 4. Advanced Security Architecture (SecOps)

### 4.1 The Need
*   **Secret Sprawl:** API Keys and DB passwords should not be in environment variables (security risk).
*   **Internal Threats:** Services within the cluster should verify each other (Zero Trust).

### 4.2 Implementation
*   **Secret Management (HashiCorp Vault):**
    *   Dynamic control of credentials.
    *   Apps request a temp DB password on startup; it expires automatically.
*   **Mutual TLS (mTLS):**
    *   Encrypt traffic *between* services (e.g., API -> Worker).
    *   Ensure "Worker" only accepts connections from "API", not from "Public Internet".
*   **WAF (Web Application Firewall):**
    *   Inspect incoming JSON bodies for Injection Attacks (SQLi, NoSQLi) before they reach the Flask app.

---

## 5. Backend Observability & Reliability

### 5.1 The Need
*   **Distributed Tracing:** When a request fails, did it die in the API, the Worker, or the DB?
*   **Proactive Alerting:** Know about failures before users report them.

### 5.2 The Stack (OTel)
*   **OpenTelemetry:** Instrument Python code to create "Spans" for every function call.
*   **Trace ID Propagation:** Pass a `X-Request-ID` through API -> Redis -> Worker -> Webhook to visualize the full lifecycle.
*   **Dashboards:**
    *   *API Latency (p95, p99)*
    *   *Worker Queue Depth*
    *   *Error Rate by Endpoint*

---

## 6. Implementation Guide (Step-by-Step)

### Phase 2.1: Infrastructure as Code (IaC)
1.  **Terraform**: Write `.tf` files to provision the K8s cluster, Redis (Managed), and Mongo Atlas.
2.  **Helm Charts**: Templates for deploying our Services (API, Worker, Beat).

### Phase 2.2: Data Pipeline
1.  **Debezium (CDC)**: Setup Debezium connector to listen to MongoDB Oplog and push changes to a Kafka/Redpanda topic.
2.  **Ingestion Service**: Write a consumer that takes Kafka messages and inserts into ClickHouse/BigQuery.

### Phase 2.3: Security Hardening
1.  **Vault Setup**: Deploy Vault. Move `MONGODB_URI` and `OPENAI_KEY` into Vault secrets.
2.  **Network Policies**: Deny all ingress traffic to pods by default; allow only specific paths.

---

## 7. Migration & Testing Plan

| Component | Test Strategy | Tool |
|:---|:---|:---|
| **Auto-Scaling** | Flood backend with 10k dummy requests. Watch Pod count increase. | **k6 / Locust** |
| **Disaster Recovery** | "Chaos Monkey": Randomly kill MongoDB Primary node. Verify easy failover. | **Chaos Mesh** |
| **Security** | Automated Penetration Test (OWASP ZAP) against staging API. | **ZAP Proxy** |
| **Data Integrity** | Compare specific MongoDB document vs Data Warehouse row. | **Great Expectations** |

---

## 8. Summary
Plan 2 transforms the backend from a "Server" to a "Platform". It ensures that the complex Application Logic built in Plan 1 runs on infrastructure that is **Resilient** (K8s), **Secure** (Vault/mTLS), and **Insightful** (Data Warehouse).
