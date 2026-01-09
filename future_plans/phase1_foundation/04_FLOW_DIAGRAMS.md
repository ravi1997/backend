# Flow Diagrams: Phase 1 Foundation
## System Architecture & Data Flows

**Phase:** P1 - Foundation  
**Version:** 1.0  

---

## 1. Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Applications                      │
│           (Web Frontend, Mobile App, API Clients)            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Load Balancer / API Gateway                │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│  Flask App      │         │  Flask App      │
│  Instance 1     │         │  Instance 2     │
│                 │         │                 │
│ ┌─────────────┐ │         │ ┌─────────────┐ │
│ │   Tenant    │ │         │ │   Tenant    │ │
│ │ Middleware  │ │         │ │ Middleware  │ │
│ └──────┬──────┘ │         │ └──────┬──────┘ │
│        │        │         │        │        │
│ ┌──────▼──────┐ │         │ ┌──────▼──────┐ │
│ │   Routes    │ │         │ │   Routes    │ │
│ │   (API)     │ │         │ │   (API)     │ │
│ └──────┬──────┘ │         │ └──────┬──────┘ │
│        │        │         │        │        │
│ ┌──────▼──────┐ │         │ ┌──────▼──────┐ │
│ │   Event     │ │         │ │   Event     │ │
│ │  Emitter    │ │         │ │  Emitter    │ │
│ └─────────────┘ │         │ └─────────────┘ │
└────┬───────┬────┘         └────┬───────┬────┘
     │       │                   │       │
     │       └────────┬──────────┘       │
     ▼                ▼                  ▼
┌─────────┐    ┌──────────────┐   ┌──────────┐
│ MongoDB │    │    Redis     │   │  Celery  │
│         │    │  (Message    │   │ Workers  │
│(Tenant- │    │   Broker)    │   │ (1..N)   │
│ Scoped) │    └──────────────┘   └──────────┘
└─────────┘
```

---

## 2. Request Flow with Tenant Resolution

```
┌──────┐
│Client│
└───┬──┘
    │ 1. HTTP Request
    │    GET /api/v1/forms
    │    Headers: X-Tenant-ID: org-abc
    ▼
┌───────────────────────────────┐
│   TenantMiddleware            │
├───────────────────────────────┤
│ 2. Extract tenant_id          │
│    - Check X-Tenant-ID header │
│    - Check JWT claim          │
│    - Use default (fallback)   │
└───────┬───────────────────────┘
        │ 3. Validate tenant exists
        ▼
┌───────────────────────────────┐
│   Tenant.exists(org-abc)?     │
└───┬─────────────────┬─────────┘
    │ YES             │ NO
    ▼                 ▼
┌────────────┐   ┌─────────────┐
│Set g.tenant│   │Return 404   │
│= org-abc   │   │Tenant not   │
└─────┬──────┘   │found        │
      │          └─────────────┘
      │ 4. Continue to route handler
      ▼
┌───────────────────────────────┐
│   Route Handler               │
│   @forms_bp.route()           │
├───────────────────────────────┤
│ 5. Query with tenant scope    │
│    Form.list_forms()          │
│    → WHERE tenant_id='org-abc'│
└───────┬───────────────────────┘
        │
        ▼
┌───────────────────────────────┐
│   MongoDB Query               │
│   db.forms.find({             │
│     tenant_id: 'org-abc'      │
│   })                          │
└───────┬───────────────────────┘
        │
        ▼
┌───────────────────────────────┐
│   6. Return JSON Response     │
│   200 OK                      │
│   [                           │
│     {id: 1, title: "..."},    │
│     {id: 2, title: "..."}     │
│   ]                           │
└───────────────────────────────┘
```

---

## 3. Event-Driven Form Submission Flow

```
┌──────┐
│Client│
└───┬──┘
    │ 1. POST /api/v1/forms/123/submit
    │    {name: "John", email: "john@test.com"}
    │    Headers: X-Tenant-ID: org-abc
    ▼
┌────────────────────────────────────────┐
│ TenantMiddleware → Set g.tenant_id     │
└────────────────┬───────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│ Route: submit_response()               │
├────────────────────────────────────────┤
│ 2. Validate form data                  │
│    - Check required fields             │
│    - Run custom validations            │
└────────────────┬───────────────────────┘
                 │ VALID
                 ▼
┌────────────────────────────────────────┐
│ 3. Save Response to MongoDB            │
│    FormResponse.create({               │
│      tenant_id: 'org-abc',             │
│      form_id: 123,                     │
│      data: {...}                       │
│    })                                  │
└────────────────┬───────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│ 4. Emit Event (NON-BLOCKING)           │
│    EventDispatcher.emit(               │
│      signal=response_submitted,        │
│      entity_id=response_id,            │
│      payload={form_id, data}           │
│    )                                   │
└────────────────┬───────────────────────┘
                 │ <5ms overhead
                 ▼
