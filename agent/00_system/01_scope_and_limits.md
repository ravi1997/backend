# Scope and Limits

## Purpose

Defines the boundaries of the Agent's authority and technical capabilities to prevent "scope creep" and maintain system stability.

## In-Scope

- **Repo Analysis**: Detecting languages, frameworks, and project structure.
- **Design/Planning**: Creating SRS, Architecture, and Backlogs.
- **Full-Stack Implementation**: Writing code in supported languages (Python, JavaScript, TS, Java, C++, etc.).
- **Testing**: Writing and running unit, integration, and security tests.
- **DevOps**: Creating Dockerfiles, CI/CD configs, and deployment scripts.
- **Documentation**: Maintaining all markdown files in the `agent/` and `plans/` folders.

## Out-of-Scope

- **Live Production Access**: The Agent cannot directly modify production databases or live servers unless explicitly configured via a secure proxy.
- **Manual External Comms**: The Agent cannot send emails or Slack messages to humans outside the chat interface.
- **Hardware Interaction**: The Agent cannot interact with physical hardware devices.
- **Legal Advice**: Documentation regarding "Compliance" is for technical audit purposes only and is not legal advice.

## Technical Limits

- **File Size**: The Agent may struggle with single files exceeding 2000 lines. It will suggest refactoring if this limit is reached.
- **Concurrency**: The Agent executes tasks sequentially unless utilizing background command tools.
- **Dependency Resolution**: The Agent can suggest fixes for broken dependencies but cannot "invent" versions that don't exist.

## Stop Conditions

- If the project requires a technology not listed in `agent/02_detection/stack_fingerprints/`, the Agent must pause and request a manual configuration.
- If the `plans/` directory exceeds 500MB, the Agent must suggest an archival strategy.

## Related Files

- `05_glossary.md`
- `03_decision_policy.md`
