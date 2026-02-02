# Orchestrator Prompts: Human Guide

## Overview

These prompts activate the **Agent OS Orchestrator**, allowing an AI agent to operate as a "manager" that spawns specialized virtual sub-agents (sequential sessions) to handle complex engineering tasks.

## When to Use Individual Prompts vs. Orchestrator

| Use **Single Prompt** When... | Use **Orchestrator** When... |
| :--- | :--- |
| Task is simple (one file change). | Task is complex (multi-file/multi-phase). |
| You only need one role (e.g., just coding). | You need multiple roles (Arch, Code, Test). |
| You are in a hurry (low friction). | Quality and consistency are paramount. |
| The project stack is simple. | The project uses Docker, CI/CD, and multiple tiers. |

## How to Start

1. **Bootstrap**: Copy the content of `00_orchestrator_master_prompt.txt`.
2. **Context**: Paste it into your LLM and provide the user request.
3. **Observation**: Watch the agent create the `plans/Orchestration/` directory and execute sub-agents.

## Decision Matrix: Routing

The Orchestrator uses `agent/00_system/11_prompt_router.md` to decide which prompts from `prompts/` to load. It generally follows this logic:

- **Empty repo?** -> `new_project.txt`.
- **Existing code?** -> `existing_project.txt`.
- **Bug report?** -> `bug_fix.txt`.
- **Outage?** -> `emergency_hotfix.txt`.

## Common Pitfalls & How to Avoid Them

- **Pitfall**: Sub-agents contradicting each other.
  - **Fix**: The Orchestrator automatically uses `CONFLICT_RESOLUTION.md` based on a hierarchy (Security > Architect > Implementer).
- **Pitfall**: Running out of context/tokens.
  - **Fix**: Use the `skill_context_budgeting.md` logic. Only provide sub-agents with the portion of the codebase they are actively modifying.
- **Pitfall**: Skipping gates.
  - **Fix**: The `rule_checker.txt` sub-agent is designed specifically to prevent gate-skipping.

## Profiles Included

- `planner.txt`: Backlog & Milestones.
- `analyst_srs.txt`: Requirements.
- `architect.txt`: Design.
- `implementer.txt`: Code development.
- `tester.txt`: QA.
- `security_auditor.txt`: Risk management.
- `pr_reviewer.txt`: Quality control.
- `rule_checker.txt`: Compliance.
- `release_manager.txt`: Release readiness.
