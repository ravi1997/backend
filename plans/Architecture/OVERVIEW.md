# Architecture & Diagrams

## 1. As-Is System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Frontend]
        MOBILE[Mobile App]
    end
    
    subgraph "API Gateway (Flask Middleware)"
        CORS[CORS Middleware]
        COMPRESS[Compression]
        JWT[JWT Auth]
    end
    
    subgraph "Backend Services (Blueprints)"
        AUTH[Authentication Service]
        USER[User Management]
        FORM[Form Management]
        VERSION[Versioning Engine]
        RESPONSE[Response Handler]
        AI[AI Service]
        WORKFLOW[Workflow Engine]
        EXPORT[Export Service]
    end
    
    subgraph "Data Layer"
        MONGO[(MongoDB)]
        POSTGRES[(PostgreSQL - Metadata/SQLAlchemy)]
        FS[File Storage]
    end
    
    subgraph "External Integrations"
        OLLAMA[Ollama - Local LLM]
        SMS[SMS Gateway]
    end
    
    WEB --> CORS
    MOBILE --> CORS
    CORS --> COMPRESS --> JWT
    JWT --> AUTH
    JWT --> USER
    JWT --> FORM
    JWT --> RESPONSE
    JWT --> AI
    JWT --> WORKFLOW
    JWT --> EXPORT
    
    AUTH --> MONGO
    USER --> MONGO
    FORM --> MONGO
    VERSION --> MONGO
    RESPONSE --> MONGO
    AI --> OLLAMA
    WORKFLOW --> MONGO
    AUTH --> SMS
```

## 2. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    USER ||--o{ FORM : "creates"
    FORM ||--o{ FORM_VERSION : "has"
    FORM_VERSION ||--o{ SECTION : "contains"
    SECTION ||--o{ QUESTION : "contains"
    QUESTION ||--o{ OPTION : "has"
    FORM ||--o{ FORM_RESPONSE : "receives"
    USER ||--o{ FORM_RESPONSE : "submits"
    FORM_RESPONSE ||--o{ RESPONSE_HISTORY : "tracks"
    WORKFLOW ||--|| FORM : "triggered_by"
    WORKFLOW ||--o{ WORKFLOW_ACTION : "executes"
```

## 3. Data Flow Diagram (DFD) - Submission Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Validation
    participant AI
    participant DB
    participant Workflow
    
    User->>API: POST /form/{id}/responses
    API->>Validation: Validate data vs Schema
    Validation-->>API: OK
    API->>AI: Scan for PII/Moderation (Async potential)
    AI-->>API: Results
    API->>DB: Save FormResponse
    API->>Workflow: Check Trigger Conditions
    Workflow->>API: Execute Actions (e.g., Create other response)
    API-->>User: 201 Created (response_id)
```

## 4. To-Be Improvements

- **Microservices Path**: Decouple AI and Export services into separate containers for scaling.
- **Event-Driven**: Use a message queue (RabbitMQ/Redis) for Workflows and AI tasks.
- **Enhanced Caching**: Implement Redis for frequently accessed form definitions.
