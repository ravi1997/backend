# Backlog State

## Current Milestone: [M1: Stability & Hardening] - ✅ COMPLETED

## Current Milestone: [M2: AI-Driven Intelligence] - 🔄 IN PROGRESS (25% Complete)

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

## M2 AI Features (1/4 Complete)

| ID | Task | Priority | Status | Assigned | Dependencies |
|---|---|---|---|---|---|
| T-M2-01 | Multi-form Cross-analysis API | High | ✅ DONE | Implementer | None |
| T-M2-02 | NLP Search Enhancement | High | ⏳ PENDING | AI Engineer | Ollama integration |
| T-M2-03 | Automated Summarization | High | ⏳ PENDING | AI Engineer | Ollama integration |
| T-M2-04 | Predictive Anomaly Detection | High | ⏳ PENDING | AI Engineer | Ollama integration |
| T-M2-07 | Validation: Static analysis and tests for M2 AI implementation | High | ⏳ PENDING | AI Engineer | T-M2-02, T-M2-03, T-M2-04 |

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
- **Completed**: 1
- **In Progress**: 0
- **Pending**: 4
- **Blocked**: 0
- **Status**: 🔄 IN PROGRESS (25%)

### M3: Webhooks & Notifications

- **Total Tasks**: 3
- **Completed**: 0
- **In Progress**: 0
- **Pending**: 3
- **Blocked**: 0
- **Status**: ⏳ NOT STARTED

### Overall Project

- **Total Tasks**: 21
- **Completed**: 9
- **In Progress**: 0
- **Pending**: 12
- **Blocked**: 0

## Priority Ranking

### 🔴 Critical (Immediate Action Required)

1. SEC-01: Update bcrypt (security vulnerability)
2. SEC-02: Update cryptography (security vulnerability)
3. SEC-03: Update requests (security vulnerability)
4. SEC-04: Update dnspython (security vulnerability)

### 🟡 High Priority

1. T-M2-02: NLP Search Enhancement
2. T-M2-03: Automated Summarization
3. T-M2-04: Predictive Anomaly Detection
4. SEC-05: Update PyJWT (security vulnerability)

### 🟢 Medium Priority

1. DEP-01: Update all 45 outdated packages
2. T-M3-01: Implement Webhook retry & failure logging

### ⚪ Low Priority

1. T-M3-02: Build pluggable SMS Gateway drivers
2. T-M3-03: User Dashboard customization persistence

## Dependencies

- **M2 Features** (T-M2-02, T-M2-03, T-M2-04) depend on Ollama integration
- **M3 Features** depend on M2 completion
- **Dependency Updates** (DEP-01) should follow security updates (SEC-01 through SEC-05)
