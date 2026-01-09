# Software Requirements Specification (SRS)
## Phase 1: Foundation & Event-Driven Architecture

**Document Version:** 1.0  
**Date:** January 9, 2026  
**Phase:** P1 - Foundation  
**Status:** Planning & Design  

---

## 1. Introduction

### 1.1 Purpose
This SRS defines the comprehensive requirements for transforming the Form Management System from a monolithic synchronous architecture to an event-driven, multi-tenant, scalable platform.

### 1.2 Scope
Phase 1 establishes the foundational infrastructure required for all subsequent phases (P2: Automation, P3: AI, P4: Enterprise). This includes:
- Event-driven architecture with asynchronous task processing
- Multi-tenancy support with data isolation
- Scalable background job processing
- Horizontal scalability readiness

### 1.3 Intended Audience
- Backend Developers
- DevOps Engineers
- System Architects
- QA Engineers
- Product Managers

### 1.4 Success Criteria
- API response time reduced from ~500ms to <100ms for form submissions
- Complete tenant isolation verified through security testing
- Zero data leakage between tenants
- Graceful degradation when background workers are unavailable
- 100% backward compatibility with existing API contracts

---

## 2. Overall Description

### 2.1 Product Perspective
The current system processes all operations synchronously, causing:
- **Performance Bottlenecks**: Email sending, file exports, and notifications block API responses
- **Scalability Limitations**: Single-threaded request handling limits throughput
- **Coupling Issues**: Core logic tightly coupled with side effects (emails, webhooks)
- **Multi-Org Barriers**: No organizational data isolation

Phase 1 addresses these fundamental architectural constraints.

### 2.2 Product Functions
1. **Event Bus System**: Decouple core operations from side effects
2. **Multi-Tenancy Framework**: Isolate data by organization
3. **Asynchronous Task Queue**: Process heavy operations in background
4. **Tenant-Scoped Middleware**: Automatic tenant resolution and enforcement

### 2.3 User Classes and Characteristics
- **System Administrators**: Manage tenants and infrastructure
- **Organization Owners**: Each tenant's admin managing their forms
- **Form Users**: End users submitting form responses
- **API Consumers**: External systems integrating via API

### 2.4 Operating Environment
- **Backend**: Flask/Python 3.11+
- **Database**: MongoDB with tenant-scoped queries
- **Message Broker**: Redis 7.0+
- **Task Queue**: Celery 5.3+
- **Container**: Docker, Docker Compose
- **Deployment**: Linux-based systems

---

## 3. System Features

### 3.1 Event-Driven Architecture

#### 3.1.1 Description
Implement a publish-subscribe event system to decouple core operations from side effects.

#### 3.1.2 Functional Requirements

**FR-1.1**: The system SHALL emit events using Python signals (Blinker)
- **Priority**: Critical
- **Events**: `form_created`, `form_updated`, `response_submitted`, `response_updated`, `form_archived`

**FR-1.2**: The system SHALL provide event metadata
- **Priority**: Critical
- **Metadata**: `event_id` (UUID), `timestamp`, `tenant_id`, `user_id`, `entity_id`, `payload`

**FR-1.3**: Multiple listeners SHALL subscribe to the same event
- **Priority**: High
- **Use Case**: Email notification + Webhook trigger + Audit log on single submission

**FR-1.4**: Event emission SHALL NOT block the request-response cycle
- **Priority**: Critical
- **Implementation**: Fire-and-forget pattern

**FR-1.5**: Events SHALL be processed by background workers
- **Priority**: Critical
- **Technology**: Celery workers consuming from Redis queues

#### 3.1.3 Non-Functional Requirements

**NFR-1.1**: Event emission overhead SHALL be <5ms
**NFR-1.2**: Event delivery SHALL be at-least-once (retry on failure)
**NFR-1.3**: Event processing failures SHALL NOT affect API availability

---

### 3.2 Multi-Tenancy Support

#### 3.2.1 Description
Implement organizational data isolation to support SaaS model with multiple customers.

#### 3.2.2 Functional Requirements

**FR-2.1**: All entities SHALL include `tenant_id` field
- **Priority**: Critical
- **Affected Models**: `User`, `Form`, `FormVersion`, `FormResponse`, `WorkflowLog`, `File`

**FR-2.2**: Database queries SHALL automatically filter by tenant
- **Priority**: Critical
- **Implementation**: Query middleware/decorators

**FR-2.3**: Unique constraints SHALL be tenant-scoped
- **Priority**: Critical
- **Examples**: 
  - `(tenant_id, email)` for Users
  - `(tenant_id, slug)` for Forms
  - `(tenant_id, form_id, version)` for FormVersions

