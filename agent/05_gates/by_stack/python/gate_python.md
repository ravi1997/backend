# Stack Gate: Python (Quality & Style)

## Purpose

Python-specific validation to ensure senior-level code quality and ecosystem compliance.

## Explicit Pass/Fail Rubric

| Criterion | Methodology | Pass Threshold | Fail Trigger |
| --- | --- | --- | --- |
| **Linting** | `flake8 .` / `pylint` | 0 Errors | Any "E" or "F" code |
| **Formatting** | `black --check .` | No changes needed | Unformatted files |
| **Imports** | `isort --check .` | Ordered | Circular or messy imports |
| **Type Integrity** | `mypy . --strict` | Success | Optional types without `Optional` |
| **Env Sync** | `pip-compile --dry-run` | Up to date | Missing packages in manifest |

## Verification Procedure

1. **Format**: Run `black .` followed by `isort .`.
2. **Lint**: Run `flake8` with `.flake8` config (if exists).
3. **Types**: Run `mypy` on the modified files.
4. **Security**: Execute `agent/05_gates/by_stack/python/gate_python_security.md`.

## Remediation

- Run `black . && isort .` to fix 90% of failures.
- Use `agent/06_skills/implementation/skill_refactor_safely.md` for type hint fixes.

## Related Files

- `agent/11_rules/stack_rules/python_rules.md`
- `agent/05_gates/by_stack/python/gate_python_security.md`
