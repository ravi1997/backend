# Gate: Global Quality

## Purpose

Universal quality baseline that must be met before any code is merged into the stable branch.

## Explicit Pass/Fail Rubric

| Criterion | Methodology | Pass Threshold | Fail Trigger |
| --- | --- | --- | --- |
| **Logic Correctness** | `npm test` / `pytest` / `mvn test` | 100% Pass Rate | Any single failure |
| **Static Analysis** | `npm run lint` / `flake8` / `clang-tidy` | 0 Errors | Any "Error" level violation |
| **Build Integrity** | `npm run build` / `make` / `mvn compile` | Success w/o Warnings | Build failure or "Warning" level |
| **Code Hygiene** | `grep -r "TODO\|FIXME" .` | No new TODOs in delta | Added TODO/FIXME in PR |
| **Coverage** | `coverage report` / `istanbul` | >= 80% (or current) | Lowering current coverage |

## Verification Procedure

1. **Test Execution**: Run the primary test suite command. Capture output to `plans/Tests/LATEST_RUN.log`.
2. **Lint Check**: Run the project's linter.
3. **Dependency Check**: Run `agent/06_skills/security/skill_dependency_audit.md`.
4. **Score**: Use `agent/12_checks/rubrics/quality_rubric.md` to calculate a score.

## Sign-off Command
>
> Proceed only if `agent/12_checks/rubrics/quality_rubric.md` score is >= 9/10.

## Failure Playbook

- If Code Hygiene fails: Adopt `agent/03_profiles/profile_rule_checker.md` and remove placeholders.
- If Build Integrity fails: Consult `agent/05_gates/enforcement/gate_failure_playbook.md`.

## Related Files

- `agent/12_checks/rubrics/quality_rubric.md`
- `agent/11_rules/code_style_rules.md`
