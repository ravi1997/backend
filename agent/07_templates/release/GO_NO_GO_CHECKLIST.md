# Go/No-Go Checklist: Release v[X.Y.Z]

## 1. Quality & Testing Gates (MANDATORY)

- [ ] 100% Pass Rate on `agent/05_gates/global/gate_global_quality.md`.
- [ ] 100% Pass Rate on Stack-specific Build Gate.
- [ ] Unit Test Coverage >= 80%.
- [ ] All Integration tests pass locally.

## 2. Security & Compliance

- [ ] 100% Pass Rate on `agent/05_gates/global/gate_global_security.md`.
- [ ] Zero hardcoded secrets in changeset.
- [ ] Dependency Audit completed (`0` High/Critical CVEs).

## 3. Documentation & State

- [ ] `CHANGELOG.md` updated and matches Git history.
- [ ] `RELEASE_NOTES.md` generated and reviewed.
- [ ] `agent/09_state/BACKLOG_STATE.md` shows all release tasks as "DONE".

## 4. Infrastructure & Deployment

- [ ] Docker production build succeeds.
- [ ] Rollback plan for this release is documented in `plans/Deployment/rollback_plan.md`.
- [ ] Configuration environment variables are verified.

---

## Final Decision

- [ ] **GO**: All mandatory checks passed.
- [ ] **NO-GO**: Blocked by [Issue ID].
