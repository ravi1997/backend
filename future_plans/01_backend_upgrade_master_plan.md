# Future Upgrade Plan: Form Management System v2.0 (Detailed Specification)

**Document Version:** 2.1  
**Date:** January 2026  
**Status:** Comprehensive Execution Blueprint  
**Goal:** Transform the monolithic form backend into an Event-Driven, AI-Powered, Enterprise-Grade Platform.

---

## 📅 Executive Summary & Roadmap

The v2.0 upgrade is designed to address scalability errors, manual workflow bottlenecks, and the need for intelligent data processing. This document breaks down the implementation into 4 sequential phases.

| Phase | Focus Area | Key Deliverables | Estimated Impact |
|:---:|:---|:---|:---|
| **P1** | **Foundation** | Event Bus, Multi-Tenancy, Celery Workers | Scalability, SaaS-Readiness |
| **P2** | **Automation** | Workflow Engine, Visual Builder, Approvals | 40% Reduction in Admin Time |
| **P3** | **Intelligence** | AI Form Gen, Semantic Search, PII Shield | 90% Faster Form Creation |
| **P4** | **Enterprise** | SSO, Webhooks, Audit Logs | Compliance & Corporate Adoption |

---

## 🚜 Phase 1: Foundation & Event-Driven Architecture

### 1. The Need (Justification)
*   **Scalability:** Current synchronous processing limits throughput. Heavy tasks (emails, exports) block API responses.
*   **Data Isolation:** "Multi-tenancy" is currently non-existent, making it impossible to serve multiple organizations securely.
*   **Decoupling:** To add features like Webhooks or AI without breaking the core `submit` function, we need an Event Bus.

### 2. Detailed Strategy
Shift from a Monolithic request-response cycle to an **Event-Driven Architecture**.
*   **Synchronous:** API validation, simple DB writes.
*   **Asynchronous:** Emails, Webhooks, AI processing, Workflow triggers.
*   **Tech Stack Addition:** `Celery` (Task Queue), `Redis` (Broker), `Blinker` (In-process Signals).

### 3. Changes Needed Checklist
*   [ ] **Infrastructure:** Spin up Redis container. Configure Celery in Flask app.
*   [ ] **Database Models:** 
    *   Add `tenant_id` (String/UUID) to `User`, `Form`, `FormResponse`.
    *   Create unique constraints on `(tenant_id, email)` and `(tenant_id, slug)`.
*   [ ] **Middleware:** Create `TenantMiddleware` to extract `X-Tenant-ID` or resolve from header/subdomain.
*   [ ] **Core Logic:** Inject `signal.send('response_submitted')` in `responses.py`.

### 4. Guide to Data Flow
**Old Flow:**
`User Request` -> `API` -> `Validate` -> `Save DB` -> `Send Email` -> `Return Response` (Slow)

**New Flow:**
1.  `User Request` -> `TenantMiddleware` (Sets scope) -> `API`
2.  `API` -> `Validate` -> `Save DB`
3.  `API` -> `Emit Signal('response_submitted')` -> `Return 201 Created` (Fast)
4.  `Background Worker` captures signal -> `Send Email` | `Trigger Webhook` | `Update Audit Log`

### 5. Step-by-Step Implementation Steps
1.  **Environment Setup**: Add `redis` and `celery` to `docker-compose.yml` and `requirements.txt`.
2.  **Model Migration**: Write a script to iterate all existing documents and assign a default `tenant_id` (e.g., "default_org").
3.  **Signal Framework**: Create `app/events/signals.py` defining core events (`form_created`, `response_submitted`).
4.  **Worker Config**: Create `celery_worker.py` entry point.
5.  **Refactor Routes**: Update `v1/form/responses.py` to remove inline email code and replace with `tasks.send_email.delay()`.

### 6. Testing Strategy
*   **Load Testing**: Verify API response time drops from ~500ms to <100ms for submissions.
*   **Isolation Test**: Create 2 tenants. Ensure User A in Tenant 1 cannot query Forms in Tenant 2.
*   **Worker Test**: Kill the Redis container, ensure API still accepts requests (graceful degradation), then process tasks when Redis returns.

---

## 🤖 Phase 2: Workflow Automation Engine

### 1. The Need
*   **Business Logic**: Users need things to *happen* when a form is submitted (e.g., "If expenses > $500, ask Manager approval").
*   **State Management**: Current responses are just static data points. They need a "State" (Draft -> Pending -> Approved).

### 2. Detailed Strategy
Implement a **Condition-Action Engine**.
*   **Triggers**: Events that start a flow (Submission, Update).
*   **Evaluator**: A safe logic engine that checks rules against the response JSON.
*   **Actions**: predefined tasks (Email, API Call, Update Status).

### 3. Changes Needed Checklist
*   [ ] **New Models**:
    *   `Workflow` (Name, TriggerType, Conditions: JSON, Actions: JSON)
    *   `WorkflowLog` (Execution history, success/fail status)
