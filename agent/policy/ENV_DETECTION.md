# Environment Detection Rules

Classify current context as `dev`, `staging`, or `production`.

## Signals (high confidence)
Production if any:
- Domain includes: `prod`, `production`, `live`
- `FLASK_ENV=production` or `DEBUG=0`
- Primary/public service domain used by real users
- On-call/outage language, SLA impact

Staging if any:
- Domain includes: `staging`, `preprod`, `uat`, `test`
- CI/CD pipeline indicates staging deploy
- Data is non-real or masked

Dev if any:
- localhost / 127.0.0.1
- developer machine, feature branches

## If mixed / uncertain
Treat as **production**.

## Output
Write a one-line decision:
`ENV=production|staging|dev` + brief reason.
