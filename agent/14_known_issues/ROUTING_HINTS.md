# Routing Hints

**System**: Fast-Track Resolver  
**Purpose**: Map symptoms to known solutions (Skills or KIs)

---

## Usage

When identifying an issue type/error, check this table for a recommended path.

---

## Hint Map

| Symptom / Keyword | Root Cause (Likely) | Recommended Action / Skill / KI |
|---|---|---|
| `open ... no such file` | File path incorrect | Check absolute path usage |
| `npm install` slow/hangs | Network/Registry | Use `skill_manage_dependencies` with audit |
| `docker build` fails context | Missing .dockerignore | Check `gate_global_docker` & add ignore |
| `pnpm` not found | Missing Corepack | Install pnpm via corepack enable |
| `Module not found` (Monorepo) | Hoisting/Linking | Check `multi_stack_rules.md` |
| `Error: Manifest not found` | Path mismatch | See `KI-20260121-manifest-loc` |
| `Rules overload` | Too many files read | See `KI-20260121-rules-overhead` |
| `React` import error | Vite config | See `stack_rules/react_rules.md` |
| `security scan failed` | Secrets or Vulns | Run `gate_global_security` remediation |
| `gh auth status` shows 403/SSO required | Token scopes/SSO | See `agent/15_tech_hard_cases/github.md` + prompt `prompts/hard_cases/github_hard_cases.txt` |
| `actions cache not found` or poisoned | Cache keys wrong | See `HC-GITHUB-006` via GitHub hard cases prompt |
| `GLIBCXX_3.4.x not found` | Stdlib/ABI mismatch | Route to `agent/15_tech_hard_cases/cpp.md` (HC-CPP-004/021) |
| `undefined reference` in CMake target | Link scope/order | Use `agent/15_tech_hard_cases/cpp.md` + `cmake.md`; prompt `prompts/hard_cases/cmake_hard_cases.txt` |
| `CMake Error: generator ... does not match` | Build dir reused | See `HC-CMAKE-001` via CMake hard cases prompt |
| `mvn dependency:tree` shows conflicts / `ResolutionException` | Version hell | Use `agent/15_tech_hard_cases/java.md` HC-JAVA-001; prompt `prompts/hard_cases/java_hard_cases.txt` |
| `pip resolver` conflicts / `ResolutionImpossible` | Dependency pins | Route to `agent/15_tech_hard_cases/python.md` HC-PY-002; prompt `prompts/hard_cases/python_hard_cases.txt` |
| `RuntimeError: Working outside of application context` (Flask) | App factory/ctx misuse | See `agent/15_tech_hard_cases/flask.md` HC-FLASK-001; prompt `prompts/hard_cases/flask_hard_cases.txt` |
| `MissingPluginException` (Flutter) | Platform channel registration | Use `agent/15_tech_hard_cases/flutter.md` HC-FLUTTER-009; prompt `prompts/hard_cases/flutter_hard_cases.txt` |
| `Refused to load the script because it violates the CSP` | CSP misconfig | Route to `agent/15_tech_hard_cases/static_web.md` HC-STATICWEB-005; prompt `prompts/hard_cases/static_web_hard_cases.txt` |

---

## Adding Hints

1. If an issue occurs > 3 times, add a hint here.
2. Link to a specific Skill or Known Issue if possible.
