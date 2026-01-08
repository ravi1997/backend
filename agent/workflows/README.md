# Workflows Directory

**Purpose:** Step-by-step procedures for common tasks and incidents
**When to use:** When you need guidance on how to handle specific situations

---

## 🔴 Production Incidents (P1)

### HTTP/Proxy Errors
- [`nginx_502_504.md`](nginx_502_504.md) - Handle 502/504 gateway errors

### Service Failures  
- [`systemd_failures.md`](systemd_failures.md) - Debug systemd service failures

### Database Issues
- [`db_migrations.md`](db_migrations.md) - Handle database migration issues

---

## 🟡 Build & Deploy (P2)

- [`docker_dev_loop.md`](docker_dev_loop.md) - Docker development workflow
- [`deploy_and_migrate.md`](deploy_and_migrate.md) - Deployment with migrations

---

## 🟢 Performance (P3)

- [`performance_profiling.md`](performance_profiling.md) - Profile performance issues
- [`performance.md`](performance.md) - General performance optimization

---

## 🔒 Security (P4)

- [`security_incident.md`](security_incident.md) - Handle security incidents
- [`security_sqli_path.md`](security_sqli_path.md) - SQL injection & path traversal

---

## 🔵 Development (P5)

- [`feature_delivery.md`](feature_delivery.md) - End-to-end feature development
- [`debug_basic.md`](debug_basic.md) - Basic debugging workflow

---

## 🟣 Operations (P6)

- [`rollback_recovery.md`](rollback_recovery.md) - Rollback deployments
- [`maintenance_mode.md`](maintenance_mode.md) - Scheduled maintenance
- [`documentation_management.md`](documentation_management.md) - Manage dev/user/test documentation

---

## 🛡️ Development & Management (P7)

- [`application_flow.md`](application_flow.md) - Manage application flows & checks
- [`model_management.md`](model_management.md) - Manage models, classes, & configs
- [`api_management.md`](api_management.md) - Manage routes, APIs, & decorators
- [`test_management.md`](test_management.md) - Manage tests & log results

---

## Quick Reference

| Workflow | Use When | Priority | Time |
|----------|----------|----------|------|
| nginx_502_504 | Getting 502/504 errors | P1 | 15-30 min |
| systemd_failures | Service won't start | P1 | 10-20 min |
| db_migrations | Migration failed | P1 | 20-40 min |
| docker_dev_loop | Docker build issues | P2 | 15-30 min |
| deploy_and_migrate | Deploying changes | P2 | 30-60 min |
| performance_profiling | App is slow | P3 | 30-60 min |
| security_incident | Security issue | P4 | 30-90 min |
| feature_delivery | Building features | P5 | Hours-Days |
| rollback_recovery | Need to rollback | P6 | 10-20 min |
| maintenance_mode | Scheduled downtime | P6 | Variable |

---

## Workflow Structure

All workflows follow this standard structure:

1. **Header** - Purpose, when to use, prerequisites
2. **Step 0: Context & Safety** - Scope resolution and execution level check
3. **Prerequisites** - What must be true before starting
4. **Steps** - Numbered steps with commands and expected output
5. **Failure Handling** - What to do if steps fail
6. **Completion Criteria** - When the workflow is done
6. **Validation** - How to verify success
7. **See Also** - Related workflows and checklists

---

## See Also

- [`../checklists/`](../checklists/) - Evidence collection checklists
- [`../flows/`](../flows/) - Decision trees
- [`../skills/`](../skills/) - Specialized knowledge
- [`../ROUTING_RULES.md`](../ROUTING_RULES.md) - How to choose a workflow
