# AI Agent System Architecture

## Overview

The AI Agent MD Pack is a markdown-based configuration system that enables AI agents to autonomously handle development, testing, and maintenance tasks with minimal user input.

## System Architecture

```mermaid
graph TB
    subgraph "Entry Layer"
        A[User Request] --> B[00_SYSTEM.md]
        B --> C[00_INDEX.md Router]
    end
    
    subgraph "Context Layer"
        C --> D[01_PROJECT_CONTEXT.md]
        D --> E[autofill/PATH_AND_SERVICE_INFERENCE.md]
        E --> F{Context Complete?}
        F -->|No| G[forms/]
        F -->|Yes| H[Policy Layer]
        G --> H
    end
    
    subgraph "Policy Layer"
        H --> I[policy/ENV_DETECTION.md]
        I --> J[policy/PHI_SAFE_LOGGING.md]
        J --> K[policy/PRODUCTION_POLICY.md]
        K --> L{Environment?}
    end
    
    subgraph "Routing Layer"
        L --> M{Request Type}
        M -->|Incident| N[flows/INCIDENT_TRIAGE.md]
        M -->|Feature| O[workflows/feature_delivery.md]
        M -->|Deploy| P[workflows/deploy_and_migrate.md]
        M -->|Security| Q[workflows/security_incident.md]
        M -->|Performance| R[workflows/performance_profiling.md]
    end
    
    subgraph "Execution Layer"
        N --> S[checklists/]
        O --> T[forms/]
        P --> T
        Q --> S
        R --> S
        S --> U[skills/]
        T --> U
    end
    
    subgraph "Quality Layer"
        U --> V[gates/QUALITY_GATES.md]
        V --> W[gates/AGENT_SELF_CHECK.md]
    end
    
    subgraph "Output Layer"
        W --> X[artifacts/]
        X --> Y[Output: Reports, PRs, Runbooks]
    end
    
    style A fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
    style L fill:#FF9800,color:#fff
    style Y fill:#9C27B0,color:#fff
```

---

## Component Interaction Flow

### 1. Request Ingestion

```mermaid
sequenceDiagram
    participant U as User
    participant S as 00_SYSTEM.md
    participant R as 00_INDEX.md
    participant C as 01_PROJECT_CONTEXT.md
    
    U->>S: Give task/problem
    S->>R: Route request
    R->>C: Load context
    C-->>R: Return config
    R->>R: Determine workflow
```

### 2. Context Resolution

```mermaid
sequenceDiagram
    participant C as 01_PROJECT_CONTEXT.md
    participant A as autofill/
    participant F as forms/
    participant W as Workflow
    
    C->>A: Check for missing values
    A->>A: Infer from repo structure
    alt All inferred
        A-->>W: Complete context
    else Need user input
        A->>F: Request minimal form
        F->>U: Ask 1-2 questions
        U-->>F: Provide answers
        F-->>W: Complete context
    end
```

### 3. Workflow Execution

```mermaid
sequenceDiagram
    participant W as Workflow
    participant CL as Checklists
    participant SK as Skills
    participant G as Gates
    participant AR as Artifacts
    
    W->>CL: Collect evidence
    CL-->>W: Evidence data
    W->>SK: Apply technical knowledge
    SK-->>W: Solution
    W->>G: Run quality gates
    G-->>W: Pass/Fail
    alt Pass
        W->>AR: Generate artifact
        AR-->>U: Deliver output
    else Fail
        W->>W: Retry with fixes
    end
```

---

## Directory Structure & Responsibilities

### Core Configuration
| File | Purpose | When Read |
|------|---------|-----------|
| `00_SYSTEM.md` | Agent behavior rules | Every request |
| `00_INDEX.md` | Request router | Every request |
| `01_PROJECT_CONTEXT.md` | Project-specific config | Every request |
| `02_CONVENTIONS.md` | Code standards | During implementation |
| `02_CONVENTIONS.md` | Fallback values | When context incomplete (See Defaults) |

### Routing & Navigation
| File | Purpose | When Used |
|------|---------|-----------|
| `REFERENCE_MAP.md` | Tag-based lookup | Cross-referencing |
| `ROUTING_RULES.md` | Keyword matching | Request classification |
| `TAXONOMY.md` | Error categorization | Incident triage |

