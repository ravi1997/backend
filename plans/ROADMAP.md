# Strategic Roadmap

## Current Status: M2 & M3 COMPLETED ✅

**Completed:** 2026-02-04

## Milestone 1: Security Hardening (M1) ✅

**Completed:** 2026-02-03

- ✅ Docker-compose v1 to v2 upgrade (FIX-20260203-ContainerConfig)
- ✅ Docker/Logs permissions fixed (uploads/ directory created)
- ✅ Test suite verified (88 tests passed)
- ✅ CI/CD workflow stubs added (.github/workflows/)
- ✅ Dependency drift analysis completed (45 outdated packages identified)

---

## Milestone 2: AI-Driven Intelligence (M2) ✅

**Completed:** 2026-02-04

**Goal**: Move from data collection to data insight.

### Core Features

- ✅ **Enhanced Search**: NLP-powered search with query parsing, semantic search, and intent extraction
- ✅ **Automated Summarization**: Extractive and abstractive summarization of feedback responses
- ✅ **Predictive Anomaly Detection**: Spam, outlier, and duplicate detection with auto-thresholding

### Extensions

- ✅ Ollama LLM integration with health checks, fallback models, and streaming support
- ✅ NLP search enhancements: query suggestions, search history, advanced filters
- ✅ Summarization enhancements: custom length, summary comparison across time periods
- ✅ Anomaly detection enhancements: auto-thresholding, batch scanning

### Infrastructure

- ✅ Redis caching with cache invalidation and distributed locking
- ✅ Ollama connection pooling for efficient resource utilization

---

## Milestone 3: Enterprise Ecosystem (M3) ✅

**Completed:** 2026-02-04

**Goal**: Integration and Reliability.

- ✅ **Reliable Webhooks**: Exponential backoff retry mechanism with dead letter queue support
- ✅ **Global SMS**: External AIIMS API integration for OTP and notifications
- ✅ **Dashboard Customization**: User preferences persistence for grid layouts and widgets

---

## Milestone 4: Scaling & Performance (Future)

**Goal**: High availability.

- **Redis Integration**: Cache form schemas to reduce MongoDB load.
- **Celery/RabbitMQ**: Move AI processing and heavy exports to background workers.
- **API Versioning (v2)**: Introduce a breaking-change clean API if necessary.

**M4 Details**: See [`plans/M4/`](plans/M4/) for comprehensive SRS specifications.