┌────────────────────────────────────────┐
│ 5. Return Response IMMEDIATELY         │
│    201 Created                         │
│    {response_id: "xyz-789"}            │
└────────────────────────────────────────┘
                 ║
                 ║ MEANWHILE (Async)...
                 ▼
┌────────────────────────────────────────┐
│ Event Listeners (In-Process)           │
├────────────────────────────────────────┤
│ @response_submitted.connect            │
│ def on_response_submitted(...):        │
│   - Queue email task                   │
│   - Queue webhook task                 │
│   - Log to audit trail                 │
└────────────────┬───────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌───────────────┐  ┌──────────────────┐
│ Redis Queue   │  │ Celery Workers   │
│ (Broker)      │  │                  │
│               │  │ 6. Process Tasks │
│ Tasks:        │  │    - send_email  │
│ - send_email  │  │    - trigger_    │
│ - webhook     │  │      webhook     │
└───────────────┘  └──────────────────┘
```

**Key Benefit**: API responds in <100ms, heavy tasks run in background

---

## 4. Multi-Tenancy Data Isolation

```
┌─────────────────────────────────────────────┐
│           MongoDB Database                  │
├─────────────────────────────────────────────┤
│                                             │
│  Collection: forms                          │
│  ┌───────────────────────────────────────┐ │
│  │ {                                     │ │
│  │   _id: ObjectId("..."),               │ │
│  │   tenant_id: "org-abc",     ◄─────────┼─┼─ Tenant Filter
│  │   title: "Contact Form",              │ │
│  │   slug: "contact",                    │ │
│  │   ...                                 │ │
│  │ }                                     │ │
│  └───────────────────────────────────────┘ │
│  ┌───────────────────────────────────────┐ │
│  │ {                                     │ │
│  │   _id: ObjectId("..."),               │ │
│  │   tenant_id: "org-xyz",     ◄─────────┼─┼─ Different Tenant
│  │   title: "Survey",                    │ │
│  │   slug: "contact",  ◄─────────────────┼─┼─ Same slug OK!
│  │   ...                                 │ │
│  │ }                                     │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Indexes:                                   │
│  - {tenant_id: 1}                           │
│  - {tenant_id: 1, slug: 1} [UNIQUE]  ◄──────┼─ Per-tenant uniqueness
│  - {tenant_id: 1, created_at: -1}           │
└─────────────────────────────────────────────┘

Query Example:
  db.forms.find({
    tenant_id: "org-abc",    ◄─── Always included
    status: "active"
  })

Result: Only org-abc's forms returned
```

---

## 5. Celery Task Processing Flow

```
┌─────────────────────────────────────────────┐
│ Flask App (Event Listener)                  │
├─────────────────────────────────────────────┤
│ @response_submitted.connect                 │
│ def on_response_submitted(event_data):      │
│     send_email.delay(                       │
│         tenant_id='org-abc',                │
│         to_email='admin@org.com',           │
│         subject='New Response',             │
│         body='...'                          │
│     )                                       │
└────────────────────┬────────────────────────┘
                     │ 1. Queue task
                     ▼
┌─────────────────────────────────────────────┐
│ Redis (Message Broker)                      │
├─────────────────────────────────────────────┤
│ Queue: celery                               │
│ ┌─────────────────────────────────────────┐ │
│ │ Task ID: abc-123                        │ │
│ │ Name: app.tasks.email_tasks.send_email  │ │
│ │ Args: [tenant_id, to, subject, body]    │ │
│ │ Status: PENDING                         │ │
│ │ Retry: 0/3                              │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────┘
                      │ 2. Worker picks up
                      ▼
┌─────────────────────────────────────────────┐
│ Celery Worker (Process 1)                   │
├─────────────────────────────────────────────┤
│ @celery.task                                │
│ def send_email(tenant_id, to, subject, ...):│
│     try:                                    │
│         EmailService.send(...)              │
│         return {'status': 'success'}        │
│     except Exception as exc:                │
│         raise self.retry(                   │
│             exc=exc,                        │
│             countdown=60  # 1 min           │
│         )                                   │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │ SUCCESS                 │ FAILURE
        ▼                         ▼
