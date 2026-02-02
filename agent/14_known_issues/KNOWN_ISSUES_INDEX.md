# Known Issues Index

**System**: Self-Learning Database  
**Purpose**: Track recurring issues and their proven solutions

---

## Log Entry Protocol

When a recurring issue is solved:

1. Create a file: `KI-YYYYMMDD-short-slug.md`
2. Template:

   ```markdown
   # Issue: [Title]
   **Tags**: [tag1, tag2]
   **Status**: Solved
   
   ## Symptoms
   - Error message X
   - Behavior Y
   
   ## Root Cause
   Explanation...
   
   ## Solution Plan
   1. Step 1
   2. Step 2
   
   ## Prevention
   Rule or Gate changes...
   ```

3. Add entry to this Index below.
4. Add detecting keywords to `ROUTING_HINTS.md`.

---

## Issue Registry

| ID | Title | Tags | Status |
|---|---|---|---|
| [KI-20260121-native-cli-impl](./KI-20260121-native-cli-impl.md) | Missing Native CLI | cli, python | Solved |
| [KI-20260121-prompt-validation](./KI-20260121-prompt-validation-failures.md) | Validation Failures | prompt, system | Solved |
| [KI-20260121-rules-overhead](./KI-20260121-rules-overhead.md) | Rules File Overhead | rules, perf | Solved |
| [KI-20260121-manifest-loc](./KI-20260121-manifest-loc.md) | Manifest Path Error | system, path | Solved |

---

## Search Strategy

Before attempting a fix, Agent MUST:

1. Grep this directory for error keywords.
2. Check `ROUTING_HINTS.md` for fast-track solutions.
