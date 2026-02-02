# Tech Hard Cases Index

## Overview

This directory contains detailed, real-world failure scenarios for each supported technology stack (hard cases + add-ons). Each file documents:

- Symptom signatures (error messages, logs)
- Likely root causes
- Fast diagnosis commands
- Step-by-step fix procedures
- Prevention strategies

## Files

### Infrastructure & DevOps

- **[docker.md](docker.md)** - Docker build/runtime/networking/compose/security/performance issues (30 cases; add-on extended cases)
- **[github.md](github.md)** - GitHub authentication, CI/CD, branching/PR, issues, and release issues (22 cases)

### Systems Programming

- **[cpp.md](cpp.md)** - C++17/20/23 toolchain, build/link, language, runtime, packaging, perf, and security issues (32 cases)
- **[cmake.md](cmake.md)** - CMake generator/cache, dependency discovery, target scoping, and cross-compilation issues (25 cases)

### Application Development

- **[java.md](java.md)** - Java/Maven/Gradle, Spring, runtime, security, and packaging issues (25 cases)
- **[python.md](python.md)** - Python environment, packaging, runtime, security, performance, and testing issues (32 cases)
- **[flask.md](flask.md)** - Flask app factory, blueprints, config, deployment, and security issues (25 cases)
- **[flutter.md](flutter.md)** - Flutter build flavors, platform-specific, pub, and performance issues (25 cases)

### Web Development

- **[static_web.md](static_web.md)** - HTML/CSS/JS bundling, CSP/CORS, XSS, performance, and accessibility issues (25 cases)

## Issue-Key Format

All hard cases use the format: `HC-<TECH>-XXX`

- HC = Hard Case
- TECH = Technology identifier (DOCKER, GITHUB, CPP, CMAKE, JAVA, PYTHON, FLASK, FLUTTER, STATICWEB)
- XXX = Sequential number (001-999)
- Incident records should include `Issue-Key: <TECH>-<hash>` (example: `Issue-Key: DOCKER-12af9c`)
- Recommended prompts: `prompts/hard_cases/<tech>_hard_cases.txt`

## Usage

1. **Identify the symptom** - Look for error messages or behavior patterns
2. **Find the matching hard case** - Search by error signature or symptom
3. **Run diagnosis commands** - Gather evidence
4. **Apply the fix** - Follow step-by-step instructions
5. **Implement prevention** - Add gates, tests, or CI checks

## Related Directories

- **Recovery Playbooks**: `agent/16_recovery_playbooks/` - Step-by-step recovery procedures
- **Caveats**: `agent/17_caveats/` - Common pitfalls and anti-patterns
- **Diagnostics**: `agent/18_diagnostics/` - Automated diagnostic command bundles
- **Prompts**: `prompts/hard_cases/` - Ready-to-run prompts for automated fixes

## Cross-References

- Gates: `agent/05_gates/`
- Rules: `agent/11_rules/`
- Known Issues: `agent/14_known_issues/`
- Examples: `agent/13_examples/`

## Maintenance

When adding new hard cases:

1. Assign next sequential HC-<TECH>-XXX number
2. Include all required sections (Symptom, Causes, Diagnosis, Fix, Prevention)
3. Update this index
4. Create corresponding recovery playbook entry
5. Add diagnostic commands if needed
6. Update routing hints in `agent/14_known_issues/ROUTING_HINTS.md`
