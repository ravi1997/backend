# 00_BOOTSTRAP (Entry Point)

> **CRITICAL INSTRUCTION**: Do NOT read any other files yet.
> You are currently in the **BOOTSTRAP PHASE**.
> Your goal is to load the *minimum* context required to route this request.

## 1. Context Budget Check
You have a limited "Context Budget" (approx 6 files).
**Current State**: You have read `00_BOOTSTRAP.md` (Count: 1).
**Remaining**: ~5 files for this turn.
**Rule**: Do not perform broad searches or read entire directories.

## 2. Load Project Context
Read `agent/01_PROJECT_CONTEXT.md` (Count: 2) to load global variables and paths.

## 3. Resolve ACTIVE_SCOPE & Stack
Determine what the user is working on *before* loading workflows.

1.  **Read `agent/ROUTING_RULES.md`** (Count: 3) to understand scope resolution.
2.  **Determine Scope**:
    *   Synthesize explicit user path + file status + open files.
    *   *Result:* `ACTIVE_SCOPE` (e.g., `backend/api`, `frontend/web`, `root`).
3.  **Detect Stack/Component**:
    *   Read `agent/components/<ACTIVE_SCOPE>.md` (Count: 4) if it exists.
    *   *Result:* `STACK` (e.g., `python`, `node`, `cpp`).

## 4. Select & Load Plan
Based on `ACTIVE_SCOPE` and `STACK`:

1.  **Identify Intent**: (Feature, Bug, Question, etc.)
2.  **Select Workflow**: Use `ROUTING_RULES.md` logic to pick the *single* best workflow file.
3.  **Budget Check**:
    *   If you need to read > 3 more files to start, **STOP**.
    *   Switch to "Plan Only" mode: Describe what you *would* read and ask for confirmation.
4.  **Execute**:
    *   Read the selected workflow file (Count: 5).
    *   Follow its instructions.

---
**PROHIBITIONS:**
*   ❌ Do NOT read `00_INDEX.md` (it is a redirect, just read `00_BOOTSTRAP.md` directly).
*   ❌ Do NOT read `agent/checklists/` unless the workflow tells you to.
*   ❌ Do NOT read project code yet. Focus on *planning* the route.
