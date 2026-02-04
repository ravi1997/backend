# Backlog State

## Current Milestone: [M1: Stability & Hardening] - ✅ COMPLETED

## Current Milestone: [M2: AI-Driven Intelligence] - ✅ COMPLETED (100%)

## M1 Completed Tasks

| ID | Task | Priority | Status | Assigned |
|---|---|---|---|---|
| T-01 | Fix puremagic dependency & requirements sync | High | ✅ DONE | Implementer |
| T-02 | Fix logs permission issue (Docker/Local) | High | ✅ DONE | Implementer |
| T-03 | Add edge case tests for Auth (Invalid roles) | Medium | ✅ DONE | Tester |
| T-04 | Setup basic GitHub Actions workflow | Medium | ✅ DONE | DevOps |
| T-05 | Document Deployment & Env variables | Medium | ✅ DONE | Architect |
| T-M11 | Implement aggregated form analytics | High | ✅ DONE | Implementer |
| T-M12 | Implement form publishing & versioning logic | High | ✅ DONE | Implementer |
| T-M17 | Implement embedded workflow execution | High | ✅ DONE | Implementer |

## M1 Security Debt (5 Vulnerabilities - High Priority)

| ID | Task | Priority | Status | Assigned | Dependencies |
|---|---|---|---|---|---|
| SEC-01 | Update bcrypt from 3.2.2 to 5.0.0 | 🔴 High | ⏳ PENDING | Security | None |
| SEC-02 | Update cryptography from 44.0.3 to 46.0.4 | 🔴 High | ⏳ PENDING | Security | None |
| SEC-03 | Update requests from 2.31.0 to 2.32.5 | 🔴 High | ⏳ PENDING | Security | None |
| SEC-04 | Update dnspython from 2.7.0 to 2.8.0 | 🔴 High | ⏳ PENDING | Security | None |
| SEC-05 | Update PyJWT from 2.7.0 to 2.11.0 | 🟡 Medium | ⏳ PENDING | Security | None |

## M2 AI Features (5/5 Complete - 100%)

| ID | Task | Priority | Status | Assigned | Dependencies |
|---|---|---|---|---|---|
| T-M2-01 | Multi-form Cross-analysis API | High | ✅ DONE | Implementer | None |
| T-M2-02 | NLP Search Enhancement | High | ✅ DONE | AI Engineer | Ollama integration |
| T-M2-03 | Automated Summarization | High | ✅ DONE | AI Engineer | Ollama integration |
| T-M2-04 | Predictive Anomaly Detection | High | ✅ DONE | AI Engineer | Ollama integration |
| T-M2-07 | Validation: Static analysis and tests for M2 AI implementation | High | ✅ DONE | AI Engineer | T-M2-02, T-M2-03, T-M2-04 |

### M2 Implementation Details

#### T-M2-02: NLP Search Enhancement ✅ COMPLETED

- Created `app/services/nlp_service.py` with query parsing
- Implemented semantic search using Ollama embeddings
- Added `app/routes/v1/form/nlp_search.py` with endpoints:
  - `POST /api/v1/ai/forms/<form_id>/nlp-search`
  - `POST /api/v1/ai/forms/<form_id>/semantic-search`
  - `GET /api/v1/ai/forms/<form_id>/search-stats`

#### T-M2-03: Automated Summarization ✅ COMPLETED

- Created `app/services/summarization_service.py` with:
  - Extractive summarization (TF-IDF based)
  - Abstractive summarization (Ollama LLM)
  - Theme-based analysis
  - Executive summary generation
- Added `app/routes/v1/form/summarization.py` with endpoints:
  - `POST /api/v1/ai/forms/<form_id>/summarize`
  - `POST /api/v1/ai/forms/<form_id>/executive-summary`
  - `POST /api/v1/ai/forms/<form_id>/theme-summary`

#### T-M2-04: Predictive Anomaly Detection ✅ COMPLETED

