# Recovery Playbooks Index

Purpose: fast recovery steps mapped to hard cases (`HC-<TECH>-XXX`). Each playbook aligns with Issue-Key format `Issue-Key: <TECH>-<hash>` and prompt files `prompts/hard_cases/<tech>_hard_cases.txt`.

## Files
- `docker_recovery.md` — build/runtime/network/add-on recovery (RECOVERY-DOCKER-001..011).
- `github_recovery.md` — auth/CI/PR/release recovery (RECOVERY-GITHUB-001..005).
- `cpp_recovery.md` — toolchain/linking/runtime/perf/security recovery.
- `cmake_recovery.md` — generator/cache/dependency/install/cross recovery.
- `java_recovery.md` — dependency/build, Spring wiring, runtime/GC, packaging recovery.
- `python_recovery.md` — env/deps, packaging, imports, async, security, perf recovery.
- `flask_recovery.md` — app factory/config, DB/migrations, proxy/security recovery.
- `flutter_recovery.md` — SDK/tooling, platform channels, assets/l10n, CI, perf/release recovery.
- `static_web_recovery.md` — assets/paths, CSP/CORS, performance, accessibility, runtime error recovery.