### Workflows (End-to-End Processes)
| Directory | Contains | Purpose |
|-----------|----------|---------|
| `workflows/` | Complete processes | Feature delivery, debugging, deployment |
| `flows/` | Reusable sub-processes | Incident triage, autofix loops |

### Supporting Components
| Directory | Contains | Purpose |
|-----------|----------|---------|
| `checklists/` | Evidence collection templates | Gather diagnostic data |
| `forms/` | Minimal input templates | Get required user input |
| `policy/` | Safety & governance rules | Enforce constraints |
| `gates/` | Quality checkpoints | Validate before completion |
| `skills/` | Technical knowledge | Domain-specific expertise |
| `profiles/` | Agent behavior modes | Adjust autonomy level |
| `autofill/` | Inference rules | Minimize user input |
| `artifacts/` | Output templates | Structure deliverables |

---

## Data Flow

### Incident Response Flow

```mermaid
graph LR
    A[Error Reported] --> B[00_INDEX.md]
    B --> C[flows/INCIDENT_TRIAGE.md]
    C --> D{Error Type?}
    
    D -->|502/504| E[checklists/NGINX_502_EVIDENCE.md]
    D -->|Docker| F[checklists/DOCKER_BUILD_FAIL_EVIDENCE.md]
    D -->|systemd| G[checklists/SYSTEMD_FAIL_EVIDENCE.md]
    D -->|Migration| H[checklists/MIGRATION_FAIL_EVIDENCE.md]
    D -->|Performance| I[checklists/PERF_REGRESSION_EVIDENCE.md]
    
    E --> J[workflows/nginx_502_504.md]
    F --> K[workflows/docker_dev_loop.md]
    G --> L[workflows/systemd_failures.md]
    H --> M[workflows/db_migrations.md]
    I --> N[workflows/performance_profiling.md]
    
    J --> O[skills/nginx_gunicorn.md]
    K --> P[skills/docker_compose.md]
    L --> Q[skills/systemd.md]
    M --> R[skills/migrations.md]
    N --> S[skills/]
    
    O --> T[artifacts/INCIDENT_REPORT.md]
    P --> T
    Q --> T
    R --> T
    S --> T
    
    style A fill:#f44336,color:#fff
    style T fill:#4CAF50,color:#fff
```

### Feature Delivery Flow

```mermaid
graph LR
    A[Feature Request] --> B[00_INDEX.md]
    B --> C[workflows/feature_delivery.md]
    C --> D[forms/FEATURE_MIN.md]
    D --> E{Complex?}
    
    E -->|Yes| F[artifacts/DECISION_RECORD.md]
    E -->|No| G[Implementation]
    F --> G
    
    G --> H[testing/TEST_STRATEGY.md]
    H --> I[gates/QUALITY_GATES.md]
    I --> J{Pass?}
    
    J -->|No| G
    J -->|Yes| K[artifacts/PR_SUMMARY.md]
    
    style A fill:#2196F3,color:#fff
    style K fill:#4CAF50,color:#fff
```

---

## Profile System

Profiles adjust agent behavior based on environment and risk tolerance:

```mermaid
graph TD
    A[Request] --> B{Detect Environment}
    B -->|Production| C[profiles/production_safe.md]
    B -->|Staging| D[profiles/default.md]
    B -->|Dev| E{User Preference}
    
    E -->|Conservative| D
    E -->|Aggressive| F[profiles/aggressive_autofix.md]
    
    C --> G[Read-only mode]
    D --> H[Balanced mode]
    F --> I[Auto-fix mode]
    
    G --> J[Require confirmation]
    H --> K[Evidence-first]
    I --> L[Fix immediately]
    
    style C fill:#f44336,color:#fff
    style D fill:#FF9800,color:#fff
    style F fill:#4CAF50,color:#fff
```

---

## Autofill System (v4)

The autofill system minimizes user input by inferring project structure:

