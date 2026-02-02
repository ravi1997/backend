# Template: GitHub Actions CI Workflow

## Purpose

This template provides a comprehensive CI pipeline for GitHub Actions that includes linting, testing, building, and Docker image creation.

## Parameters

- `{{WORKFLOW_NAME}}`: Name of the workflow (e.g., `CI`, `Continuous Integration`)
- `{{LANGUAGE}}`: Primary language (e.g., `node`, `python`, `java`)
- `{{LANGUAGE_VERSION}}`: Language version or matrix (e.g., `20`, `['18', '20', '22']`, `3.11`)
- `{{PACKAGE_MANAGER}}`: Package manager (e.g., `npm`, `pip`, `maven`)
- `{{LINT_CMD}}`: Linting command (e.g., `npm run lint`, `ruff check .`)
- `{{TEST_CMD}}`: Test command (e.g., `npm test`, `pytest`)
- `{{BUILD_CMD}}`: Build command (e.g., `npm run build`, `mvn package`)

## Template

```yaml
name: {{WORKFLOW_NAME}}

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup {{LANGUAGE}}
        uses: {{SETUP_ACTION}}
        with:
          {{LANGUAGE}}-version: '{{LANGUAGE_VERSION}}'
          cache: '{{PACKAGE_MANAGER}}'

      - name: Install dependencies
        run: {{INSTALL_CMD}}

      - name: Run linter
        run: {{LINT_CMD}}

  test:
    name: Test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        {{LANGUAGE}}-version: {{VERSION_MATRIX}}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup {{LANGUAGE}} ${{ matrix.{{LANGUAGE}}-version }}
        uses: {{SETUP_ACTION}}
        with:
          {{LANGUAGE}}-version: ${{ matrix.{{LANGUAGE}}-version }}
          cache: '{{PACKAGE_MANAGER}}'

      - name: Install dependencies
        run: {{INSTALL_CMD}}

      - name: Run tests
        run: {{TEST_CMD}}

      - name: Upload coverage
        if: matrix.{{LANGUAGE}}-version == '{{PRIMARY_VERSION}}'
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: false

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup {{LANGUAGE}}
        uses: {{SETUP_ACTION}}
        with:
          {{LANGUAGE}}-version: '{{LANGUAGE_VERSION}}'
          cache: '{{PACKAGE_MANAGER}}'

      - name: Install dependencies
        run: {{INSTALL_CMD}}

      - name: Build application
        run: {{BUILD_CMD}}

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: {{BUILD_OUTPUT_PATH}}
          retention-days: 7

  docker:
    name: Docker Build
    runs-on: ubuntu-latest
    needs: [lint, test]
    if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.full_name == github.repository
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          tags: ${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          load: true

      - name: Test Docker image
        run: |
          docker run --rm -d --name test-container -p {{APP_PORT}}:{{APP_PORT}} ${{ github.repository }}:${{ github.sha }}
          sleep 5
          curl --fail http://localhost:{{APP_PORT}}/health || exit 1
          docker stop test-container
```

## Example: Node.js/Next.js CI

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint

      - name: Check formatting
        run: npm run format:check

  test:
    name: Test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

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
        if: matrix.node-version == 20
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
          fail_ci_if_error: false

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

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
          name: next-build
          path: .next/
          retention-days: 7

  docker:
    name: Docker Build
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          tags: ${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Run npm audit
        run: npm audit --audit-level=moderate
        continue-on-error: true
```

## Example: Python FastAPI CI

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install linting tools
        run: |
          pip install ruff black isort

      - name: Run ruff
        run: ruff check .

      - name: Check formatting with black
        run: black --check .

      - name: Check import sorting
        run: isort --check-only .

  test:
    name: Test
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
          pip install pytest pytest-cov pytest-asyncio

      - name: Run tests
        run: pytest --cov=. --cov-report=xml --cov-report=html

      - name: Upload coverage
        if: matrix.python-version == '3.11'
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  security:
    name: Security Scan
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
    name: Docker Build
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

## Notes

- Use `concurrency` to cancel outdated workflow runs
- Cache dependencies to speed up builds
- Use matrix strategy to test multiple versions
- Upload coverage reports for visibility
- Include security scanning in CI
- Test Docker images as part of CI
- Use `needs` to define job dependencies
- Set appropriate timeouts for jobs

## Related Files

- `agent/11_rules/github_rules.md`
- `agent/06_skills/devops/skill_github_actions_ci.md`
- `agent/05_gates/global/gate_global_ci_github.md`
