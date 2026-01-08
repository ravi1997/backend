# Profile: Default

## Autonomy
- You may suggest changes and produce patch-ready edits.
- Prefer safe, incremental changes.
- Always include verification commands and rollback steps when relevant.

## Safety
- PHI-safe logging: ON
- Secret redaction: ON
- Production write actions: OFF by default (require explicit environment confirmation)

## Debug philosophy
1. Confirm symptom + scope
2. Find root cause with minimal assumptions
3. Fix with smallest change
4. Add regression test (when feasible)
5. Run tests + lint
6. Produce an artifact (PR summary / incident report when applicable)
