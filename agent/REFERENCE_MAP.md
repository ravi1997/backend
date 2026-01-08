# Reference Map (Tags → Files)

**Purpose:** Quick reference for finding files by tag or category
**When to use:** When you need to locate a specific file quickly
**Format:** `TAG:NAME → path/to/file.md`

---

## 🎯 Entry Points

| Tag | File | Purpose |
|-----|------|---------|
| `BOOTSTRAP` | [`00_BOOTSTRAP.md`](00_BOOTSTRAP.md) | Bootstrap logic (Actual Start) |
| `ENTRYPOINT` | [`00_INDEX.md`](00_INDEX.md) | Legacy router (Redirects to Bootstrap) |
| `SYSTEM` | [`00_SYSTEM.md`](00_SYSTEM.md) | Agent instructions |
| `QUICKSTART` | [`QUICKSTART.md`](QUICKSTART.md) | 30-second setup guide |
| `CONTEXT` | [`01_PROJECT_CONTEXT.md`](01_PROJECT_CONTEXT.md) | Project configuration |
| `CONVENTIONS` | [`02_CONVENTIONS.md`](02_CONVENTIONS.md) | Coding standards & defaults |
| `DEFAULTS` | [`02_CONVENTIONS.md`](02_CONVENTIONS.md) | Default assumptions (Merged) |
| `COMMANDS` | [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) | Quick commands |

---

## 📋 Workflows

| Tag | File | Use When |
|-----|------|----------|
| `WORKFLOW:NGINX_502_504` | [`workflows/nginx_502_504.md`](workflows/nginx_502_504.md) | 502/504 errors |
| `WORKFLOW:FEATURE_DELIVERY` | [`workflows/feature_delivery.md`](workflows/feature_delivery.md) | Building features |
| `WORKFLOW:DEPLOY_MIGRATE` | [`workflows/deploy_and_migrate.md`](workflows/deploy_and_migrate.md) | Deployments |
| `WORKFLOW:SECURITY_INCIDENT` | [`workflows/security_incident.md`](workflows/security_incident.md) | Security issues |
| `WORKFLOW:PERF_PROFILING` | [`workflows/performance_profiling.md`](workflows/performance_profiling.md) | Performance issues |
| `WORKFLOW:MAINTENANCE_MODE` | [`workflows/maintenance_mode.md`](workflows/maintenance_mode.md) | Maintenance windows |
| `WORKFLOW:ROLLBACK_RECOVERY` | [`workflows/rollback_recovery.md`](workflows/rollback_recovery.md) | Rollback procedures |
| `WORKFLOW:DOCKER_DEV_LOOP` | [`workflows/docker_dev_loop.md`](workflows/docker_dev_loop.md) | Docker development |
| `WORKFLOW:SYSTEMD_FAILURES` | [`workflows/systemd_failures.md`](workflows/systemd_failures.md) | systemd issues |
| `WORKFLOW:DB_MIGRATIONS` | [`workflows/db_migrations.md`](workflows/db_migrations.md) | Database migrations |
| `WORKFLOW:DEBUG_BASIC` | [`workflows/debug_basic.md`](workflows/debug_basic.md) | Basic debugging |
| `WORKFLOW:PERFORMANCE` | [`workflows/performance.md`](workflows/performance.md) | Performance tuning |
| `WORKFLOW:SECURITY_SQLI` | [`workflows/security_sqli_path.md`](workflows/security_sqli_path.md) | SQL injection |
| `WORKFLOW:META_MGMT` | [`workflows/agent_meta_management.md`](workflows/agent_meta_management.md) | Update agent rules |
| `WORKFLOW:CPP_LOOP` | [`workflows/cpp_build_test.md`](workflows/cpp_build_test.md) | C++ Build & Test |
| `WORKFLOW:JAVA_LOOP` | [`workflows/java_dev_loop.md`](workflows/java_dev_loop.md) | Java development |
| `WORKFLOW:FLUTTER_LOOP` | [`workflows/flutter_dev_loop.md`](workflows/flutter_dev_loop.md) | Flutter development |

---

## ✅ Checklists (Evidence Collection)

| Tag | File | Use When |
|-----|------|----------|
| `CHECK:NGINX_502` | [`checklists/NGINX_502_EVIDENCE.md`](checklists/NGINX_502_EVIDENCE.md) | 502/504 errors |
| `CHECK:DOCKER_BUILD` | [`checklists/DOCKER_BUILD_FAIL_EVIDENCE.md`](checklists/DOCKER_BUILD_FAIL_EVIDENCE.md) | Docker build fails |
| `CHECK:SYSTEMD_FAIL` | [`checklists/SYSTEMD_FAIL_EVIDENCE.md`](checklists/SYSTEMD_FAIL_EVIDENCE.md) | systemd failures |
| `CHECK:MIGRATION_FAIL` | [`checklists/MIGRATION_FAIL_EVIDENCE.md`](checklists/MIGRATION_FAIL_EVIDENCE.md) | Migration failures |
| `CHECK:PERF_REGRESSION` | [`checklists/PERF_REGRESSION_EVIDENCE.md`](checklists/PERF_REGRESSION_EVIDENCE.md) | Performance issues |

