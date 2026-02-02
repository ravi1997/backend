# System Principle: Self-Evolution

## Purpose

Enables the Agent OS to improve its own instructions, gates, and workflows based on real-world performance and user feedback.

## Core Mandates

1. **Performance Journaling**: After every major milestone, perform a "Post-Mortem".
2. **Workflow Refinement**: If a workflow step consistently fails, propose an edit.
3. **Template Versioning**: Update templates if output consistently lacks detail.
4. **Knowledge Compound**: Upstream new patterns to `agent/02_detection/` or `agent/11_rules/`.
5. **Issue Registry**: When a non-trivial issue is solved, creating a Known Issue entry is MANDATORY.

## Procedure for Self-Update

1. **Identify**: Notice a pattern of failure or inefficiency.
2. **Propose**: Generate a new version of the specific `agent/` file.
3. **Verify**: Ensure the update doesn't break cross-references.
4. **Human Approval**: Ask for approval before overwriting `agent/` files.

## Known Issue Protocol (Mandatory)

When a recurring technical block is resolved:

1. **Document**: Create a `KI-YYYYMMDD-slug.md` file in `agent/14_known_issues/`.
2. **Index**: Add it to `KNOWN_ISSUES_INDEX.md`.
3. **Hint**: Add a routing hint to `ROUTING_HINTS.md` if useful for future detection.

## Constraint

- NEVER delete safety principles or security gates. Self-evolution is for efficiency and clarity, not for bypassing constraints.
