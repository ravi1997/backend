# Orchestration Protocol

The Orchestrator is the high-level cognitive layer that manages complex tasks by:

1. Decomposing requests into subtasks.
2. Routing subtasks to specialized sub-agents.
3. Merging outputs into a coherent result.

## Lifecycle

1. **Intake**: Analyze User Request.
2. **Routing**: Select best prompt/profile.
3. **Execution**: Spawn sub-agent (one-shot or chat).
4. **Synthesis**: Combine artifacts.
5. **Review**: Check against gates.