---

## 🔒 Policies (Safety Rules)

| Tag | File | Purpose |
|-----|------|---------|
| `POLICY:PRODUCTION` | [`policy/PRODUCTION_POLICY.md`](policy/PRODUCTION_POLICY.md) | Production safety (347 lines) |
| `POLICY:PHI_SAFE` | [`policy/PHI_SAFE_LOGGING.md`](policy/PHI_SAFE_LOGGING.md) | PHI/PII redaction |
| `POLICY:COMMAND_SAFETY` | [`policy/COMMAND_SAFETY.md`](policy/COMMAND_SAFETY.md) | Command safety rules |
| `POLICY:ENV_DETECTION` | [`policy/ENV_DETECTION.md`](policy/ENV_DETECTION.md) | Environment detection |
| `POLICY:RELEASE` | [`agent/release/RELEASE_POLICY.md`](agent/release/RELEASE_POLICY.md) | Release engineering policy |

---

## ✅ Gates (Quality Checks)

| Tag | File | Purpose |
|-----|------|---------|
| `GATE:QUALITY` | [`gates/QUALITY_GATES.md`](gates/QUALITY_GATES.md) | 10 quality gates (401 lines) |
| `GATE:SELF_CHECK` | [`gates/AGENT_SELF_CHECK.md`](gates/AGENT_SELF_CHECK.md) | Hallucination prevention (414 lines) |

---

## 📄 Artifacts (Templates)

| Tag | File | Use When |
|-----|------|----------|
| `ARTIFACT:INCIDENT_REPORT` | [`artifacts/incident_report.md`](artifacts/incident_report.md) | Production incidents |
| `ARTIFACT:POSTMORTEM` | [`artifacts/postmortem.md`](artifacts/postmortem.md) | Major outages |
| `ARTIFACT:PR_SUMMARY` | [`artifacts/pr_summary.md`](artifacts/pr_summary.md) | Pull requests |
| `ARTIFACT:DECISION_RECORD` | [`artifacts/DECISION_RECORD.md`](artifacts/DECISION_RECORD.md) | Technical decisions |
| `ARTIFACT:RUNBOOK` | [`artifacts/runbook.md`](artifacts/runbook.md) | Operational procedures |
| `ARTIFACT:BUILD_LOG` | [`artifacts/BUILD_LOG.md`](artifacts/BUILD_LOG.md) | Build results |
| `ARTIFACT:FLUTTER_ANALYSIS` | [`artifacts/FLUTTER_ANALYSIS.md`](artifacts/FLUTTER_ANALYSIS.md) | Flutter lint results |
| `ARTIFACT:DOCS_MANIFEST` | [`artifacts/DOCS_MANIFEST.md`](artifacts/DOCS_MANIFEST.md) | Documentation tracking |

---

## 🔄 Flows (Decision Trees)

| Tag | File | Purpose |
|-----|------|---------|
| `FLOW:INCIDENT_TRIAGE` | [`flows/INCIDENT_TRIAGE.md`](flows/INCIDENT_TRIAGE.md) | Classify incidents |
| `FLOW:AUTOFIX_LOOP` | [`flows/AUTOFIX_LOOP.md`](flows/AUTOFIX_LOOP.md) | Auto-fix workflow |
| `FLOW:EVIDENCE_COLLECTION` | [`flows/EVIDENCE_COLLECTION.md`](flows/EVIDENCE_COLLECTION.md) | Gather evidence |
| `FLOW:FEATURE_SPEC` | [`flows/FEATURE_SPEC.md`](flows/FEATURE_SPEC.md) | Feature planning |

---

## 🎯 Skills (Specialized Knowledge)

| Tag | File | Purpose |
|-----|------|---------|
| `SKILL:PROJECT_AUTO_SETUP` | [`skills/project_auto_setup.md`](skills/project_auto_setup.md) | Auto-detect project (500+ lines) |
| `SKILL:NGINX_GUNICORN` | [`skills/nginx_gunicorn.md`](skills/nginx_gunicorn.md) | Nginx/Gunicorn debugging |
| `SKILL:DOCKER_COMPOSE` | [`skills/docker_compose_debug.md`](skills/docker_compose_debug.md) | Docker debugging |
| `SKILL:ALEMBIC_MIGRATIONS` | [`skills/alembic_migrations.md`](skills/alembic_migrations.md) | Database migrations |
| `SKILL:PYTEST_DEBUGGING` | [`skills/pytest_debugging.md`](skills/pytest_debugging.md) | Test debugging |
| `SKILL:CPP_CMAKE` | [`skills/cpp_cmake.md`](skills/cpp_cmake.md) | C++ development |
| `SKILL:JAVA_DEV` | [`skills/java_gradle_maven.md`](skills/java_gradle_maven.md) | Java development |
| `SKILL:FLUTTER` | [`skills/flutter.md`](skills/flutter.md) | Flutter development |
| `SKILL:DOCKER` | [`skills/docker.md`](skills/docker.md) | Docker best practices |

---

