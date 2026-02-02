# DevOps Examples - Docker & GitHub

## Purpose

This directory contains **complete, copy-paste ready examples** for Docker containerization and GitHub CI/CD workflows that integrate with the Agent OS.

All examples follow Agent OS gates, workflows, and rules to ensure production-ready quality.

## Quick Start

**New to Docker/GitHub?** Start here:

1. Read `docker_examples.md` for your stack
2. Read `github_examples.md` for CI/CD setup
3. Follow `docker_github_end_to_end.md` for complete workflow

**Already have Docker/GitHub?** Use these examples to:

- Validate your setup against Agent OS standards
- Add missing best practices
- Troubleshoot common issues

## Files in This Directory

| File | Purpose | Agent OS Integration |
|------|---------|---------------------|
| `docker_examples.md` | Complete Docker examples for 6+ stacks | Maps to `gate_global_docker.md` |
| `github_examples.md` | GitHub Actions CI/CD examples | Maps to `gate_global_ci_github.md` |
| `docker_github_end_to_end.md` | Full workflow from dev to release | Maps to all workflows |

## Stack Coverage

### Docker Examples

- ✅ Python (Flask/FastAPI)
- ✅ Node.js (Express)
- ✅ Next.js
- ✅ Flutter
- ✅ Java (Spring Boot)
- ✅ C++ (CMake)

Each includes:

- Production-ready Dockerfile
- docker-compose.yml for local dev
- Environment variable management
- Common troubleshooting

### GitHub Actions Examples

- ✅ CI workflows (lint, test, build)
- ✅ Release workflows (tag, publish, notes)
- ✅ Caching strategies
- ✅ Security scanning
- ✅ Multi-platform builds

## Agent OS Integration

All examples satisfy these Agent OS components:

### Gates

- `agent/05_gates/global/gate_global_docker.md` - Docker best practices
- `agent/05_gates/global/gate_global_ci_github.md` - CI/CD requirements
- `agent/05_gates/global/gate_global_release.md` - Release readiness

### Workflows

- `agent/04_workflows/02_repo_audit_and_baseline.md` - Initial setup
- `agent/04_workflows/07_testing_and_validation.md` - Testing in containers
- `agent/04_workflows/10_release_process.md` - Release automation

### Skills

- `agent/06_skills/devops/skill_docker_baseline.md` - Docker creation
- `agent/06_skills/devops/skill_compose_local_dev.md` - Compose setup
- `agent/06_skills/devops/skill_github_actions_ci.md` - CI pipeline
- `agent/06_skills/devops/skill_github_release_flow.md` - Release automation

### Rules

- `agent/11_rules/docker_rules.md` - Docker standards
- `agent/11_rules/github_rules.md` - GitHub standards

## Example Usage

### Scenario 1: Add Docker to Existing Project

```bash
# 1. Choose your stack from docker_examples.md
# 2. Copy the Dockerfile example
# 3. Copy the docker-compose.yml example
# 4. Create .env.example (no secrets!)
# 5. Test build
docker build -t myapp .

# 6. Test run
docker run -p 3000:3000 myapp

# 7. Validate against gate
# Check agent/05_gates/global/gate_global_docker.md
```

### Scenario 2: Add GitHub Actions CI

```bash
# 1. Choose your stack from github_examples.md
# 2. Create .github/workflows/ci.yml
# 3. Copy the workflow example
# 4. Commit and push
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow"
git push

# 5. Validate against gate
# Check agent/05_gates/global/gate_global_ci_github.md
```

### Scenario 3: Complete DevOps Setup

Follow `docker_github_end_to_end.md` for step-by-step guide.

## Troubleshooting

Each example file includes a troubleshooting section for common issues:

- Docker build failures
- Port conflicts
- Volume mount issues
- Dependency caching
- CI/CD failures

## Related Agent OS Files

### For Learning

- `agent/DOCKER_GITHUB_UPGRADE_SUMMARY.md` - Overview of Docker/GitHub support
- `agent/13_examples/example_docker_setup.md` - Agent OS example
- `agent/13_examples/example_github_actions_setup.md` - Agent OS example
- `agent/13_examples/example_devops_end_to_end.md` - Agent OS example

### For Reference

- `agent/07_templates/devops/` - All DevOps templates
- `plans/DevOps/` - DevOps planning documents

## Contributing

When adding new examples:

1. Follow existing format
2. Test all commands
3. Reference Agent OS gates/workflows
4. Include troubleshooting section
5. No secrets or placeholders

## Support

For issues or questions:

1. Check troubleshooting sections
2. Review Agent OS gates for requirements
3. Consult Agent OS skills for detailed procedures
4. Check Agent OS rules for standards

---

**Start Here**: `docker_examples.md` → `github_examples.md` → `docker_github_end_to_end.md`
