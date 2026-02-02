# How to Use: Agent OS

## 1. Onboarding the Agent

When you start a session with an AI Agent, your first message should be:
> "Read `agent/AGENT_MANIFEST.md` and follow the `run_existing_project.md` entrypoint."

## 2. Navigating the Lifecycle

The Agent OS follows a rigid sequence to prevent design drift:

### Phase A: Discovery

- The Agent uses `agent/02_detection/` to understand your stack.
- It builds a map of your repo using `skill_generate_project_map.md`.

### Phase B: Specification (SRS)

- The Agent will propose an SRS in `plans/SRS/` using templates from `agent/07_templates/srs/`.
- **User Action**: You MUST approve the SRS before any code is written.

### Phase C: Implementation Loop

- For every task, the Agent adopts the `profile_implementer.md`.
- It follows the `06_feature_implementation_loop.md`.
- **Validation**: It will run tests and gates automatically.

## 3. Profile Commands

You can manually trigger profile shifts:

- "Adopt `profile_architect.md` and review this schema."
- "Adopt `profile_security_auditor.md` and scan for vulnerabilities."
- "Adopt `profile_devops_engineer.md` and Dockerize the app."

## 4. Troubleshooting Gate Failures

If a Gate fails:

1. Read the Failure Reason in the Agent response.
2. The Agent will automatically consult `agent/05_gates/enforcement/gate_failure_playbook.md`.
3. Fix the violation and re-run the gate command provided by the Agent.

## 5. Session Persistence

The Agent keeps track of progress in `agent/09_state/`. If you start a new session, simply tell the Agent to:
> "Read `agent/09_state/PROJECT_STATE.md` to resume the last task."