*   [ ] **Logic Engine**: Implement `RuleEvaluator` class (using complex usage of Python's AST or simple dict matching).
*   [ ] **Scheduler**: Celery Beat for time-based triggers (e.g., "3 days after submission").

### 4. Guide to Flow
1.  **Trigger**: `Signal('response_submitted')` fires.
2.  **Listener**: `WorkflowDispatcher` catches signal.
3.  **Lookup**: Finds all active `Workflows` for this Form.
4.  **Evaluation**: 
    *   Workflow A: "Is department == 'IT'?" (True) -> **Queue Action**
    *   Workflow B: "Is department == 'HR'?" (False) -> **Skip**
5.  **Execution**: Worker executes `SendSlackNotification(data)`.

### 5. Step-by-Step Implementation Steps
1.  **Schema Definition**: Define the JSON structure for storing rules (e.g., `{ "operator": "gt", "field": "amount", "value": 500 }`).
2.  **Evaluator Logic**: Write unit-tested functions to process these rules against response data.
3.  **Action Handlers**: Create `app/services/actions/` with classes for `EmailAction`, `UpdateStatusAction`.
4.  **API Routes**: Build CRUD endpoints for configuring Workflows (`/api/v2/workflows`).
5.  **Integration**: Hook `WorkflowDispatcher` into the Phase 1 Event Bus.

### 6. Testing Strategy
*   **Logic Matrix**: Test evaluator against every edge case (String matching, Number comparison, Date logic, Missing fields).
*   **Loop Prevention**: Ensure Workflow A triggering an update doesn't infinite-loop trigger Workflow A again.

---

## 🧠 Phase 3: AI Intelligence Layer

### 1. The Need
*   **Friction Reduction**: Manually dragging and dropping 50 fields is tedious. Users want to just say "Make me a survey".
*   **Insight**: Users have thousands of text responses but no quick way to find patterns.

### 2. Detailed Strategy
*   **Generative AI**: Use efficient prompts to convert Natural Language -> JSON Form Schema.
*   **RAG / Semantic Search**: Embed response text into specialized vectors to allow "meaning-based" searching.

### 3. Changes Needed Checklist
*   [ ] **Dependencies**: `langchain`, `openai` (or local LLM client), `chromadb` (or Pinecone).
*   [ ] **Vector Store**: Setup a local Vector DB container or cloud connection.
*   [ ] **New Service**: `AIService` class to handle prompt engineering and context management.

### 4. Guide to Flow (Generative)
1.  **User**: "Create a 5-step detailed medical onboarding form".
2.  **API**: `POST /ai/generate`
3.  **LLM Service**: enhancing prompt ("You are a JSON generator...") -> Calls LLM.
4.  **Validator**: Validates returned JSON against our `Form` schema (pydantic).
5.  **Result**: Returns valid JSON to frontend builder.

### 5. Step-by-Step Implementation Steps
1.  **Prompt Engineering**: Design system prompts that guarantee valid JSON output compatible with our renderer.
2.  **Integration**: Create the `generate` endpoint.
3.  **Embedding Pipeline**: Create a background task that runs on *every* new text response -> generates vector -> upserts to VectorDB.
4.  **Search API**: Update search endpoint to accept `query_text`, convert to vector, and query VectorDB.

### 6. Testing Strategy
*   **Hallucination Check**: Ensure generated forms always have valid field types (e.g., AI shouldn't invent a "mood-ring" field type).
*   **Privacy Test**: Ensure PII is not sent to the Vector DB or LLM unless strictly configured.

---

## 🏢 Phase 4: Enterprise Hardening

### 1. The Need
*   **Security Compliance**: Large orgs require Audit Trails and SSO.
*   **Ecosystem**: They need data to leave our system instantly (Webhooks).

### 2. Detailed Strategy
*   **SSO**: Use `Authlib` to support OIDC (Google/Microsoft) and SAML 2.0.
*   **Webhooks**: A robust "Subscriber" model with signature verification (HMAC).
*   **Audit**: A write-only append log for compliance.

### 3. Changes Needed Checklist
*   [ ] **SSO Handlers**: Login routes that redirect to IdP and handle callbacks.
*   [ ] **Webhook Dispatcher**: Retry logic with exponential backoff for failed endpoint hits.
*   [ ] **Audit Middleware**: Automatic logging of "Who changed What".

### 4. Guide to Flow (Webhooks)
1.  **Event**: Form Submitted.
2.  **Dispatcher**: Finds 3 subscribed Webhook URLs for this form.
3.  **Security**: Calculates `HMAC_SHA256(payload, secret)`.
4.  **Attempt 1**: POST payload + Signature headers.
5.  **Failure**: Target returns 500.
6.  **Retry**: Queue retry in 1 minute, then 5 mins, then 30 mins.

### 5. Step-by-Step Implementation Steps
1.  **SSO Routes**: Implement `/auth/login/sso/{provider}` and callback.
2.  **Webhook Models**: Create `WebhookSubscription` and `WebhookDeliveryLog`.
3.  **Retry Queue**: Configure a specific Celery queue for webhooks to avoid clogging the main worker.
4.  **Audit System**: Create a decorator `@audit_action('action_name')` to apply to sensitive admin routes.

### 6. Testing Strategy
*   **Chaos Testing**: Point webhooks to a chaotic endpoint (random timeouts/500s) and verify retry logic.
*   **Forensics**: Perform a sequence of actions, then query the Audit Log to re-construct the timeline exactly.

---

## 🚦 Final Migration Guide

When deploying v2.0:
1.  **Stop Writes**: Maintenance mode.
2.  **Backup**: Full Mongo dump.
3.  **Phase 1 Script**: Run `migrate_tenants.py` to backfill `tenant_id`.
4.  **Deploy**: Push new code with Event Bus.
5.  **Phase 3 Script**: Run `backfill_embeddings.py` (Background) to index old data.
6.  **Resume**: Open traffic.
