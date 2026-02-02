# Rules: Multi-Stack Architecture

**Class**: Architecture Constraints  
**Complexity**: High  
**Enforcement**: Strict

---

## 1. Subproject Boundaries

### 1.1 Independence

- **Strict Isolation**: Each subproject (frontend, backend, service) MUST have its own build configuration (package.json, pom.xml, CMakeLists.txt).
- **No Cross-Imports**: A subproject MUST NOT import code directly from another subproject's source files. Use shared packages or APIs.
- **Example**:
  - ❌ `import Component from '../../frontend/src/components/Component'`
  - ✅ `import { Component } from '@org/ui-kit'`

### 1.2 Structure

- **Root-Level Service Directory**: All services/apps MUST reside in top-level directories (`apps/`, `services/`, `packages/`).
- **Shared Code**: All shared code MUST be extracted into a `packages/` or `libs/` directory.

---

## 2. API Contract

### 2.1 Explicit Definitions

- **Schema-First**: APIs MUST be defined by a schema (OpenAPI, GraphQL, Protobuf) BEFORE implementation.
- **Versioning**: API changes MUST be versioned (v1, v2) if breaking.

### 2.2 Consumption

- **Generated Clients**: Frontends SHOULD use generated clients from API schemas, not ad-hoc fetch calls.
- **Type Safety**: Shared types MUST be used between backend and frontend where possible (e.g., shared TypeScript interfaces).

---

## 3. DevOps & CI/CD

### 3.1 Containerization

- **One Container Per Service**: Each deployable subproject MUST have its own Dockerfile.
- **Docker Compose**: A root-level `docker-compose.yml` MUST orchestrate all services for local development.

### 3.2 CI Pipelines

- **Selective Builds**: CI MUST only build/test the subprojects that changed (using tools like Turborepo, Nx, or git-diff logic).
- **Parallel Execution**: Integration tests SHOULD run in parallel where possible.

---

## 4. Integration Testing

### 4.1 Test Scope

- **E2E Tests**: MUST exist to verify critical flows spanning multiple stacks (e.g., Frontend → Backend → DB).
- **Mocking**: Integration tests SHOULD run against real containers (not mocks) where feasible (using Testcontainers or docker-compose).

### 4.2 Data Management

- **Test Data**: Integration tests MUST use seeded test data, not production data.
- **Isolation**: Tests MUST NOT depend on the state left by previous tests (reset DB between runs).

---

## 5. Dependency Management

### 5.1 Version Alignment

- **Shared Dependencies**: Dependencies used across multiple subprojects (e.g., React version, logging lib) SHOULD be kept in sync.
- **Lock Files**: Each subproject MUST have a lock file, OR a root-level lock file for the workspace.

---

## 6. Communication

### 6.1 Sync vs Async

- **Sync (HTTP/gRPC)**: Use for user-facing, immediate response requirements.
- **Async (Events/Queues)**: Use for side effects, heavy processing, and service decoupling.

### 6.2 Error Handling

- **Standard Errors**: All stacks MUST return errors in a standard format (e.g., `{ code, message, details }`).

---

## Enforcement Checklist

- [ ] Subprojects are isolated with own config
- [ ] No relative imports across subproject roots
- [ ] Shared code is in `packages/`
- [ ] Dockerfile exists for each deployable service
- [ ] API schema is defined
- [ ] Integration tests cover cross-stack flows
- [ ] CI runs selective builds
