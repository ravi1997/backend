# Skill: GitHub Actions CI Pipeline

## Purpose

Create a comprehensive CI pipeline using GitHub Actions that runs linting, testing, and building on every push and pull request.

## Inputs

- **Stack Type**: From `agent/09_state/STACK_STATE.md`
- **Test Command**: How to run tests (e.g., `npm test`, `pytest`)
- **Lint Command**: How to run linter (e.g., `eslint`, `ruff`)
- **Build Command**: How to build (e.g., `npm run build`, `docker build`)

## Outputs

- `.github/workflows/ci.yml`
- Updated `README.md` with CI badge and status
- Optional: `.github/workflows/pr-checks.yml` for additional PR validation

## Procedure

### Step 1: Create Workflow Directory

```bash
mkdir -p .github/workflows
```

### Step 2: Define CI Workflow Structure

Create `.github/workflows/ci.yml` with:

1. **Trigger Configuration**:
   - Run on push to main/master branch
   - Run on all pull requests
   - Allow manual dispatch

2. **Job: Lint**:
   - Checkout code
   - Setup language runtime (Node, Python, etc.)
   - Cache dependencies
   - Install dependencies
   - Run linter
   - Report results

3. **Job: Test**:
   - Checkout code
   - Setup runtime (with version matrix if applicable)
   - Cache dependencies
   - Install dependencies
   - Run tests with coverage
   - Upload coverage reports
   - Report results

4. **Job: Build**:
   - Checkout code
   - Setup runtime
   - Cache dependencies
   - Install dependencies
   - Run build command
   - Upload build artifacts (optional)

5. **Job: Docker** (if Dockerfile exists):
   - Checkout code
   - Setup Docker Buildx
   - Build Docker image
   - Optionally scan image for vulnerabilities

### Step 3: Implement Caching

Based on stack:

- **Node.js**: Cache `~/.npm` or `node_modules`
- **Python**: Cache `~/.cache/pip`
- **Java**: Cache `~/.m2/repository`
- **Rust**: Cache `~/.cargo` and `target/`

Use `actions/cache@v3` with appropriate cache keys.

### Step 4: Add Security Scanning

Include dependency vulnerability scanning:

- **Node.js**: `npm audit`
- **Python**: `pip-audit` or `safety check`
- **Java**: OWASP dependency check
- **Docker**: `docker scan` or `trivy`

### Step 5: Configure Required Status Checks

Document in `README.md` or `CONTRIBUTING.md`:

- Which checks must pass before merge
- How to run checks locally
- How to interpret failures

### Step 6: Add CI Badge

Add to `README.md`:

```markdown
[![CI](https://github.com/<owner>/<repo>/workflows/CI/badge.svg)](https://github.com/<owner>/<repo>/actions)
```

## Failure Modes

### Workflow Syntax Error

- **Cause**: Invalid YAML or unknown action
- **Fix**: Use `actionlint` to validate, check action versions

### Jobs Timeout

- **Cause**: Tests hang, dependencies take too long
- **Fix**: Add timeout-minutes, optimize dependency installation

### Flaky Tests

- **Cause**: Non-deterministic tests, race conditions
- **Fix**: Identify and fix flaky tests, add retries as temporary measure

### Cache Not Working

- **Cause**: Incorrect cache key or path
- **Fix**: Verify cache paths, use hash of lock files in key

## Examples

### Node.js/Next.js CI Pipeline

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linter
        run: npm run lint

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        if: matrix.node-version == 20

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build application
        run: npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: .next/

  docker:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          tags: myapp:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Python FastAPI CI Pipeline

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install ruff
          pip install -r requirements.txt
      
      - name: Run ruff
        run: ruff check .

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        if: matrix.python-version == '3.11'

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install pip-audit
        run: pip install pip-audit
      
      - name: Run security scan
        run: pip-audit -r requirements.txt

  docker:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t myapp:test .
      
      - name: Test Docker image
        run: |
          docker run -d --name test-container -p 8000:8000 myapp:test
          sleep 5
          curl --fail http://localhost:8000/health || exit 1
          docker stop test-container
```

## Related Files

- `agent/05_gates/global/gate_global_ci_github.md`
- `agent/11_rules/github_rules.md`
- `agent/07_templates/devops/github_actions_ci.template.yml.md`
