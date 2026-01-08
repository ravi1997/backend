# Component Release Map

This file tracks the current version state of all components in the monorepo. It is the source of truth for "what is live" and "what is next".

## Active State

| Component ID | Current Version | Last Release Date | Depends On (Shared) |
| :--- | :--- | :--- | :--- |
| `example-api` | `1.0.1` | 2024-01-01 | `lib/auth`, `lib/utils` |
| `example-web` | `2.1.0` | 2024-01-05 | `lib/ui-kit` |
| `data-worker` | `0.5.0` | 2023-12-20 | `lib/utils` |

> **Note**: The "Component ID" matches the entries in `agent/component_registry/REGISTRY.md` (if exists) or the directory name.

---

## Pending Release Queue
*Agent Use Only: Populate this section during the "Release Selection Gate" phase.*

**Topology**: `PER_COMPONENT`

| Component | Target Version | Reason (Commit/Feature) | Impacted Shared Libs |
| :--- | :--- | :--- | :--- |
| `[PENDING]` | `...` | `...` | `...` |

---

## History Log
- **2024-01-05**: Released `example-web` v2.1.0 (Feat: New Dashboard).
- **2024-01-01**: Released `example-api` v1.0.1 (Fix: Auth timeout).
