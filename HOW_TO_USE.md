# How to Use Agent OS

## Instructions for the Human User

1. **Deployment**: Copy the `agent/` folder into the root of your repository.
2. **Standard Mode**: For simple tasks, copy a prompt from `prompts/by_entrypoint/` or `prompts/by_scenario/` and paste it into your AI.
3. **Orchestrated Mode**: For complex, multi-phase projects, copy `prompts/orchestrator/00_orchestrator_master_prompt.txt` and paste it into your AI.
4. **Monitoring**: Check `agent/09_state/` frequently to see where the Agent thinks the project stands.
5. **Approval**: The Agent will stop at "Gates" (defined in `05_gates/`) and wait for your feedback or automated test confirmation.
6. **Reference Examples**: For Docker/GitHub setups, check `prompts/examples_devops/` for copy-paste ready implementations.

## Instructions for the AI Assistant

1. **Read-First Policy**: Before taking any action, you MUST read the appropriate Entrypoint in `01_entrypoints/`.
2. **Orchestration**: If operating in orchestrated mode, follow the `agent/00_system/10_orchestration_protocol.md` and use the `11_prompt_router.md`.
3. **State Management**: Every significant change to the repository must be reflected in `09_state/PROJECT_STATE.md`.
4. **Template Adherence**: All planning documents MUST follow the templates in `07_templates/` and be saved to the paths defined in `08_plan_output_contract/`.
5. **Profile Switching**: Explicitly state which profile you are adopting (from `03_profiles/`) or which sub-agent role you are fulfilling at the start of a task.

## Execution Modes

### Single-Agent Mode (Manual)

Best for quick fixes, single features, or when you want to control every step.

- **Entrypoint**: Use `prompts/by_entrypoint/` directly.
- **Roles**: Manually switch profiles as needed.

### Orchestrated Mode (Auto)

Best for large features, new projects, or high-fidelity security/quality requirements.

- **Entrypoint**: `agent/01_entrypoints/run_orchestrator.md`.
- **Master Prompt**: `prompts/orchestrator/00_orchestrator_master_prompt.txt`.
- **Process**: Decomposes work into subtasks assigned to specialized virtual agents.

## Typical Flow (Orchestrated)

1. **User**: Pastes the Orchestrator Master Prompt + request.
2. **Orchestrator**: Analyzes situation -> Selects prompt via Router -> Decomposes into Taskboard.
3. **Virtual Agents**: Execute roles (Planner, Analyst, Architect, etc.) sequentially.
4. **Merge**: Orchestrator reconciles all outputs into a final coherence report.
5. **Gates**: Final global and stack-specific gates are validated.

## Troubleshooting

- If the Agent is confused, tell it to: "Reset state and read `00_system/00_principles.md`."
- If the Orchestrator selects the wrong prompt, use `prompts/cheatsheets/prompt_selector.md` to point it to the correct one.
- If the Agent's code style is wrong, point it to `11_rules/code_style_rules.md`.
