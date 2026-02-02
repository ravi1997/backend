# Example: Existing Project Walkthrough (Multi-Stack)

**Scenario**: Onboarding a legacy monorepo (Frontend + Backend) to Agent OS.

---

## 1. Initial Detection

**Action**: Run `detect_multi_stack` (part of Repository Scan).
**Result**: `STACK_MAP.md` created.

```markdown
- Subproject 1: /frontend (React + Vite)
- Subproject 2: /backend (Node.js + NestJS)
- DevOps: Docker present
```

## 2. Baseline Audit

**Action**: Run `04_workflows/02_repo_audit_and_baseline.md` (or `multi_stack_orchestration` audit phase).
**Outcome**:

- Frontend: Missing specialized Linter rules.
- Backend: Missing Dependency Audit.
- Repo: Missing global CI workflow.

## 3. Applying Fixes

**Priority 1**: Create CI Pipeline (Global Gate).

- **Skill**: `skill_generate_github_actions.md`
- **Action**: Create `.github/workflows/ci.yml` that triggers on changes to `/frontend` or `/backend`.

**Priority 2**: Dockerize (Stack Rules).

- **Skill**: `skill_dockerize_stack.md`
- **Action**: Update `backend/Dockerfile` to best practices (non-root user).
- **Action**: Create `frontend/Dockerfile` for Nginx serving.

## 4. Orchestrating Build

**Action**: Run `agent/04_workflows/11_multi_stack_orchestration.md`.
**Flow**:

1. Build Backend container → Pass
2. Build Frontend container → Pass
3. Run Integration Test (Frontend calling Backend API) → Pass

## 5. Release

**Action**: Tag release `v1.2.0`.
**Outcome**:

- Docker images pushed to registry.
- Changelog updated relative to both stacks.