**FR-2.4**: Tenant resolution SHALL support multiple methods
- **Priority**: High
- **Methods**:
  1. HTTP Header: `X-Tenant-ID`
  2. JWT Claim: `tenant_id`
  3. Subdomain: `{tenant}.forms.example.com`
  4. Path Parameter: `/api/v1/{tenant_id}/forms`

**FR-2.5**: Default tenant SHALL be assigned to existing data
- **Priority**: Critical
- **Value**: `default` or organization UUID from config

**FR-2.6**: Cross-tenant operations SHALL be explicitly prohibited
- **Priority**: Critical
- **Exception**: Super-admin role with explicit scope elevation

#### 3.2.3 Non-Functional Requirements

**NFR-2.1**: Tenant resolution SHALL complete in <2ms
**NFR-2.2**: Data isolation SHALL be verified through automated security tests
**NFR-2.3**: Migration script SHALL preserve 100% of existing data with audit trail

---

### 3.3 Asynchronous Task Processing

#### 3.3.1 Description
Move heavy operations to background workers using Celery task queue.

#### 3.3.2 Functional Requirements

**FR-3.1**: The system SHALL define task categories
- **Priority**: High
- **Categories**:
  - `email`: Email notifications (low priority, can be delayed)
  - `export`: CSV/Excel exports (medium priority)
  - `webhook`: External API calls (high priority, time-sensitive)
  - `analytics`: Data aggregation (low priority, batch)

**FR-3.2**: Tasks SHALL include retry logic
- **Priority**: Critical
- **Strategy**: Exponential backoff (1m, 5m, 15m, 1h)
- **Max Retries**: 3 for most tasks, 10 for webhooks

**FR-3.3**: Tasks SHALL respect tenant context
- **Priority**: Critical
- **Implementation**: Pass `tenant_id` as task parameter

**FR-3.4**: Tasks SHALL log execution status
- **Priority**: High
- **States**: PENDING, STARTED, SUCCESS, FAILURE, RETRY

**FR-3.5**: Failed tasks SHALL be stored for investigation
- **Priority**: High
- **Storage**: Database collection `task_failures` with full traceback

**FR-3.6**: The system SHALL provide task status API
- **Priority**: Medium
- **Endpoint**: `GET /api/v1/tasks/{task_id}/status`

#### 3.3.3 Non-Functional Requirements

**NFR-3.1**: Task queue SHALL handle 1000+ tasks/minute
**NFR-3.2**: Worker pool SHALL be horizontally scalable
**NFR-3.3**: Task failure rate SHALL be <1% under normal conditions

---

### 3.4 Middleware & Request Pipeline

#### 3.4.1 Description
Implement request middleware for automatic tenant scoping and context injection.

#### 3.4.2 Functional Requirements

**FR-4.1**: TenantMiddleware SHALL execute before route handlers
- **Priority**: Critical
- **Order**: After authentication, before business logic

**FR-4.2**: Middleware SHALL validate tenant existence
- **Priority**: High
- **Response**: 404 if tenant not found, 403 if access denied

**FR-4.3**: Middleware SHALL inject tenant context into Flask `g` object
- **Priority**: Critical
- **Access**: Available as `g.tenant_id` in all routes

**FR-4.4**: Middleware SHALL handle missing tenant gracefully
- **Priority**: High
- **Behavior**: Return 400 with clear error message

**FR-4.5**: Middleware SHALL log tenant access patterns
- **Priority**: Medium
- **Purpose**: Security auditing and usage analytics

---

## 4. Data Requirements

### 4.1 Database Schema Changes

#### 4.1.1 New Fields

**All Collections**:
```python
tenant_id: str  # UUID or organization identifier
created_at: datetime  # Already exists, ensure indexed
updated_at: datetime  # Already exists, ensure indexed
```

**User Collection**:
```python
tenant_id: str
email: str
# Unique index: (tenant_id, email)
```

**Form Collection**:
```python
tenant_id: str
slug: str
# Unique index: (tenant_id, slug)
```

**FormResponse Collection**:
```python
tenant_id: str
form_id: ObjectId
# Index: (tenant_id, form_id, created_at)
```

#### 4.1.2 Migration Requirements

**M-1**: Backfill `tenant_id` to all existing documents
- **Default Value**: `"default"` or from environment variable
- **Validation**: Ensure no document left without `tenant_id`

**M-2**: Create unique indexes after backfill
- **Safety**: Run in background with `background=True`
- **Verification**: Check for index violations before creation

**M-3**: Preserve audit trail
- **Log**: Record migration timestamp and document counts per collection
- **Backup**: Create full database dump before migration

---

### 4.2 Event Schema

