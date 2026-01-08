# FLOW: Incident Triage

## Inputs (minimal)
Fill: `forms/INCIDENT_MIN.md`

## Step 1 — Classify incident
Choose one primary category:
- NGINX / 502 / 504 / upstream
- App crash / exception
- Docker build/run failure
- systemd service failure
- DB/migration failure
- Performance regression
- Security event

## Step 2 — Collect evidence (mandatory)
Use the relevant checklist:
- `checklists/NGINX_502_EVIDENCE.md`
- `checklists/DOCKER_BUILD_FAIL_EVIDENCE.md`
- `checklists/SYSTEMD_FAIL_EVIDENCE.md`
- `checklists/MIGRATION_FAIL_EVIDENCE.md`
- `checklists/PERF_REGRESSION_EVIDENCE.md`

## Step 3 — Hypotheses (ranked)
Create 3–5 hypotheses with:
- supporting evidence
- disconfirming evidence
- next verification command

## Step 4 — Containment / rollback
If user impact:
- recommend safe containment (rate-limit, maintenance mode)
- recommend rollback strategy (`workflows/rollback_recovery.md`)

## Step 5 — Fix loop
Follow: `flows/AUTOFIX_LOOP.md`

## Outputs
- `artifacts/INCIDENT_REPORT.md`
- (If major) `artifacts/POSTMORTEM.md`
- `artifacts/DECISION_RECORD.md` for notable decisions
