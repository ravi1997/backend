# Caveats & Footguns Index

Use Issue-Key format `Issue-Key: <TECH>-<hash>` and pair with hard cases and prompts (`prompts/hard_cases/<tech>_hard_cases.txt`). These caveats add guardrails and prevention steps.

## Files
- `docker_caveats.md` — secrets, tagging, SBOM, .dockerignore patterns, add-on rootless/BuildKit/compose cautions.
- `github_caveats.md` — auth scopes, SSO, cache safety, branch protection, issue hygiene; Issue-Key dedupe rules.
- `cpp_caveats.md` — toolchain/stdlib alignment, target-based linking, constexpr/std rules, sanitizer caveats.
- `cmake_caveats.md` — golden CMake patterns, generator/toolchain hygiene, FetchContent pinning.
- `java_caveats.md` — wrappers, BOMs, Spring security/CORS, logging, timezone/GC safety.
- `python_caveats.md` — venv enforcement, lockfiles, async safety, security bans, packaging data hygiene.
- `flask_caveats.md` — app factory, config safety, SECRET_KEY, DB sessions, security headers/rate limits.
- `flutter_caveats.md` — SDK pinning, null-safety, AGP/CocoaPods, signing, assets/goldens determinism.
- `static_web_caveats.md` — path/case safety, CSP/XSS, a11y requirements, caching and cross-browser caveats.
