# Detection: Repo Health

## Purpose

Assesses the current state of code quality, testing debt, and documentation completeness.

## Metrics

- **Build Status**: Does the current code compile/run?
- **Test Coverage**: Are there tests, and do they pass?
- **Documentation**: Does a README exist? Is it updated?
- **Linting**: Is there a linter config? Does it pass?
- **Security**: Are there known vulnerable dependencies?
- **Docker Health**: If Dockerfile exists, does `docker build` succeed?
- **Compose Health**: If docker-compose.yml exists, does `docker compose config` validate?
- **CI/CD Status**: If GitHub Actions exist, are workflows syntactically valid?
- **Container Security**: Are base images pinned? Is a non-root user configured?
- **Branch Protection**: Are there indicators of protected branches or required reviews?

## Procedure

1. **Run Build**: Attempt the primary build command.
2. **Run Tests**: Attempt to run existing tests.
3. **Scan Lints**: Run `npm lint`, `pylint`, etc.
4. **Log Results**: Write health report to `agent/09_state/PROJECT_STATE.md`.

## Health Levels

- **HEALTHY**: All pass.
- **DEGRADED**: Minor lint/test failures.
- **CRITICAL**: Build failure or major security leak.

## Related Files

- `agent/05_gates/global/gate_global_quality.md`
