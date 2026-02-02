# Skill: Project Topology & Mapping

## Purpose

Generating a human-readable and AI-navigable map of a new or large codebase.

## Execution Procedure

1. **Crawl**: Run `ls -R` and `grep` for main entrypoints.
2. **Topology Identification**: Determine if Monorepo, Microservice, or Monolith.
3. **Dependency Graph**: Map how `src/` modules interact.
4. **Map Creation**: Generate a `PROJECT_MAP.md`.

## Output Contract

- **Project Map**: Saved to `plans/Architecture/PROJECT_MAP.md`.