#### 4.2.1 Event Structure
```python
{
    "event_id": "uuid-v4",
    "event_type": "response_submitted",
    "timestamp": "2026-01-09T12:00:00Z",
    "tenant_id": "org-abc-123",
    "user_id": "user-xyz-456",
    "entity_id": "response-789",
    "payload": {
        "form_id": "form-001",
        "form_version": 2,
        "data": {...}
    },
    "metadata": {
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    }
}
```

---

## 5. External Interface Requirements

### 5.1 API Changes

#### 5.1.1 Backward Compatibility
- **Requirement**: All existing v1 endpoints MUST continue to work without changes
- **Implementation**: Default tenant for v1 requests without `X-Tenant-ID` header

#### 5.1.2 New Headers
**Request Headers**:
- `X-Tenant-ID`: Optional for v1, required for v2 (future)
- `X-Request-ID`: Optional, for request tracing

**Response Headers**:
- `X-Task-ID`: Returned when async task is queued
- `X-Tenant-ID`: Echo back the resolved tenant

#### 5.1.3 Error Responses
**400 Bad Request**: Missing or invalid tenant
```json
{
    "error": "TENANT_REQUIRED",
    "message": "X-Tenant-ID header is required",
    "code": 400
}
```

**404 Not Found**: Tenant doesn't exist
```json
{
    "error": "TENANT_NOT_FOUND",
    "message": "Tenant 'org-123' does not exist",
    "code": 404
}
```

---

## 6. Non-Functional Requirements

### 6.1 Performance
- **P-1**: API response time (submit) < 100ms (90th percentile)
- **P-2**: Tenant resolution < 2ms
- **P-3**: Event emission < 5ms
- **P-4**: Support 500 concurrent requests per server instance

### 6.2 Scalability
- **S-1**: Horizontal scaling of web servers (stateless)
- **S-2**: Horizontal scaling of Celery workers
- **S-3**: Support for 1000+ tenants
- **S-4**: Support for 100,000+ forms across all tenants

### 6.3 Reliability
- **R-1**: 99.9% uptime for API layer
- **R-2**: Graceful degradation when Redis is down (queue locally, process when available)
- **R-3**: Zero data loss during tenant migration
- **R-4**: Automatic reconnection to Redis/MongoDB

### 6.4 Security
- **SEC-1**: Complete tenant isolation (no cross-tenant data leakage)
- **SEC-2**: Audit logging for all tenant access patterns
- **SEC-3**: Rate limiting per tenant (configurable)
- **SEC-4**: Encrypted communication between components

### 6.5 Maintainability
- **M-1**: Comprehensive logging with correlation IDs
- **M-2**: Metrics for queue depth, task lag, error rates
- **M-3**: Health check endpoints for all services
- **M-4**: Documentation for all configuration parameters

---

## 7. System Constraints

### 7.1 Technical Constraints
- Must maintain Python 3.11+ compatibility
- MongoDB 5.0+ required for multi-document transactions
- Redis persistence must be configured (AOF or RDB)

### 7.2 Business Constraints
- Zero downtime deployment for existing customers
- 100% backward compatibility with v1 API
- Migration must complete within 4-hour maintenance window

---

## 8. Assumptions and Dependencies

### 8.1 Assumptions
- Redis is configured with persistence (data survives restarts)
- Existing data is clean (no orphaned references)
- Network latency between services < 10ms

### 8.2 Dependencies
- **External Services**: Redis, MongoDB
- **Python Packages**: `celery[redis]>=5.3`, `blinker>=1.6`, `redis>=4.5`
- **Infrastructure**: Docker Compose for development, Kubernetes for production

---

## 9. Acceptance Criteria

### 9.1 Feature Acceptance
- [ ] Form submission completes in <100ms (API returns 201)
- [ ] Email sent successfully in background (verify in logs)
- [ ] Tenant A cannot access Tenant B's data (security test passes)
- [ ] Redis failure does not crash API (queues tasks when Redis returns)
- [ ] All existing unit tests pass
- [ ] New integration tests pass (>90% coverage for new code)

### 9.2 Migration Acceptance
- [ ] All documents have `tenant_id` field
- [ ] Unique indexes created successfully
- [ ] No data loss (document count matches pre-migration)
- [ ] Existing API calls return identical responses

---

## 10. Appendices

### Appendix A: Glossary
- **Event Bus**: Publish-subscribe messaging system for decoupling components
- **Multi-Tenancy**: Architectural pattern for serving multiple organizations from single deployment
- **Graceful Degradation**: System continues functioning with reduced features when dependencies fail
- **Tenant**: Organization or customer using the SaaS platform

### Appendix B: References
- Flask Signals: https://flask.palletsprojects.com/en/latest/signals/
- Celery Documentation: https://docs.celeryproject.org/
- Multi-Tenancy Patterns: https://aws.amazon.com/solutions/multi-tenant-architectures/

---

**Revision History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-09 | Development Team | Initial SRS creation for Phase 1 |
