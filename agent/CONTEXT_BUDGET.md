# Context Budget & Token Economy

**Purpose**: Prevent "Context Bloat" where agents read too many files "just in case," confusing themselves and wasting tokens.

## 1. The Budget
*   **Max Files per Turn**: 6–10 files.
*   **Max Token Guideline**: Keep prompt-in under 20k if possible (excluding system prompt).
*   **Expansion**: Only expand context if *strictly* necessary for the specific next step.

## 2. The Two-Pass Rule

### Pass 1: Minimal Context (The Bootstrap)
*   **Goal**: Identify `ACTIVE_SCOPE`, `STACK`, and `WORKFLOW`.
*   **Allowed Reads**:
    1.  `00_BOOTSTRAP.md`
    2.  `agent/01_PROJECT_CONTEXT.md`
    3.  `ROUTING_RULES.md`
    4.  `agent/components/<ACTIVE_SCOPE>.md`
    5.  The selected target workflow (e.g., `agent/workflows/feature_delivery.md`).
*   **Forbidden**:
    *   Broad `ls -R` or `find` commands.
    *   Reading "all documentation" or `README.md`.
    *   Reading source code files *unless* specific lines are targeted by a stack trace.

### Pass 2: Targeted Expansion (Execution)
*   **Goal**: Execute the plan defined in Pass 1.
*   **Trigger**: You have a selected workflow and a clear task.
*   **Allowed Reads**:
    *   Files explicitly listed in the Workflow's "Prerequisites".
    *   Source code files identified as relevant (limit 1-2 at a time).
    *   Reference materials (e.g., `checklists/`) *only when you reach that step*.

## 3. Handling Overage ("Plan-Only" Mode)
If a request is complex and requires reading > 10 files to understand (e.g., "Refactor the entire auth system"):

1.  **STOP** loading files.
2.  **Switch to Plan-Only**:
    *   Do not write code.
    *   Write a `implementation_plan.md` that lists the files you *need* to read.
    *   Ask the user to approve the plan.
    *   *Then* proceed chunk-by-chunk.

## 4. Anti-Patterns
*   ❌ "I will read `agent/00_INDEX.md` and `agent/README.md` to understand the project." (VIOLATION: Too generic).
*   ❌ "I will read all files in `src/` to find where the bug is." (VIOLATION: Too broad).
*   ✅ "I will grep for `error_code_50` to find the specific file, then read only that file." (APPROVED: Targeted).
