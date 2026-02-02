# Multi-Stack Detection Protocol

**Component**: DET-02  
**Purpose**: Detect and map multiple technology stacks within a single repository  
**Output**: `plans/Detection/STACK_MAP.md`

---

## Overview

Modern repositories often contain multiple stacks:

- **Frontend + Backend** (e.g., React + Node.js)
- **Microservices** (multiple services with different stacks)
- **Mono-repos** (packages/, apps/, services/)
- **Tools + Apps** (CLI tools + web apps)
- **Multi-platform** (mobile + web + backend)

This protocol enables Agent OS to detect, map, and orchestrate work across all stacks in a repository.

---

## Detection Algorithm

### Step 1: Identify Subproject Boundaries

Scan for common multi-stack patterns:

```
Common Patterns:
├── frontend/          → Subproject 1
├── backend/           → Subproject 2
├── mobile/            → Subproject 3
├── packages/          → Multiple subprojects
│   ├── package-a/     → Subproject 4
│   └── package-b/     → Subproject 5
├── apps/              → Multiple subprojects
│   ├── web/           → Subproject 6
│   └── api/           → Subproject 7
├── services/          → Multiple subprojects
│   ├── auth/          → Subproject 8
│   └── data/          → Subproject 9
├── tools/             → Subproject 10
└── docs/              → Documentation (not a stack)
```

**Detection Rules**:

1. **Top-level directories** named: `frontend`, `backend`, `mobile`, `web`, `api`, `server`, `client`, `ui`, `services`, `apps`, `packages`, `tools`, `libs`, `modules`
2. **Subdirectories** within `packages/`, `apps/`, `services/`, `libs/`, `modules/` that contain their own `package.json`, `pom.xml`, `CMakeLists.txt`, `pubspec.yaml`, etc.
3. **Root-level** if no subproject structure detected (single-stack repo)

### Step 2: Apply Stack Fingerprinting to Each Subproject

For each identified subproject:

1. Run stack fingerprint detection (see `detect_stack_signals.md`)
2. Check for presence of:
   - `package.json` → Node/Next.js/React
   - `requirements.txt`, `pyproject.toml`, `Pipfile` → Python
   - `pom.xml`, `build.gradle` → Java
   - `CMakeLists.txt`, `Makefile` → C/C++
   - `pubspec.yaml` → Flutter
   - `index.html` + no build system → Static Web
   - `Dockerfile` → Docker support
   - `.github/workflows/` → GitHub Actions CI

3. Determine **primary stack** and **secondary stacks** (e.g., Node.js primary, Docker secondary)

### Step 3: Detect Cross-Stack Dependencies

Identify integration points:

- **Shared packages** (e.g., `packages/shared/` used by frontend + backend)
- **API contracts** (e.g., backend exposes API, frontend consumes it)
- **Database schemas** (e.g., backend + data service share DB)
- **Shared configuration** (e.g., `.env`, `config/`)
- **Monorepo tools** (e.g., `lerna.json`, `nx.json`, `turbo.json`, `pnpm-workspace.yaml`)

### Step 4: Detect DevOps Stack

Check for:

- **Docker**: `Dockerfile`, `docker-compose.yml`, `.dockerignore`
- **GitHub**: `.github/workflows/`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE/`
- **CI/CD**: `.gitlab-ci.yml`, `.circleci/`, `Jenkinsfile`, `.travis.yml`
- **Infrastructure**: `terraform/`, `k8s/`, `helm/`, `ansible/`

---

## Output Format: STACK_MAP.md

Generate `plans/Detection/STACK_MAP.md` with the following structure:

```markdown
# Stack Map

**Repository**: [repo-name]  
**Detection Date**: [ISO timestamp]  
**Total Subprojects**: [count]  
**Multi-Stack**: [YES/NO]

---

## Subproject Map

| ID | Path | Primary Stack | Secondary Stacks | Build Tool | Test Framework | Notes |
|----|------|---------------|------------------|------------|----------------|-------|
| SP-01 | `/frontend` | Next.js | TypeScript, React | npm | Jest | Web UI |
| SP-02 | `/backend` | Node.js Express | TypeScript | npm | Jest | REST API |
| SP-03 | `/mobile` | Flutter | Dart | flutter | flutter test | Mobile app |
| SP-04 | `/packages/shared` | TypeScript | - | npm | Jest | Shared types |

---

## Stack Summary

### Detected Stacks
- **Next.js**: 1 subproject (SP-01)
- **Node.js Express**: 1 subproject (SP-02)
- **Flutter**: 1 subproject (SP-03)
- **TypeScript**: 3 subprojects (SP-01, SP-02, SP-04)

### DevOps Stack
- **Docker**: ✓ (Dockerfile in root, docker-compose.yml)
- **GitHub Actions**: ✓ (.github/workflows/ci.yml)
- **Infrastructure**: ✗

---

## Cross-Stack Dependencies

### Shared Packages
- `packages/shared/` → Used by SP-01 (frontend), SP-02 (backend)