┌──────────────┐        ┌───────────────────┐
│ Update Redis │        │ Retry Logic       │
│ Status:      │        │ - Wait 60s        │
│ SUCCESS      │        │ - Retry (1/3)     │
└──────────────┘        │ - Exponential     │
                        │   backoff         │
                        └─────┬─────────────┘
                              │ After 3 retries
                              ▼
                        ┌───────────────────┐
                        │ Store in          │
                        │ task_failures     │
                        │ collection        │
                        └───────────────────┘
```

---

## 6. Migration Flow

```
┌─────────────────────────────────────────────┐
│ 1. PRE-MIGRATION                            │
├─────────────────────────────────────────────┤
│ - Enable maintenance mode                   │
│ - Stop application servers                  │
│ - Full database backup                      │
│   mongodump --out=/backup/pre-migration     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ 2. MIGRATION SCRIPT                         │
├─────────────────────────────────────────────┤
│ For each collection:                        │
│   - Create backup (timestamped)             │
│   - Add tenant_id='default' to all docs     │
│   - Verify document count matches           │
│   - Create indexes (background)             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ 3. VERIFICATION                             │
├─────────────────────────────────────────────┤
│ - Count documents with tenant_id            │
│ - Check unique constraints work             │
│ - Run sample queries                        │
│ - Test cross-tenant isolation               │
└────────────────┬────────────────────────────┘
                 │ ALL PASS
                 ▼
┌─────────────────────────────────────────────┐
│ 4. POST-MIGRATION                           │
├─────────────────────────────────────────────┤
│ - Start Redis                               │
│ - Start Celery workers                      │
│ - Start application servers                 │
│ - Disable maintenance mode                  │
│ - Monitor logs for 30 minutes               │
└─────────────────────────────────────────────┘

If migration fails:
┌─────────────────────────────────────────────┐
│ ROLLBACK PROCEDURE                          │
├─────────────────────────────────────────────┤
│ - Restore from backup collections           │
│ - Verify data integrity                     │
│ - Drop failed migration changes             │
│ - Restart with old code                     │
└─────────────────────────────────────────────┘
```

---

## 7. Tenant Resolution Decision Tree

```
                  ┌──────────────┐
                  │HTTP Request  │
                  └──────┬───────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ X-Tenant-ID header   │
              │ present?             │
              └────┬────────────┬────┘
                   │ YES        │ NO
                   ▼            ▼
            ┌─────────┐  ┌──────────────┐
            │Use header│  │ JWT present? │
            │ value    │  └───┬─────┬────┘
            └────┬─────┘      │YES  │NO
                 │            ▼     ▼
                 │     ┌──────────┐ ┌──────────┐
                 │     │Extract   │ │Use       │
                 │     │tenant_id │ │DEFAULT_  │
                 │     │from JWT  │ │TENANT_ID │
                 │     └────┬─────┘ └────┬─────┘
                 │          │            │
                 └──────────┴────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Tenant exists &  │
                  │ is active?       │
                  └────┬────────┬────┘
                       │ YES    │ NO
                       ▼        ▼
                ┌─────────┐  ┌────────┐
                │Set      │  │Return  │
                │g.tenant │  │404 or  │
                │Continue │  │403     │
                └─────────┘  └────────┘
```

---

## 8. Scale-Out Architecture (Production)

```
┌──────────────────────────────────────────────────────────┐
│                    Load Balancer                         │
│                  (nginx/AWS ALB)                         │
└────────┬──────────────────────────┬────────────┬─────────┘
         │                          │            │
         ▼                          ▼            ▼
┌──────────────┐         ┌──────────────┐  ┌──────────────┐
│ Flask App 1  │         │ Flask App 2  │  │ Flask App N  │
│ (Stateless)  │         │ (Stateless)  │  │ (Stateless)  │
└──────┬───────┘         └──────┬───────┘  └──────┬───────┘
       │                        │                 │
       └────────────┬───────────┴─────────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌──────────────────┐   ┌──────────────────┐
│  MongoDB Cluster │   │  Redis Cluster   │
│  (Replica Set)   │   │  (Sentinel)      │
│  - Primary       │   │  - Master        │
│  - Secondary 1   │   │  - Replica 1     │
│  - Secondary 2   │   │  - Replica 2     │
└──────────────────┘   └────────┬─────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
           ┌──────────────┐       ┌──────────────┐
           │Celery Worker │       │Celery Worker │
           │    Pool 1    │       │    Pool N    │
           │ (4 processes)│       │(4 processes) │
           └──────────────┘       └──────────────┘
```

**Capacity Planning:**
- Each Flask instance: 100 concurrent requests
- Each Celery worker: 4-8 concurrent tasks
- MongoDB: 10K operations/sec
- Redis: 100K operations/sec

---

**Next Document:** [Implementation Checklist](./05_CHECKLIST.md)
