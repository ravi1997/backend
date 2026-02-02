# Entrypoint: Run SRS Only

## Purpose

Used when the User only wants a professional requirements document without starting implementation.

## Inputs

- Project idea or rough notes.

## Procedure

1. **Profile**: `profile_analyst_srs.md`.
2. **Extraction**: Run `agent/06_skills/knowledge_extraction/` on User input.
3. **Generation**: Apply `agent/07_templates/srs/` to create `plans/SRS/FULL_SRS.md`.
4. **Validation**: Check against `agent/05_gates/global/gate_global_docs.md`.

## Stop Conditions

- SRS is complete and signed off by the User.

## Related Files

- `agent/07_templates/srs/functional_reqs.md`
