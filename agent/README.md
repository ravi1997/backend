# Agent OS: Global README

## 🚀 Mission

To provide a standardized, high-integrity environment for AI-driven software engineering that ensures 100% consistency, quality, and safety across any technology stack.

## 📂 System Structure

| Component | ID | Description |
| --- | --- | --- |
| **System** | `00` | Principles, response protocols, and orchestration logic. |
| **Entrypoints** | `01` | Scenario-based triggers (New project, Bug fix, etc.). |
| **Detection** | `02` | Automated stack fingerprinting and repo health assessment. |
| **Profiles** | `03` | Persona-based instructions (Architect, DevOps, UX, etc.). |
| **Workflows** | `04` | Step-by-step SDLC execution playbooks. |
| **Gates** | `05` | Mandatory quality and security checkpoints. |
| **Skills** | `06` | Atomic execution logic (Git hygiene, secret scrubbing). |
| **Templates** | `07` | Ready-to-use document and diagram scaffolds. |

## 🛠️ Quick Start

1. **Initialize**: Provide the Agent with access to your repository.
2. **Boot**: Run `agent/01_entrypoints/run_existing_project.md` (for existing code) or `run_new_project.md`.
3. **Follow the Workflow**: The Agent will guide you through SPEC -> PLAN -> DEV -> RELEASE.
4. **Pass Gates**: No feature is merged without passing `agent/05_gates/global/gate_global_quality.md`.

## ⚖️ Global Constraints (The "Golden Rules")

- **Absolute Paths**: Always use absolute paths for file operations.
- **Root-Relative Links**: Internal documentation links must use `agent/` prefix.
- **Zero Placeholders**: Never produce "TODO" or "TBD" content.
- **State Integrity**: Every cycle must update `agent/09_state/PROJECT_STATE.md`.

## 📚 Documentation Index

- [How to Use](./HOW_TO_USE.md)
- [Quickstart Checklist](./QUICKSTART_CHECKLIST.md)
- [System Principles](./00_system/00_principles.md)
- [Workflow Overview](./04_workflows/00_overview.md)

---
**Version**: 1.1.0 (Audit Upgrade)  
**Maintainer**: Agent OS Maintainer
