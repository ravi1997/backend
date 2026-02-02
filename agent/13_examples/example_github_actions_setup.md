# Example: GitHub Actions Setup

## Purpose

Demonstrates how to add GitHub Actions CI/CD following Agent OS standards.

## Agent OS Integration

- **Workflow**: `agent/04_workflows/06_feature_implementation_loop.md`
- **Skill**: `agent/06_skills/devops/skill_github_actions_ci.md`
- **Gate**: `agent/05_gates/global/gate_global_ci_github.md`
- **Rules**: `agent/11_rules/github_rules.md`

## Scenario

Adding CI/CD to a Node.js Express project.

## Step 1: Create CI Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage
      - if: matrix.node-version == 20
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json

  docker:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          tags: myapp:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Step 2: Create PR Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change

## Testing
- [ ] Tests pass
- [ ] Docker build succeeds

## Checklist
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] CI passes
```

## Step 3: Configure Branch Protection

In GitHub Settings → Branches:

1. Add rule for `main`
2. Require PR reviews (1 approval)
3. Require status checks:
   - lint
   - test
   - docker
4. Require branches up to date

## Step 4: Test Workflow

```bash
# Create feature branch
git checkout -b feature/test

# Make changes
echo "test" > test.txt
git add test.txt
git commit -m "test: add test file"

# Push
git push origin feature/test

# Open PR on GitHub
# Verify CI runs
```

## Step 5: Validate Against Gate

Check `agent/05_gates/global/gate_global_ci_github.md`:

- [x] CI workflow exists
- [x] Lint job runs
- [x] Test job runs
- [x] Docker build job runs
- [x] Caching configured (`cache: 'npm'`)
- [x] No secrets in workflow
- [x] Actions pinned to v4
- [x] Matrix build for multiple versions

## Complete Examples

See `prompts/examples_devops/github_examples.md` for more stacks:

- Python (FastAPI/Flask)
- Node.js (Express)
- Next.js
- Flutter
- Java (Spring Boot)
- C++ (CMake)
