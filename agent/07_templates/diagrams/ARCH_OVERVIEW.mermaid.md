# Diagram: Architecture Overview (Mermaid)

## Purpose

High-level structural view of the system components and their relationships.

## Template

```mermaid
graph TD
    subgraph "Client Layer"
        UI[Frontend App]
        CLI[Command Line Interface]
    end

    subgraph "Application Layer"
        API[Gatekeeper / API Gateway]
        AUTH[Auth Service]
        CORE[Core Logic Engine]
    end

    subgraph "Data Layer"
        DB[(Database)]
        REDIS[(Cache / Queue)]
        STORAGE[S3 / File Storage]
    end

    UI --> API
    CLI --> API
    API --> AUTH
    API --> CORE
    CORE --> DB
    CORE --> REDIS
    CORE --> STORAGE
```

## How to use

1. Copy the mermaid block above.
2. Replace component names with project-specific names.
3. Add or remove subgraphs based on the system's complexity.
4. Save in `plans/Architecture/OVERVIEW.mermaid.md`.
