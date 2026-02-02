# Gate: Global GitHub CI/CD

**Type**: Global DevOps Gate  
**Purpose**: Ensure GitHub usage meets collaboration, quality, and automation standards

---

## Overview

This gate validates the GitHub repository configuration, including Actions CI/CD, issue management, and security settings.

---

## Checks

### 1. Repository Structure

- [ ] `.github/` directory exists
- [ ] `.github/workflows/` contains CI definition
- [ ] `.github/ISSUE_TEMPLATE/` configured
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` exists
- [ ] `.gitignore` exists and is effective
- [ ] `README.md` is comprehensive and up-to-date
- [ ] `LICENSE` file present

### 2. CI/CD Workflows (GitHub Actions)

- [ ] CI pipeline configured (triggers on push/PR)
- [ ] Build step runs successfully
- [ ] Test step runs successfully
- [ ] Lint/Style check runs and enforces standards
- [ ] Security scan step (e.g., CodeQL, Trivy) present
- [ ] Secrets used safely (`${{ secrets.NAME }}`)
- [ ] Matrix builds used (if testing multiple versions)
- [ ] Caching configured (npm, pip, maven, etc.)

**Example Workflow**:

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
```

### 3. Pull Request Standards

- [ ] Template enforces description of changes
- [ ] Template requires linking to issues
- [ ] Checklist included in PR template
- [ ] Branch protection rules active (require CI pass)
- [ ] Code owner review required (optional but recommended)

### 4. Issue Management

- [ ] Templates for Bugs, Features, Tasks
- [ ] Labels defined (bug, feature, documentation, etc.)
- [ ] Stale bot configured (optional)

### 5. Security & Governance

- [ ] DEPENDABOT configured (`.github/dependabot.yml`)
- [ ] Branch protection on `main`/`master`
  - Require status checks to pass
  - Require pull request reviews
  - Dismiss stale approving reviews
- [ ] No secrets committed to repo
- [ ] `CODEOWNERS` file present (if team based)

---

## Pass Criteria

✅ **PASS** if:

- CI pipeline runs and passes
- All templates exist
- .gitignore is correct
- No secrets in history
- Branch protection is active (if possible to check)

❌ **FAIL** if:

- CI fails
- Missing CI configuration
- Committing generated files (node_modules, build artifacts)
- Hardcoded secrets found

---

## Configuration Files

### `.gitignore` (Standard)

```gitignore
# Dependencies
node_modules/
venv/
target/

# Build
dist/
build/

# Env
.env
.DS_Store
```

### `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## GitHub Checklist

```markdown
## GitHub Readiness Checklist

### Structure
- [ ] .gitignore present and validated
- [ ] README.md current
- [ ] LICENSE present

### Automation (Actions)
- [ ] CI workflow created
- [ ] Build job succeeds
- [ ] Test job succeeds
- [ ] Lint job succeeds
- [ ] Security scan job success

### Collaboration
- [ ] PR template exists
- [ ] Issue templates exist
- [ ] CODEOWNERS exists (optional)

### Security
- [ ] Dependabot configured
- [ ] Branch protection rules Set
- [ ] Secrets audit performed
```

---

## Related Files

- `agent/13_examples/example_github_actions_setup.md`
- `agent/05_gates/global/gate_global_security.md`
- `agent/06_skills/skill_github_ci_gen.md`
