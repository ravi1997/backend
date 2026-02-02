# Scenario: Circular Dependency Detection & Resolution

## Purpose

Identifying and breaking circular dependencies in code modules or services.

## Inputs

- Build errors indicating circular imports/dependencies.
- Architecture that has become tangled over time.

## Detection Phase (Adopt `profile_architect.md`)

1. **Dependency Graphing**: Use tools or manual analysis to create a dependency graph:
   - For Python: `pydeps` or manual import analysis.
   - For JavaScript: `madge` or webpack bundle analyzer.
   - For Java: `jdeps` or IDE dependency diagrams.
2. **Cycle Identification**: Highlight all circular paths (A → B → C → A).
3. **Impact Assessment**: Determine if the cycles are:
   - **Logical**: Actual design flaw.
   - **Structural**: Just import organization issue.

## Analysis Phase (Adopt `profile_implementer.md`)

1. **Root Cause**: Identify why the cycle exists:
   - Shared state between modules.
   - Bidirectional communication.
   - Poor separation of concerns.
2. **Breaking Strategy**: Choose an approach:
   - **Dependency Inversion**: Introduce an interface/abstraction layer.
   - **Extract Common**: Move shared code to a third module.
   - **Event-Driven**: Replace direct calls with events/messages.

## Refactoring Phase (Adopt `profile_implementer.md`)

1. **Incremental Breaking**: Break one cycle at a time.
2. **Test Coverage**: Ensure high test coverage before refactoring.
3. **Verification**: After each change, verify the build succeeds and tests pass.

## Prevention Phase (Adopt `profile_rule_checker.md`)

1. **Architecture Rules**: Add a rule to `agent/11_rules/code_style_rules.md` prohibiting circular dependencies.
2. **CI Check**: Add a linting step to detect new cycles in CI/CD.

## STOP Condition

- All circular dependencies are resolved.
- Prevention mechanisms are in place.

## Related Files

- `agent/06_skills/implementation/skill_surgical_refactor.md`
- `agent/11_rules/code_style_rules.md`
