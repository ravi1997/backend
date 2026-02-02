# Scenario: External API Dependency Failure

## Purpose

Handling situations where the project depends on a third-party API that becomes unavailable, deprecated, or rate-limited during development or testing.

## Inputs

- Error logs showing API failures (timeout, 429, 503, etc.).
- Dependency on external services (payment gateways, auth providers, data APIs).

## Detection Phase (Adopt `profile_tester.md`)

1. **Failure Classification**: Determine if the failure is:
   - **Transient**: Network blip, temporary outage.
   - **Rate Limit**: Too many requests.
   - **Permanent**: API deprecated or credentials revoked.
2. **Impact Scope**: Identify all code paths that depend on this API.

## Mitigation Phase (Adopt `profile_implementer.md`)

1. **Immediate Workaround**:
   - **For Testing**: Create a mock/stub implementation using the last known good response schema.
   - **For Production**: Implement exponential backoff and circuit breaker patterns.
2. **Fallback Strategy**:
   - If the API is critical and has no alternative, add a task to the backlog: "Research alternative providers for [Service]".
   - If the API is optional, gracefully degrade functionality.
3. **Documentation**: Update `plans/Architecture/EXTERNAL_DEPENDENCIES.md` with:
   - API endpoint URLs.
   - Rate limits and SLA.
   - Fallback behavior.

## Testing Phase (Adopt `profile_tester.md`)

1. **Chaos Engineering**: Intentionally disable the API in tests to verify fallback logic works.
2. **Mock Validation**: Ensure mocks match the real API schema (use contract testing if possible).

## STOP Condition

- The application can handle API failures gracefully without crashing.
- All external dependencies are documented with fallback strategies.

## Related Files

- `agent/10_security/threat_model_template.md` (for supply chain risks)
- `agent/06_skills/testing/skill_discover_edge_cases.md`