- Created `app/services/anomaly_detection_service.py` with:
  - Spam detection (keywords, patterns, timing)
  - Statistical outlier detection (Z-score)
  - Duplicate detection
  - Impossible value detection
- Added `app/routes/v1/form/anomaly.py` with endpoints:
  - `POST /api/v1/ai/forms/<form_id>/detect-anomalies`
  - `GET /api/v1/ai/forms/<form_id>/anomalies/<response_id>`
  - `GET /api/v1/ai/forms/<form_id>/anomaly-stats`

#### T-M2-07: Validation & Tests ✅ COMPLETED

- Created `tests/unit/test_nlp_search.py` with:
  - Tests for NLP Search Service
  - Tests for Summarization Service
  - Tests for Anomaly Detection Service
  - Tests for Ollama Service (mocked)

## M3 Webhooks & Notifications (Not Started)

| ID | Task | Priority | Status | Assigned | Dependencies |
|---|---|---|---|---|---|
| T-M3-01 | Implement Webhook retry & failure logging | High | ⏳ TODO | Implementer | M2 completion |
| T-M3-02 | Build pluggable SMS Gateway drivers | Medium | ⏳ TODO | DevOps | M2 completion |
| T-M3-03 | User Dashboard customization persistence | Low | ⏳ TODO | Implementer | M2 completion |

## Dependency Updates (45 Outdated Packages)

| ID | Task | Priority | Status | Assigned | Dependencies |
|---|---|---|---|---|---|
| DEP-01 | Update all 45 outdated packages | Medium | ⏳ PENDING | DevOps | Security updates first |

## Progress Summary

### M1: Stability & Hardening

- **Total Tasks**: 8
- **Completed**: 8
- **In Progress**: 0
- **Pending**: 0
- **Blocked**: 0
- **Status**: ✅ COMPLETED

### M2: AI-Driven Intelligence

- **Total Tasks**: 5
- **Completed**: 5
- **In Progress**: 0
- **Pending**: 0
- **Blocked**: 0
- **Status**: ✅ COMPLETED (100%)

### M3: Webhooks & Notifications

- **Total Tasks**: 3
- **Completed**: 0
- **In Progress**: 0
- **Pending**: 3
- **Blocked**: 0
- **Status**: ⏳ NOT STARTED

### Overall Project

- **Total Tasks**: 21
- **Completed**: 13
- **In Progress**: 0
- **Pending**: 8
- **Blocked**: 0

## Priority Ranking

### 🔴 Critical (Immediate Action Required)

1. SEC-01: Update bcrypt (security vulnerability)
2. SEC-02: Update cryptography (security vulnerability)
3. SEC-03: Update requests (security vulnerability)
4. SEC-04: Update dnspython (security vulnerability)

### 🟡 High Priority

1. SEC-05: Update PyJWT (security vulnerability)
2. T-M3-01: Implement Webhook retry & failure logging
3. DEP-01: Update all 45 outdated packages

### 🟢 Medium Priority

1. T-M3-02: Build pluggable SMS Gateway drivers
2. T-M3-03: User Dashboard customization persistence

## Dependencies

- **M2 Features**: All implemented and complete
- **M3 Features**: Waiting on M2 completion (now ready)
- **Dependency Updates** (DEP-01): Should follow security updates (SEC-01 through SEC-05)

## M2 Files Created/Modified

### New Files

- `app/services/ollama_service.py` - Ollama LLM integration
- `app/services/nlp_service.py` - NLP search processing
- `app/services/summarization_service.py` - Response summarization
- `app/services/anomaly_detection_service.py` - Anomaly detection
- `app/routes/v1/form/nlp_search.py` - NLP search routes
- `app/routes/v1/form/summarization.py` - Summarization routes
- `app/routes/v1/form/anomaly.py` - Anomaly detection routes
- `tests/unit/test_nlp_search.py` - M2 unit tests

### Modified Files

- `app/routes/v1/form/routes.py` - Added M2 route imports
