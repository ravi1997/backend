# Future Upgradition Plan (Form Management System v2.0)

**Document Version:** 2.0  
**Date:** January 2026  
**Status:** Planning / Draft  
**Target:** Enterprise-Grade, AI-Enhanced Form Automation Platform

---

## 1. Introduction

This document serves as the **Strategic Upgrade Plan** and **Software Requirements Specification (SRS)** for the next major version (v2.0) of the Form Management System. 

**Assumptions:** 
- All requirements in `SRS.md` (v1.0) are fully implemented.
- The system currently supports basic form creation, response collection, and simple role-based access.

**Goals for v2.0:**
1.  **To Intelligent Automation:** Moving from passive data collection to active, event-driven workflows.
2.  **AI-First Experience:** Leveraging LLMs for form creation, data analysis, and anomaly detection.
3.  **Enterprise Scalability:** Supporting multi-tenancy, advanced security/compliance, and high-volume triggers.
4.  **Integration Ecosystem:** Seamless connectivity with external systems via Webhooks and API Connectors.

---

## 2. New Software Requirements Specification (SRS v2.0)

### 2.1 Module A: Advanced Workflow Automation Engine

**Purpose:** Enable complex, multi-stage processes triggered by form submissions or temporal events.

#### FR-WORKFLOW-001: Visual Workflow Builder
*   **Description:** A backend service to define state machines for form data.
*   **Capabilities:**
    *   **Triggers:** Form Submission, Form Update, Scheduled Time, External API Event.
    *   **Conditions:** Logic evaluation based on response data (e.g., `amount > 1000 AND risk_score == 'High'`).
    *   **Actions:** Send Email, PDF Generation, HTTP Webhook, Update Remote Record, Assign Task.
*   **Data Model:** `Workflow`, `Trigger`, `Action`, `ExectuionLog`.

#### FR-WORKFLOW-002: Approval Chains
*   **Description:** Built-in support for hierarchical approval processes.
*   **Capabilities:**
    *   **Stages:** Draft -> Manager Review -> Finance Approval -> Finalized.
    *   **Assignments:** Assign reviews to specific Users or Roles.
    *   **Notifications:** Email/In-app alerts for pending approvals.
*   **Logic:** If rejected, return to previous stage or 'Draft' with comments.

#### FR-WORKFLOW-003: Time-Based Triggers (SLA Management)
*   **Description:** Automations based on time elapsed since submission.
*   **Use Case:** Send reminder email if approval is pending for > 72 hours.
*   **Implementation:** Periodic task scheduler (Celery/Beat).

---

### 2.2 Module B: AI Intelligence Layer

**Purpose:** Integrate Generative AI and NLP to drastically reduce manual effort.

#### FR-AI-001: Generative Form Creation
*   **Description:** Generate complete form structures (JSON Schema) from natural language prompts.
*   **Endpoint:** `POST /api/v2/ai/generate-form`
*   **Input:** "Create a medical history form for cardiology patients."
*   **Output:** Full JSON with Sections, Questions, Validation Rules, and Options.

#### FR-AI-002: Semantic Search & Natural Language Query (NLQ)
*   **Description:** Search responses using meaning rather than exact keywords.
*   **Mechanism:** Vector embeddings (e.g., OpenAI embeddings + Vector DB).
*   **Example Query:** "Show me all patients who reported explicit chest pain symptoms." (Matches "severe angina", "chest tightness").

#### FR-AI-003: Automated Summary & Sentiment Analysis
*   **Description:** Auto-generate summaries for long-text responses.
*   **Output:** a `summary` field and `sentiment_score` (-1 to 1) attached to response metadata.

#### FR-AI-004: PII/PHI Redaction Shield
*   **Description:** Real-time AI scanning of text inputs to detect and mask PII (SSN, Phone, Email) before storage if configured.

---

### 2.3 Module C: Enterprise Infrastructure (Multi-Tenancy & Compliance)

**Purpose:** Support SaaS distribution and strict compliance standards (HIPAA/GDPR).

#### FR-ENT-001: Native Multi-Tenancy
*   **Description:** Logical isolation of data per Organization (Tenant).
*   **Architecture:** `OrganizationID` on every collection (Users, Forms, Responses).
*   **Scoping:** Superadmins see all; Org Admins see only their tenant's data.

#### FR-ENT-002: Enterprise SSO (SAML/OIDC)
*   **Description:** Support for Okta, Azure AD, and Google Workspace logical login.
*   **Integration:** Map Identity Provider (IdP) groups to System Roles.

#### FR-ENT-003: Immutable Audit Logs
*   **Description:** Forensic-grade logging of *every* read/write action.
*   **Storage:** Write-optimized collection or external service (e.g., CloudWatch, Splunk).
*   **Fields:** `Actor`, `Action`, `Resource`, `OldValue`, `NewValue`, `IP`, `Timestamp`.

