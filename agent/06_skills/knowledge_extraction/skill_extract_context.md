# Skill: Strategic Context Extraction

## Purpose

Deep reading of repository metadata to identify core business logic and non-functional constraints.

## Execution Procedure

1. **Metadata Scan**: Read `package.json`, `pyproject.toml`, `Dockerfile`, and `README.md`.
2. **Constraint Identification**: Extract language versions, environment variables, and external service requirements.
3. **Core Logic Search**: Locate the primary handler or "Main" logic folder.
4. **Summary**: Compile a "Context Snapshot" for the sub-agent.

## Output Contract

- **Context Brief**: Passed to the sub-agent during handoff.
