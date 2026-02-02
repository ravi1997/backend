# Template: CODEOWNERS

## Purpose

Define code ownership for automatic review assignment and approval requirements.

## Format

```
# CODEOWNERS file
# Each line is a file pattern followed by one or more owners.
# Owners can be @username, @org/team-name, or email addresses.

# Default owners for everything in the repo
* @org/core-team

# Documentation
*.md @org/docs-team
/docs/ @org/docs-team

# Frontend
/src/components/ @org/frontend-team
/src/pages/ @org/frontend-team
/public/ @org/frontend-team
*.tsx @org/frontend-team
*.jsx @org/frontend-team

# Backend
/src/api/ @org/backend-team
/src/services/ @org/backend-team
/src/models/ @org/backend-team

# Database
/migrations/ @org/backend-team @org/dba-team
/prisma/ @org/backend-team @org/dba-team
schema.sql @org/dba-team

# DevOps and Infrastructure
Dockerfile @org/devops-team
docker-compose*.yml @org/devops-team
.github/workflows/ @org/devops-team
/infrastructure/ @org/devops-team
/terraform/ @org/devops-team
/k8s/ @org/devops-team

# CI/CD
.github/workflows/*.yml @org/devops-team
.gitlab-ci.yml @org/devops-team

# Security
/src/auth/ @org/security-team
/src/middleware/auth* @org/security-team

# Configuration
.env.example @org/devops-team
config/ @org/backend-team @org/devops-team

# Dependencies
package.json @org/core-team
package-lock.json @org/core-team
requirements.txt @org/core-team
Gemfile @org/core-team
go.mod @org/core-team

# Testing
/tests/ @org/qa-team
*.test.* @org/qa-team
*.spec.* @org/qa-team
jest.config.js @org/qa-team
pytest.ini @org/qa-team
```

## Example: Small Team

```
# Default owner
* @username

# Frontend
/frontend/ @frontend-dev

# Backend
/backend/ @backend-dev

# DevOps
Dockerfile @devops-lead
.github/workflows/ @devops-lead
```

## Example: Open Source Project

```
# Core maintainers own everything by default
* @org/maintainers

# Specific areas
/docs/ @org/docs-writers @username
/examples/ @org/community
/.github/ @org/maintainers

# Critical files require multiple approvals
package.json @org/maintainers @org/security
Dockerfile @org/maintainers @org/devops
```

## Example: Monorepo

```
# Default
* @org/core-team

# Service A
/services/service-a/ @org/team-a
/libs/shared-a/ @org/team-a

# Service B
/services/service-b/ @org/team-b
/libs/shared-b/ @org/team-b

# Shared infrastructure
/libs/common/ @org/core-team
/infrastructure/ @org/devops-team

# CI/CD affects everyone
.github/workflows/ @org/core-team @org/devops-team
```

## Best Practices

### Pattern Specificity

- More specific patterns override less specific ones
- Last matching pattern takes precedence
- Use `*` for default owners

### Team vs Individual

```
# Prefer teams over individuals
/src/ @org/backend-team  # Good
/src/ @john @jane @bob   # Avoid - hard to maintain
```

### Critical Files

```
# Require multiple approvals for critical files
package.json @org/core-team @org/security-team
Dockerfile @org/devops-team @org/security-team
```

### Documentation

```
# Always include comments explaining ownership
# Frontend team owns all React components
/src/components/ @org/frontend-team
```

## Validation

To test CODEOWNERS file:

1. Create a PR that modifies files
2. Check if correct reviewers are auto-assigned
3. Verify required approvals match expectations

GitHub provides a CODEOWNERS validator in repository settings.

## Notes

- CODEOWNERS must be in repository root, `.github/`, or `docs/` directory
- Patterns follow `.gitignore` syntax
- Teams must have write access to the repository
- Use with branch protection rules for enforcement
- Keep file updated as team structure changes

## Related Files

- `agent/11_rules/github_rules.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