#### FR-ENT-004: Data Retention Policies
*   **Description:** Automated cleanup rules.
*   **Example:** "Hard delete responses older than 7 years", "Anonymize users 30 days after termination".

---

### 2.4 Module D: Integration & Connectivity

#### FR-INT-001: Outbound Webhooks
*   **Description:** Real-time JSON POST to registered URLs on events.
*   **Events:** `form.submitted`, `response.approved`, `user.created`.
*   **Security:** HMAC signatures (header `X-Form-Signature`) to verify payload integrity.

#### FR-INT-002: Dynamic Data Sources (External Options)
*   **Description:** Dropdowns that fetch options from external APIs at runtime.
*   **Config:** `field_api_call` with customizable Headers/Auth.
*   **Caching:** Redis caching of external responses for performance.

---

## 3. detailed Background Implementation Plan (Backend)

The backend upgrade will be executed in **4 Phases**.

### Phase 1: Foundation & Architecture Refactoring
**Goal:** Prepare the codebase for scale and event-driven logic.

1.  **Event Bus Implementation:**
    *   **Action:** Introduce `blinker` signals or a message broker (RabbitMQ/Redis) for decoupled events.
    *   **Reason:** Creating a response should emit a `response_created` event, which listeners (Audit, Webhook, Workflow) consume asynchronously.
2.  **Database Migration for Multi-Tenancy:**
    *   **Action:** Add `organization_id` index to all core models (`User`, `Form`, `FormResponse`).
    *   **Action:** Update all queries to implicitly filter by `current_user.organization_id`.
3.  **Upgrade Tech Stack:**
    *   Ensure Python 3.12+ compatibility.
    *   Introduce `Celery` or `RQ` for background task processing (required for Webhooks/AI).

### Phase 2: The Workflow Engine
**Goal:** Implement the "Active" part of the system.

1.  **Workflow Model Design:**
    *   Create schemas for `Workflow`, `WorkflowStep`, and `WorkflowExecution`.
2.  **Execution Engine:**
    *   Build a Celery worker that processes `WorkflowExecution` tasks.
    *   Implement "Action Handlers": `EmailHandler`, `WebhookHandler`, `UpdateFieldHandler`.
    *   Implement "Condition Evaluator": Safe Python expression evaluation (using `AST` or `simpleeval`) for logic checks.
3.  **Approval State Management:**
    *   Add `status` field to `FormResponse` (Draft, Pending, Approved, Rejected).
    *   Create endpoints for `approve_response` / `reject_response` that trigger the next workflow step.

### Phase 3: AI Service Integration
**Goal:** Connect the system to LLMs and Vector Stores.

1.  **LLM Connector Service:**
    *   Create an abstraction layer (`AIService`) to swap providers (OpenAI, Anthropic, Local Llama).
    *   Implement `generate_form_schema(prompt)` prompt engineering pipelines.
2.  **Vector Store Setup:**
    *   Deploy a vector database sidecar (e.g., Qdrant or ChromaDB) or use a cloud service (Pinecone).
    *   Create a pipeline to embed `FormResponse` text data upon submission and update the vector index.
3.  **Search API Upgrade:**
    *   Modify `/api/v1/form/{id}/responses/search` to accept a `semantic_query` parameter.
    *   If present, perform vector similarity search instead of Mongo regex.

### Phase 4: Enterprise Hardening & API Gateway
**Goal:** Security, Compliance, and Integrations.

1.  **SSO Implementation:**
    *   Integrate `authlib` for OIDC/SAML support.
    *   Create `SSOConfiguration` model for Tenant-specific IdP settings.
2.  **Webhook Dispatcher:**
    *   Create `WebhookSubscription` model (Url, Events, Secrets).
    *   Implement reliable delivery with exponential backoff retries (using Celery).
3.  **Audit Service:**
    *   Implement middleware that captures every modification.
    *   Serialize `diff` of changes (Request vs DB state).
    *   Expose `/api/v2/audit-logs` endpoint for Admins.

---

## 4. API Endpoint Changes (Preview)

### New Endpoints
*   `POST /api/v2/workflows/` - Create a new automation workflow.
*   `POST /api/v2/ai/generate` - AI Form Generation.
*   `POST /api/v2/ai/analyze` - Analyze response sentiment/content.
*   `GET /api/v2/audit-logs` - Retrieve system audit trail.
*   `POST /api/v2/webhooks/subscribe` - Register an external webhook.

### Modified Endpoints
*   `GET /api/v1/form/{top}/responses` - Now requires `Organization-ID` header (implied in JWT).
*   `POST /api/v1/auth/login` - Added `sso_redirect` logic.

---

## 5. Migration Strategy

1.  **Data Backfill:**
    *   Script to assign default `OrganizationID` to all existing legacy data.
    *   Script to generate embeddings for existing text responses (batch job).
2.  **Compatibility:**
    *   v1 API endpoints remain fully backward compatible.
    *   New v2 namespace for advanced features.
