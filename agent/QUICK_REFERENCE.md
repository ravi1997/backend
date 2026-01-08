# Quick Reference Card

**AI Agent MD Pack v4** - One-page cheat sheet

---

## 🚀 Setup (30 seconds)

```bash
# 1. Copy folder
cp -r agent/ /path/to/your/project/

# 2. Fill context (minimum: app_name + env)
vim agent/01_PROJECT_CONTEXT.md

# 3. Start using
# Tell agent: "Read agent/00_INDEX.md"
```

---

## 📋 Common Commands

| Command | What It Does |
|---------|--------------|
| `fix this error: [paste log]` | Incident response |
| `implement feature: [description]` | Feature development |
| `deploy to [env]` | Deployment |
| `review logs for [pattern]` | Security audit |
| `profile slow endpoint [path]` | Performance analysis |
| `add tests for [feature]` | Test creation |

---

## 🗺️ Routing Decision Tree

```
User Request
    │
    ├─ Contains error/502/504/crash? ──→ INCIDENT_TRIAGE
    ├─ Contains implement/feature/add? ──→ FEATURE_DELIVERY
    ├─ Contains deploy/migrate/release? ──→ DEPLOY_MIGRATE
    ├─ Contains security/attack/injection? ──→ SECURITY_INCIDENT
    └─ Contains slow/latency/performance? ──→ PERF_PROFILING
```

---

## 📁 Key Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `00_INDEX.md` | Main router | Every request |
| `01_PROJECT_CONTEXT.md` | Your config | Setup once |
| `QUICKSTART.md` | Getting started | First time |
| `ARCHITECTURE.md` | System design | Understanding |
| `examples/` | Real examples | Learning |

---

## 🎯 Workflows Quick Ref

| Workflow | File | Use When |
|----------|------|----------|
| **Incident** | `flows/INCIDENT_TRIAGE.md` | Errors, crashes, outages |
| **Feature** | `workflows/feature_delivery.md` | New features |
| **Deploy** | `workflows/deploy_and_migrate.md` | Deployments |
| **Nginx 502** | `workflows/nginx_502_504.md` | Proxy errors |
| **Docker** | `workflows/docker_dev_loop.md` | Container issues |
| **Security** | `workflows/security_incident.md` | Security concerns |
| **Performance** | `workflows/performance_profiling.md` | Slow endpoints |

---

## 🔐 Safety Checklist

Before any action:
- ✅ Environment detected correctly?
- ✅ PHI/PII will be redacted?
- ✅ Production = read-only?
- ✅ Evidence collected first?
- ✅ Rollback plan exists?

---

## 🎨 Profiles

| Profile | Use In | Behavior |
|---------|--------|----------|
| `default.md` | Dev/Staging | Balanced, evidence-first |
| `production_safe.md` | Production | Read-only, conservative |
| `aggressive_autofix.md` | Dev only | Auto-fix, fast |

---

## 📊 Autofill System

**You provide:**
```yaml
app_name: "myapp"
env: "dev"
```

**Agent infers:**
- `backend_dir` from repo structure
- `entrypoint` from app.py/wsgi.py
- `app_port` from docker-compose.yml
- `compose_backend_service` from services
- `python_package` from __init__.py

---

## 🛠️ Quality Gates

Before marking complete:
1. ✅ Tests pass (`pytest`)
2. ✅ Lints pass (`ruff check`)
3. ✅ Format applied (`ruff format`)
4. ✅ Security reviewed
5. ✅ Artifact generated

---

## 📦 Artifacts Generated

| Type | Template | Contains |
|------|----------|----------|
| Incident | `incident_report.md` | Root cause, fix, prevention |
| Feature | `pr_summary.md` | Changes, tests, deployment |
| Decision | `DECISION_RECORD.md` | Design choices, alternatives |
| Deploy | `runbook.md` | Steps, verification, rollback |
| Postmortem | `postmortem.md` | Timeline, lessons learned |

---

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent asks too many questions | Fill more in `01_PROJECT_CONTEXT.md` |
| Wrong workflow selected | Use specific keywords |
| Production safety blocking | Check `env:` in context |
| Can't find files | Verify `repo_root` setting |
| Autofill not working | Check standard project layout |

---

## 📚 Learning Path

1. **Day 1:** Read `QUICKSTART.md`, fill `01_PROJECT_CONTEXT.md`
2. **Day 2:** Try incident workflow with test error
3. **Day 3:** Try feature workflow with small feature
4. **Week 1:** Review `ARCHITECTURE.md`, customize workflows
5. **Month 1:** Add custom workflows, extend skills

---

## 🔗 Quick Links

- **Start:** [`QUICKSTART.md`](QUICKSTART.md)
- **Setup:** [`COPY_INTO_NEW_REPO.md`](COPY_INTO_NEW_REPO.md)
- **Docs:** [`README.md`](README.md)
- **Design:** [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Examples:** [`examples/`](examples/)
- **Migrate:** [`MIGRATION_GUIDE.md`](MIGRATION_GUIDE.md)

---

## 💡 Pro Tips

1. **Start minimal** - Fill only `app_name` and `env`, let autofill do the rest
2. **Use examples** - Copy from `examples/` directory
3. **Trust the router** - `00_INDEX.md` knows what to do
4. **Evidence first** - Always collect logs before fixing
5. **Small changes** - Incremental is safer than big bang

---

## 🆘 Emergency Commands

```bash
# View agent routing
cat agent/00_INDEX.md

# Check your config
cat agent/01_PROJECT_CONTEXT.md

# See all workflows
ls agent/workflows/

# Find a workflow
grep -r "nginx" agent/workflows/

# Check autofill rules
cat agent/autofill/PATH_AND_SERVICE_INFERENCE.md
```

---

**Version:** 4.0 | **Updated:** 2026-01-05

**Need help?** → [`README.md`](README.md) | **Examples:** → [`examples/`](examples/)

---

## ⚡ Command Phrase Book (from 10_COMMANDS)
(You speak short; agent does deep)

### Debug / Fix
- `fix this error: <paste traceback/log>`
- `reproduce and fix: <symptom>`
- `write a regression test for: <bug>`
- `why nginx 502? <paste minimal logs>`
- `gunicorn keeps restarting <logs>`

### DevOps
- `make docker dev loop stable`
- `optimize compose for dev`
- `systemd service failing <unit name/logs>`
- `add maintenance mode for app`

### Security
- `harden inputs for route <route>`
- `review logs for sqli/path traversal patterns`
- `add safe request logging middleware`

### Performance
- `profile slow endpoint <path>`
- `reduce memory usage`
- `add caching safely`

### Feature work
- `implement feature: <one sentence>`
- `turn this into tasks: <goal>`
- `generate PR description for <changes>`
