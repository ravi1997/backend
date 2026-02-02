# Gate Index

## Global Gates (`agent/05_gates/global/`)

- `agent/05_gates/global/gate_global_quality.md`: Primary code quality and testing thresholds.
- `agent/05_gates/global/gate_global_security.md`: Safety, secrets management, and zero-trust.
- `agent/05_gates/global/gate_global_build.md`: Clean compilation and deployability.
- `agent/05_gates/global/gate_global_release.md`: Final production readiness and rollback.
- `agent/05_gates/global/gate_performance.md`: Latency, bundle size, and efficiency.
- `agent/05_gates/global/gate_accessibility.md`: WCAG 2.1 and semantic UI compliance.
- `agent/05_gates/global/gate_global_docker.md`: Docker containerization best practices.
- `agent/05_gates/global/gate_global_ci_github.md`: GitHub Actions CI/CD requirements.
- `agent/05_gates/global/gate_global_docs.md`: Minimum doc requirements.

## Stack Gates (`agent/05_gates/by_stack/`)

### Python

- `agent/05_gates/by_stack/python/gate_python.md`: Black, Flake8, and Mypy.
- `agent/05_gates/by_stack/python/gate_python_security.md`: Bandit and Pip-audit.

### Node/Next/React

- `agent/05_gates/by_stack/node/gate_node.md`: NPM ecosystem rules.
- `agent/05_gates/by_stack/nextjs/gate_nextjs.md`: SSR and hydrations rules.

## Enforcement (`agent/05_gates/enforcement/`)

- `agent/05_gates/enforcement/gate_failure_playbook.md`: What to do when a gate fails.
- `agent/05_gates/enforcement/gate_exception_policy.md`: Rules for bypassing a gate (rare).
- `agent/05_gates/enforcement/gate_signoff_checklist.md`: The binary "Ready" signal.

## Checklist Add-Ons (New)

- `agent/12_checks/checklists/cpp_build_release_checklist_addon.md`: Release/build gate for C++ (toolchain/ABI/packaging).
- `agent/12_checks/checklists/python_packaging_checklist_addon.md`: Packaging gate for Python (lock, build, security).
- `agent/12_checks/checklists/flutter_release_checklist_addon.md`: Release gate for Flutter (SDK pinning, signing, assets, perf).
- `agent/12_checks/checklists/static_web_accessibility_checklist_addon.md`: Accessibility gate for static web (WCAG, focus, contrast).