### API Contracts
- SP-02 (backend) exposes REST API at `/api/*`
- SP-01 (frontend) consumes API via `fetch('/api/*')`

### Database
- SP-02 (backend) uses PostgreSQL
- No other subprojects access DB directly

---

## Integration Testing Strategy

### Required Integration Tests
1. **Frontend ↔ Backend**: E2E tests for API consumption
2. **Mobile ↔ Backend**: API integration tests
3. **Shared Package**: Unit tests in SP-04, integration tests in SP-01 and SP-02

### Test Orchestration
- Run unit tests per subproject first
- Run integration tests after all subprojects pass unit tests
- Run E2E tests last

---

## Build Order

**Dependency Graph**:
```

SP-04 (shared) → SP-01 (frontend)
                 ↓
                 SP-02 (backend) → SP-03 (mobile)

```

**Build Order**:
1. SP-04 (shared package)
2. SP-02 (backend) - depends on shared
3. SP-01 (frontend) - depends on shared
4. SP-03 (mobile) - depends on backend API

---

## Recommended Workflow

Use `agent/04_workflows/11_multi_stack_orchestration.md` to:
1. Run stack-specific gates per subproject
2. Coordinate integration tests
3. Merge release readiness results

---

**End of Stack Map**
```

---

## Detection Rules

### Rule 1: Minimum Subproject Criteria

A directory is a subproject if it contains:

- A build configuration file (package.json, pom.xml, CMakeLists.txt, etc.)
- OR a source code directory (src/, lib/, app/)
- AND is not a test fixture or example directory

### Rule 2: Stack Fingerprint Priority

If multiple stack fingerprints match:

1. **Specific over generic** (Next.js over Node.js)
2. **Framework over language** (Flask over Python)
3. **Primary over secondary** (main app over Docker support)

### Rule 3: Monorepo Detection

If `lerna.json`, `nx.json`, `turbo.json`, or `pnpm-workspace.yaml` exists:

- Treat as monorepo
- Scan `packages/`, `apps/`, `libs/` for subprojects
- Detect shared dependencies

### Rule 4: Root-Level Single Stack

If no subproject structure detected:

- Treat entire repo as single subproject
- ID: `SP-01`
- Path: `/`

---

## Integration with Other Components

### With `detect_stack_signals.md`

- Multi-stack detection calls stack signals detection per subproject
- Stack signals detection returns fingerprint match results

### With `04_workflows/11_multi_stack_orchestration.md`

- Stack map is input to orchestration workflow
- Orchestration workflow runs stack-specific gates per subproject

### With `05_gates/`

- Each subproject gets stack-specific gates applied
- Global gates apply to entire repository

### With `09_state/`

- Update `state_detection.md` with multi-stack status
- Track per-subproject state in orchestration

---

## Error Handling

### No Stacks Detected

- **Action**: Treat as documentation-only or unknown repo
- **Output**: STACK_MAP.md with "No stacks detected"
- **Next**: Prompt user for clarification

### Conflicting Stack Signals

- **Action**: List all detected stacks with confidence scores
- **Output**: STACK_MAP.md with "Multiple possible stacks" section
- **Next**: Prompt user to confirm primary stack

### Circular Dependencies

- **Action**: Detect cycles in dependency graph
- **Output**: STACK_MAP.md with "WARNING: Circular dependencies detected"
- **Next**: Recommend refactoring or manual build order

---

## Examples

### Example 1: Frontend + Backend Monorepo

```
repo/
├── frontend/          → Next.js (SP-01)
├── backend/           → Node.js Express (SP-02)
└── docker-compose.yml → Docker (DevOps)

STACK_MAP.md:
- Multi-Stack: YES
- Subprojects: 2
- DevOps: Docker
```

### Example 2: Microservices

```
repo/
├── services/
│   ├── auth/          → Java Spring (SP-01)
│   ├── data/          → Python FastAPI (SP-02)
│   └── gateway/       → Node.js Express (SP-03)
└── .github/workflows/ → GitHub Actions (DevOps)

STACK_MAP.md:
- Multi-Stack: YES
- Subprojects: 3
- DevOps: GitHub Actions
```

### Example 3: Single Stack

```
repo/
├── src/               → Python Flask (SP-01)
├── tests/
└── requirements.txt

STACK_MAP.md:
- Multi-Stack: NO
- Subprojects: 1 (root)
- DevOps: None
```

---

## Validation

After generating STACK_MAP.md:

1. **Verify all subprojects** have a detected stack
2. **Verify dependency graph** is acyclic (or document cycles)
3. **Verify build order** is logical
4. **Verify integration points** are identified

---

## State Update

After multi-stack detection:

- Update `plans/Detection/STACK_MAP.md`
- Update `agent/09_state/state_detection.md` with:
  - Multi-stack: YES/NO
  - Subproject count
  - Primary stacks list
  - DevOps stack presence

---

**End of Multi-Stack Detection Protocol**
