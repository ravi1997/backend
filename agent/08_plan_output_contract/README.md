# Plan Output Contract: README

## Purpose

This document defines the strict agreement on **where** the Agent stores its generated planning artifacts. This ensures both models and humans can always find data.

## Rules

1. **Never change the root**: All plans must live in the project root under `/plans/`.
2. **Strict Hierarchy**: Follow the `folder_layout.md`.
3. **No Orphans**: Every file in `/plans/` must be referenced in a Workflow or State file.
4. **Immutable Names**: Use the naming conventions in `naming_conventions.md`.

## Concluding Note

If a tool expects a file at a certain path and it is missing, the Agent must trigger a "State Recovery" to find or regenerate it.
