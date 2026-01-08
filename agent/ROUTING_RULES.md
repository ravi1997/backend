# Routing Rules (Scope → Stack → Workflow)

**Purpose:** Deterministically map user requests to the correct component and workflow.
**Core Logic:** **Scope First, Stack Second.**
**Priority:**
1.  **Scope:** Which component is the user talking about?
2.  **Stack:** What technology does that component use?
3.  **Intent:** What is the user trying to do (Feature, Bug, Release)?

---

## 🛑 MANDATORY PREAMBLE: Determine ACTIVE_SCOPE

> **Context Budget Warning**: You should already be in **Pass 1** (Bootstrap Mode).
> Do NOT read files outside the budget defined in `agent/CONTEXT_BUDGET.md`.

Before routing ANY request, the Agent **MUST** determine the `ACTIVE_SCOPE`.

### Scope Resolution Ladder (Rules & Precedence)

The agent determines the `ACTIVE_SCOPE` by evaluating the following rules in order. The **first rule that matches** determines the scope.

#### 1. Explicit User Instructions
**If** the user explicitly mentions a specific directory, component name, or path in their prompt.
**Then** that target becomes the `ACTIVE_SCOPE`.
> *Example:* "Fix the build errors in `apps/web`." -> Scope: `apps_web`

#### 2. Contextual Invocation (IDE)
**If** the agent is invoked from a specific subdirectory within the IDE (and the IDE passes this context).
**Then** the component rooted at or nearest to that directory becomes the `ACTIVE_SCOPE`.
> *Example:* User right-clicks `services/api/src/main.py` -> Scope: `services_api`

#### 3. Edited Files Context (Git/Status)
**If** the task involves modifying specific files.
**Then** the smallest matching component that contains the majority of the edited files becomes the `ACTIVE_SCOPE`.
> *Example:* User asks to refactor `packages/ui/Button.tsx`. -> Scope: `packages_ui`

#### 4. Root Fallback
**If** none of the above apply, or if the request is global (e.g., "Update the README").
**Then** the `root` component (repository root) is the `ACTIVE_SCOPE`.

### Ambiguity Resolution
If the scope remains ambiguous:
1.  **Default to Root**: Assume the user means the entire repository.
2.  **Ask for Clarification**: If a destructive action is imminent, **PAUSE** and ask.

### Loading Component Config

Once `ACTIVE_SCOPE` is determined:
1.  **Read:** `agent/components/<scope_name>.md` (if it exists).
2.  **Identify Stack:** Look for `Stack: <type>` (e.g., `python`, `cpp`, `flutter`).
3.  **Load Context:** Use this stack to select the correct specific workflow.

---

## 🚦 Routing Logic

### 1. Cross-Component Safety Check
**If the request involves changes:**
1.  **List Impacted Components:** Does this change affect others? (e.g., changing a shared API model).
2.  **Safety Plan:**
    *   If **YES**: Generate commands to run minimal checks in *dependent* components.
    *   *Note:* If dependent component environment is not available, **generate the commands anyway** for the user to run later.

### 2. Match Intent & Route by Stack

Use the **Keywords** below to determine verify *Intent*, then use **Component Stack** to route.

#### 🔴 Priority 1: Incidents (Production/Dev Support)

| Intent | Keywords | Universal Route |
| :--- | :--- | :--- |
| **HTTP 5xx** | `502`, `504`, `bad gateway`, `gateway timeout` | `workflows/nginx_502_504.md` |
| **Service Down** | `systemctl`, `failed`, `dead`, `inactive` | `workflows/systemd_failures.md` |
| **Database** | `connection refused`, `deadlock`, `migration fail` | `workflows/db_migrations.md` |

#### 🟡 Priority 2: Build & Configuration

| Intent | Keywords | component.Stack == 'docker' / Root | component.Stack == 'cpp' | component.Stack == 'web' |
| :--- | :--- | :--- | :--- | :--- |
| **Build Fail** | `build failed`, `make error` | `workflows/docker_dev_loop.md` | `workflows/cpp_build_test.md` | `workflows/web_build.md` |
| **Config** | `env var`, `settings` | `skills/config_update.md` | - | - |

#### 🟢 Priority 3: Feature & Changes

| Intent | Keywords | Route Logic |
| :--- | :--- | :--- |
| **New Feature** | `add`, `create`, `implement`, `feature` | **1.** Load `agent/workflows/_stack/<stack>_feature_delivery.md` <br> **2.** If missing, use `workflows/feature_delivery.md` |
| **Refactor** | `refactor`, `clean up`, `optimize` | Same as above. |

#### 🔵 Priority 4: Testing & Quality

| Intent | Keywords | component.Stack == 'python' | component.Stack == 'java' | component.Stack == 'flutter' |
| :--- | :--- | :--- | :--- | :--- |
| **Test Fail** | `test`, `fail`, `pytest`, `junit` | `skills/pytest_debugging.md` | `workflows/java_dev_loop.md` | `workflows/flutter_dev_loop.md` |
| **Linting** | `lint`, `format`, `style` | `skills/python_linting.md` | - | `skills/flutter_linting.md` |

---

## 🔄 Execution Flow Summary

1.  **Input:** User Request + Context.
2.  **Step A: Scope:** Identify `ACTIVE_SCOPE` (e.g., `backend_service`).
3.  **Step B: Stack:** Read `backend_service.md` -> Stack is `python`.
4.  **Step C: Intent:** Keywords match "add new endpoint" -> Intent: **Feature**.
5.  **Step D: Safety:** Is this a shared library? No. Proceed.
6.  **Step E: Route:** Execute `agent/workflows/_stack/python_feature_delivery.md`.

---

## ❓ Ambiguity Resolution

If **Scope** is unclear:
> "I see you want to [Intent]. Which component are you working on? (Detected: [A], [B])"

If **Stack** is unknown (missing component file):
> "I cannot find config for [Scope]. Proceeding with Generic/Universal workflows."
