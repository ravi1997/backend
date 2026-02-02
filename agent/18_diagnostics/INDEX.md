# Diagnostics Bundles Index

Run these command bundles before fixing issues. Pair with Issue-Key `Issue-Key: <TECH>-<hash>` and hard-case prompts (`prompts/hard_cases/<tech>_hard_cases.txt`).

## Files
- `docker_diagnostics.md` — build/runtime/network/permissions diagnostics plus add-on BuildKit/rootless/compose checks.
- `github_diagnostics.md` — auth/rate limits, secrets, branch protection, cache/matrix, runner disk checks.
- `cpp_diagnostics.md` — toolchain/build flags, link info, sanitizers, packaging/install probes.
- `cmake_diagnostics.md` — generator/cache, find_package tracing, FetchContent inspection, install dry-runs.
- `java_diagnostics.md` — dependency graphs, test discovery, Spring/GC/container checks.
- `python_diagnostics.md` — interpreter/env, pip checks, build, import timing, security scans.
- `flask_diagnostics.md` — app factory/routes, config snapshot, migrations, proxy/headers checks.
- `flutter_diagnostics.md` — SDK info, pub/analyzer/tests, Android/iOS tooling, assets/flavors, size/perf.
- `static_web_diagnostics.md` — build+serve preview, CSP/CORS headers, Lighthouse/axe, bundle analysis, SW/cache checks.
