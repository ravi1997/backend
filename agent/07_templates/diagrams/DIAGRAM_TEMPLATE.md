# Diagram Template

## Sequence Diagram (Mermaid)

```mermaid
sequenceDiagram
    participant User
    participant System
    User->>System: Request
    System-->>User: Response
```

## ERD (Mermaid)

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        string name
        string email
    }
```