```mermaid
graph TD
    A[01_PROJECT_CONTEXT.md] --> B{Field Empty?}
    B -->|No| C[Use Provided Value]
    B -->|Yes| D[autofill/PATH_AND_SERVICE_INFERENCE.md]
    
    D --> E{Check pyproject.toml}
    E -->|Found| F[Infer Python package]
    E -->|Not found| G{Check requirements.txt}
    
    G -->|Found| H[Infer from imports]
    G -->|Not found| I{Check docker-compose.yml}
    
    I -->|Found| J[Infer services & ports]
    I -->|Not found| K{Check app.py/wsgi.py}
    
    K -->|Found| L[Infer entrypoint]
    K -->|Not found| M[Use defaults]
    
    F --> N[Complete Context]
    H --> N
    J --> N
    L --> N
    M --> N
    
    N --> O{Critical Missing?}
    O -->|Yes| P[forms/PROJECT_CONTEXT_MIN.md]
    O -->|No| Q[Proceed]
    
    P --> R[Ask 1-2 questions]
    R --> Q
    
    style A fill:#2196F3,color:#fff
    style Q fill:#4CAF50,color:#fff
```

---

## Safety Layers

### PHI/PII Protection

```mermaid
graph LR
    A[Log Request] --> B{Contains PHI/PII?}
    B -->|Yes| C[policy/PHI_SAFE_LOGGING.md]
    B -->|No| D[Log Normally]
    
    C --> E[Redact Sensitive Fields]
    E --> F[Mask Identifiers]
    F --> G[Hash if Needed]
    G --> H[Safe Log]
    
    style B fill:#f44336,color:#fff
    style H fill:#4CAF50,color:#fff
```

### Production Safety

```mermaid
graph LR
    A[Command Request] --> B{Environment?}
    B -->|Production| C[policy/PRODUCTION_POLICY.md]
    B -->|Non-Prod| D[Execute]
    
    C --> E{Destructive?}
    E -->|Yes| F[Block + Warn]
    E -->|No| G{Read-Only?}
    
    G -->|Yes| D
    G -->|No| H[Require Confirmation]
    H --> I{Confirmed?}
    I -->|Yes| J[Execute with Rollback Plan]
    I -->|No| F
    
    style F fill:#f44336,color:#fff
    style D fill:#4CAF50,color:#fff
```

---

## Extension Points

### Adding Custom Workflows

1. Create `workflows/your_workflow.md`
2. Follow template structure:
   ```markdown
   # Workflow: Your Workflow Name
   
   Inputs: forms/YOUR_FORM.md
   
   ## 1) Step One
   ## 2) Step Two
   ## 3) Output
   ```
3. Add to `REFERENCE_MAP.md`:
   ```
   - WORKFLOW:YOUR_WORKFLOW → workflows/your_workflow.md
   ```
4. Update routing in `00_INDEX.md` when adding new request types

### Adding Custom Skills

1. Create `skills/your_skill.md`
2. Document technical knowledge
3. Reference from workflows

### Adding Custom Policies

1. Create `policy/YOUR_POLICY.md`
2. Define rules and constraints
3. Reference from `00_INDEX.md` non-negotiables

---

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Request routing | O(1) | Direct lookup via 00_INDEX.md |
| Context resolution | O(n) | n = number of inference rules |
| Workflow execution | O(m) | m = workflow steps |
| Quality gates | O(k) | k = number of tests |

---

## Design Principles

1. **Minimal User Input** - Autofill infers 80% of configuration
2. **Safety First** - PHI/PII protection and production safety by default
3. **Evidence-Based** - Collect data before acting
4. **Incremental** - Small, verifiable changes
5. **Documented** - Every action produces an artifact
6. **Extensible** - Easy to add workflows, skills, policies

---

## Future Enhancements

- [ ] Multi-language support (beyond Python/Flask)
- [ ] Kubernetes workflow integration
- [ ] Advanced monitoring integration (Prometheus, Grafana)
- [ ] CI/CD pipeline templates
- [ ] Cost optimization workflows
- [ ] Compliance audit workflows (SOC2, HIPAA)

---

**See Also:**
- [`README.md`](README.md) - Overview and quick start
- [`00_INDEX.md`](00_INDEX.md) - Main router
- [`01_PROJECT_CONTEXT.md`](01_PROJECT_CONTEXT.md) - Configuration