## 🔧 Autofill & Contracts

| Tag | File | Purpose |
|-----|------|---------|
| `AUTOFILL:INFERENCE` | [`autofill/PATH_AND_SERVICE_INFERENCE.md`](autofill/PATH_AND_SERVICE_INFERENCE.md) | Auto-infer values |
| `AUTOFILL:VARS` | [`autofill/AUTOFILL_VARIABLES.md`](autofill/AUTOFILL_VARIABLES.md) | Variable definitions |
| `CONTRACT:UNIVERSAL_SCHEMA` | [`contracts/UNIVERSAL_PROJECT_SCHEMA.md`](contracts/UNIVERSAL_PROJECT_SCHEMA.md) | Universal config (400+ lines) |
| `CONTRACT:CONTEXT_SCHEMA` | [`contracts/CONTEXT_SCHEMA.md`](contracts/CONTEXT_SCHEMA.md) | Context schema |
| `CONTRACT:REPO_LAYOUT` | [`contracts/REPO_LAYOUT_FLASK.md`](contracts/REPO_LAYOUT_FLASK.md) | Flask layout |

---

## 📝 Forms (Minimal Input)

| Tag | File | Purpose |
|-----|------|---------|
| `FORM:INCIDENT_MIN` | [`forms/INCIDENT_MIN.md`](forms/INCIDENT_MIN.md) | Quick incident report |
| `FORM:FEATURE_MIN` | [`forms/FEATURE_MIN.md`](forms/FEATURE_MIN.md) | Quick feature spec |
| `FORM:DEPLOY_MIN` | [`forms/DEPLOY_MIN.md`](forms/DEPLOY_MIN.md) | Quick deploy checklist |
| `FORM:PROJECT_CONTEXT_MIN` | [`forms/PROJECT_CONTEXT_MIN.md`](forms/PROJECT_CONTEXT_MIN.md) | Minimal context |

---

## 👤 Profiles (Agent Behavior)

| Tag | File | Use When |
|-----|------|----------|
| `PROFILE:DEFAULT` | [`profiles/default.md`](profiles/default.md) | Balanced approach |
| `PROFILE:PRODUCTION_SAFE` | [`profiles/production_safe.md`](profiles/production_safe.md) | Production only |
| `PROFILE:AGGRESSIVE_AUTOFIX` | [`profiles/aggressive_autofix.md`](profiles/aggressive_autofix.md) | Dev/staging only |
| `PROFILE:CPP_DEV` | [`profiles/cpp_developer.md`](profiles/cpp_developer.md) | C++ focus |
| `PROFILE:JAVA_DEV` | [`profiles/java_developer.md`](profiles/java_developer.md) | Java focus |
| `PROFILE:FLUTTER_DEV` | [`profiles/flutter_developer.md`](profiles/flutter_developer.md) | Flutter focus |
| `PROFILE:DOCKER_EXPERT` | [`profiles/docker_expert.md`](profiles/docker_expert.md) | Docker focus |

---

## 📚 Documentation

| Tag | File | Purpose |
|-----|------|---------|
| `DOC:README` | [`README.md`](README.md) | Main documentation |
| `DOC:ARCHITECTURE` | [`ARCHITECTURE.md`](ARCHITECTURE.md) | System architecture (435 lines) |
| `DOC:UNIVERSAL_SUPPORT` | [`UNIVERSAL_SUPPORT.md`](UNIVERSAL_SUPPORT.md) | Language support (600+ lines) |
| `DOC:MIGRATION_GUIDE` | [`MIGRATION_GUIDE.md`](MIGRATION_GUIDE.md) | v3 → v4 upgrade |
| `DOC:QUICK_REFERENCE` | [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) | Cheat sheet |
| `DOC:VERSION` | [`CHANGELOG.md`](CHANGELOG.md) | Version history |

---

## 📖 Examples

| Tag | File | Purpose |
|-----|------|---------|
| `EXAMPLE:PROJECT_CONTEXT` | [`examples/example_project_context.md`](examples/example_project_context.md) | Filled context |
| `EXAMPLE:INCIDENT` | [`examples/example_incident_workflow.md`](examples/example_incident_workflow.md) | Incident workflow |
| `EXAMPLE:FEATURE` | [`examples/example_feature_delivery.md`](examples/example_feature_delivery.md) | Feature delivery |

---

## Usage Examples

### Finding a File by Category
```
Need incident workflow? → WORKFLOW:NGINX_502_504
Need quality gates? → GATE:QUALITY
Need production rules? → POLICY:PRODUCTION
```

### Finding a File by Keyword
```
"502 error" → CHECK:NGINX_502 → WORKFLOW:NGINX_502_504
"migration failed" → CHECK:MIGRATION_FAIL → WORKFLOW:DB_MIGRATIONS
"security issue" → WORKFLOW:SECURITY_INCIDENT
```

---

## See Also

- [`ROUTING_RULES.md`](ROUTING_RULES.md) - Keyword-based routing
- [`TAXONOMY.md`](TAXONOMY.md) - Error categorization
- [`00_INDEX.md`](00_INDEX.md) - Main router

