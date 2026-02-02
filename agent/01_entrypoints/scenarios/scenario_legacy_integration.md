# Scenario: Legacy Code Integration

## Purpose

Integrating with or refactoring legacy codebases that lack tests, documentation, or modern tooling.

## Inputs

- Legacy module or codebase (potentially undocumented).
- Requirement to integrate with or modernize the legacy system.

## Archaeology Phase (Adopt `profile_rule_checker.md`)

1. **Code Reading**: Use `agent/06_skills/knowledge_extraction/skill_extract_context.md` to map the legacy code structure.
2. **Behavior Capture**: Run the legacy code with various inputs and document the outputs (characterization testing).
3. **Dependency Audit**: Identify all external libraries, especially deprecated or unmaintained ones.
4. **Risk Assessment**: Flag sections of code that are:
   - Security vulnerabilities (SQL injection, XSS).
   - Performance bottlenecks.
   - Incompatible with modern runtimes.

## Stabilization Phase (Adopt `profile_tester.md`)

1. **Test Harness**: Write integration tests that capture the current behavior (even if it's buggy).
2. **Approval Tests**: Use snapshot testing to lock in current outputs.
3. **Baseline**: Establish a "known state" before making any changes.

## Modernization Phase (Adopt `profile_implementer.md`)

1. **Strangler Fig Pattern**: Gradually replace legacy components with new implementations while keeping the old code running.
2. **Facade Layer**: Create a clean interface around the legacy code to isolate its complexity.
3. **Incremental Refactor**: Refactor one function at a time, ensuring tests still pass.

## Migration Phase (Adopt `profile_architect.md`)

1. **Dual-Run**: Run both legacy and new implementations in parallel, comparing outputs.
2. **Feature Flags**: Use flags to toggle between old and new code paths.
3. **Deprecation**: Once the new system is stable, mark legacy code as deprecated and schedule removal.

## STOP Condition

- Legacy code is either fully replaced or safely encapsulated behind a clean interface.
- All tests pass and performance is maintained or improved.

## Related Files

- `agent/06_skills/implementation/skill_surgical_refactor.md`
- `agent/04_workflows/02_repo_audit_and_baseline.md`
