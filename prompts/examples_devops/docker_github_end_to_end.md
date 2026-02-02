# Docker + GitHub End-to-End DevOps Workflow

## Purpose

Complete, step-by-step guide from adding Docker to releasing with GitHub Actions. This example integrates all Agent OS workflows and gates.

## Agent OS Integration

**Satisfies Workflows:**

- `agent/04_workflows/02_repo_audit_and_baseline.md` ✅
- `agent/04_workflows/06_feature_implementation_loop.md` ✅
- `agent/04_workflows/07_testing_and_validation.md` ✅
- `agent/04_workflows/10_release_process.md` ✅

**Satisfies Gates:**

- `agent/05_gates/global/gate_global_docker.md` ✅
- `agent/05_gates/global/gate_global_ci_github.md` ✅
- `agent/05_gates/global/gate_global_release.md` ✅

---

## Scenario: Node.js Express API

We'll add Docker and GitHub CI/CD to an existing Node.js Express API.

### Starting Point

```
my-api/
├── src/
│   ├── index.js
│   ├── routes/
│   └── models/
├── tests/
├── package.json
├── package-lock.json
└── README.md
```

---

## Phase 1: Baseline Audit

**Maps to**: `agent/04_workflows/02_repo_audit_and_baseline.md`

### Step 1: Check Current State

```bash
# Test build
npm install
npm run build  # or npm start

# Run tests
npm test

# Check for linter
npm run lint
```

### Step 2: Document Baseline

Create `plans/DevOps/baseline_audit.md`:

```markdown
# Baseline Audit - 2026-01-19

## Current State
- ✅ Build: Works
- ✅ Tests: 45 passing
- ✅ Lint: ESLint configured
- ❌ Docker: Not present
- ❌ CI/CD: Not present

## Action Items
1. Add Docker support
2. Add GitHub Actions CI
3. Add release workflow
```

---

## Phase 2: Add Docker Support

**Maps to**: `agent/06_skills/devops/skill_docker_baseline.md`

### Step 3: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

FROM node:20-alpine

WORKDIR /app

COPY --from=builder --chown=node:node /app /app

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

USER node

CMD ["node", "src/index.js"]
```

### Step 4: Create .dockerignore

Create `.dockerignore`:

```dockerignore
node_modules
npm-debug.log
.env
.git
.gitignore
README.md
tests
coverage
.nyc_output
dist
build
```

### Step 5: Create docker-compose.yml

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "${API_PORT:-3000}:3000"
    volumes:
      - ./src:/app/src:ro
    environment:
      - NODE_ENV=${NODE_ENV:-development}
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=${DB_NAME:-myapi}
      - DB_USER=${DB_USER:-postgres}
      - DB_PASSWORD=${DB_PASSWORD:-postgres}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - api-network

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=${DB_NAME:-myapi}
      - POSTGRES_USER=${DB_USER:-postgres}
      - POSTGRES_PASSWORD=${DB_PASSWORD:-postgres}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - api-network

volumes:
  postgres-data:

networks:
  api-network:
```

### Step 6: Create .env.example

Create `.env.example`:

```env
# Application
API_PORT=3000
NODE_ENV=development

# Database
DB_NAME=myapi
DB_USER=postgres
DB_PASSWORD=changeme_in_production

# NEVER commit .env file with real secrets!
```

### Step 7: Test Docker Build

```bash
# Build image
docker build -t my-api .

# Check image size
docker images my-api

# Run standalone
docker run -p 3000:3000 -e DB_HOST=localhost my-api

# Test with compose
cp .env.example .env
docker compose up

# In another terminal, test API
curl http://localhost:3000/health

# View logs
docker compose logs -f api

# Stop
docker compose down
```

### Step 8: Validate Against Docker Gate

Check `agent/05_gates/global/gate_global_docker.md`:

- [x] Build succeeds
- [x] Base image pinned (`node:20-alpine`)
- [x] Multi-stage build
- [x] Non-root user (`node`)
- [x] No secrets in Dockerfile
- [x] .dockerignore present
- [x] Environment variables used
- [x] Healthcheck defined
- [x] Port exposed

### Step 9: Update README

Add to `README.md`:

```markdown
## Docker

### Build and Run

```bash
# Build image
docker build -t my-api .

# Run with Docker Compose
cp .env.example .env
docker compose up
```

### Development

The API runs on port 3000. Source code is mounted for hot-reload.

### Production

Set environment variables in `.env` (never commit this file).

```

### Step 10: Commit Docker Changes

```bash
git add Dockerfile docker-compose.yml .dockerignore .env.example
git add README.md
git commit -m "feat: add Docker support with multi-stage build"
git push origin main
```

---

## Phase 3: Add GitHub Actions CI

**Maps to**: `agent/06_skills/devops/skill_github_actions_ci.md`

### Step 11: Create CI Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
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

      - name: Run ESLint
        run: npm run lint

  test:
    name: Test
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
        if: matrix.node-version == 20
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
          fail_ci_if_error: false

  security:
    name: Security Scan
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

      - name: Run npm audit
        run: npm audit --audit-level=moderate
        continue-on-error: true

  docker:
    name: Docker Build
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
          tags: ${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          load: true

      - name: Test Docker image
        run: |
          docker run -d --name test-api -p 3000:3000 -e DB_HOST=localhost ${{ github.repository }}:${{ github.sha }}
          sleep 5
          curl --fail http://localhost:3000/health || exit 1
          docker stop test-api
```

### Step 12: Create PR Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Docker build succeeds
- [ ] Manual testing completed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CI passes
- [ ] No secrets committed
```

### Step 13: Commit CI Changes

```bash
git add .github/
git commit -m "ci: add GitHub Actions workflow"
git push origin main
```

### Step 14: Verify CI Runs

1. Go to GitHub → Actions tab
2. Verify workflow runs successfully
3. Check all jobs pass (lint, test, security, docker)

### Step 15: Validate Against CI Gate

Check `agent/05_gates/global/gate_global_ci_github.md`:

- [x] CI workflow exists
- [x] Lint job runs
- [x] Test job runs
- [x] Build/Docker job runs
- [x] Caching configured
- [x] No secrets in workflow
- [x] Security scan included

---

## Phase 4: Feature Development with Docker/CI

**Maps to**: `agent/04_workflows/06_feature_implementation_loop.md`

### Step 16: Create Feature Branch

```bash
git checkout -b feature/add-user-endpoint
```

### Step 17: Implement Feature

Edit `src/routes/users.js`:

```javascript
router.get('/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);
});
```

### Step 18: Add Tests

Edit `tests/users.test.js`:

```javascript
describe('GET /users/:id', () => {
  it('should return user by id', async () => {
    const response = await request(app).get('/users/1');
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('id', 1);
  });
});
```

### Step 19: Test Locally

```bash
# Run tests
npm test

# Test in Docker
docker compose up --build
curl http://localhost:3000/users/1
```

### Step 20: Commit and Push

```bash
git add src/routes/users.js tests/users.test.js
git commit -m "feat: add user endpoint"
git push origin feature/add-user-endpoint
```

### Step 21: Open Pull Request

1. Go to GitHub
2. Click "Compare & pull request"
3. Fill out PR template
4. Create pull request
5. Wait for CI to pass
6. Request review

### Step 22: Address Review Feedback

```bash
# Make changes
git add .
git commit -m "fix: address review feedback"
git push origin feature/add-user-endpoint
```

### Step 23: Merge PR

Once approved and CI passes:

1. Click "Squash and merge"
2. Confirm merge
3. Delete branch

---

## Phase 5: Release Process

**Maps to**: `agent/04_workflows/10_release_process.md`

### Step 24: Create Release Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

permissions:
  contents: write
  packages: write

jobs:
  build:
    name: Build Release
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

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build || echo "No build step"

  docker:
    name: Publish Docker Image
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract version
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/}
          echo "VERSION=${VERSION}" >> $GITHUB_OUTPUT

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ steps.version.outputs.VERSION }}
            ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  release:
    name: Create GitHub Release
    runs-on: ubuntu-latest
    needs: [build, docker]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate release notes
        id: notes
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "## Changes" > release_notes.md
          git log $(git describe --tags --abbrev=0 HEAD^)..HEAD --pretty=format:"- %s" >> release_notes.md

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: release_notes.md
          draft: false
          prerelease: false
```

### Step 25: Update Version

Edit `package.json`:

```json
{
  "name": "my-api",
  "version": "1.1.0",
  ...
}
```

### Step 26: Update CHANGELOG

Create/update `CHANGELOG.md`:

```markdown
# Changelog

## [1.1.0] - 2026-01-19

### Added
- User endpoint to fetch user by ID
- Docker support with multi-stage build
- GitHub Actions CI/CD pipeline

### Changed
- Improved error handling

### Fixed
- Database connection timeout issue
```

### Step 27: Create Release

```bash
# Commit version bump
git add package.json CHANGELOG.md
git commit -m "chore: bump version to v1.1.0"
git push origin main

# Create tag
git tag -a v1.1.0 -m "Release v1.1.0"

# Push tag
git push origin v1.1.0
```

### Step 28: Verify Release

1. Go to GitHub → Actions
2. Verify release workflow runs
3. Check Docker image published to GHCR
4. Verify GitHub Release created
5. Download and test release artifacts

### Step 29: Validate Against Release Gate

Check `agent/05_gates/global/gate_global_release.md`:

- [x] Version follows semantic versioning
- [x] CHANGELOG updated
- [x] All tests pass
- [x] Docker image built and tagged
- [x] GitHub Release created
- [x] Release notes included

---

## Phase 6: Production Deployment

### Step 30: Pull and Deploy

```bash
# Pull latest image
docker pull ghcr.io/username/my-api:v1.1.0

# Run in production
docker run -d \
  --name my-api \
  -p 3000:3000 \
  -e NODE_ENV=production \
  -e DB_HOST=prod-db.example.com \
  -e DB_USER=prod_user \
  -e DB_PASSWORD=$DB_PASSWORD \
  --restart unless-stopped \
  ghcr.io/username/my-api:v1.1.0

# Check health
curl http://localhost:3000/health

# View logs
docker logs -f my-api
```

---

## Complete File Structure

```
my-api/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── release.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── src/
│   ├── index.js
│   ├── routes/
│   │   └── users.js
│   └── models/
├── tests/
│   └── users.test.js
├── plans/
│   └── DevOps/
│       └── baseline_audit.md
├── .dockerignore
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── Dockerfile
├── docker-compose.yml
├── package.json
├── package-lock.json
└── README.md
```

---

## Go/No-Go Checklist

Before each release, verify:

### Code Quality

- [ ] All tests pass locally
- [ ] Linter passes
- [ ] Code reviewed and approved
- [ ] Documentation updated

### Docker

- [ ] `docker build .` succeeds
- [ ] `docker compose up` works
- [ ] No secrets in image
- [ ] Image size reasonable
- [ ] Healthcheck works

### CI/CD

- [ ] All CI jobs pass
- [ ] Security scan clean
- [ ] No new vulnerabilities
- [ ] Coverage maintained/improved

### Release

- [ ] Version bumped correctly
- [ ] CHANGELOG updated
- [ ] Tag created
- [ ] Release notes complete
- [ ] Docker image published
- [ ] GitHub Release created

### Deployment

- [ ] Smoke tests pass
- [ ] Monitoring configured
- [ ] Rollback plan ready
- [ ] Team notified

---

## Troubleshooting

### Docker Build Fails in CI

```yaml
# Add BuildKit
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
```

### Tests Fail in Docker

```bash
# Run tests in container
docker compose exec api npm test

# Check environment variables
docker compose exec api env
```

### Release Workflow Not Triggering

```bash
# Ensure tag format is correct
git tag -a v1.0.0 -m "Release v1.0.0"

# Push tags
git push --tags
```

### Docker Image Too Large

```dockerfile
# Use multi-stage build
FROM node:20-alpine AS builder
# ... build steps ...

FROM node:20-alpine
# Copy only necessary files
```

---

## Summary

This end-to-end workflow demonstrates:

1. ✅ Baseline audit and documentation
2. ✅ Docker containerization with best practices
3. ✅ GitHub Actions CI with comprehensive checks
4. ✅ Feature development with Docker validation
5. ✅ PR workflow with automated testing
6. ✅ Release automation with Docker publishing
7. ✅ Production deployment

All steps satisfy Agent OS gates, workflows, and rules.

---

**Related Files:**

- `prompts/examples_devops/docker_examples.md` - Detailed Docker examples
- `prompts/examples_devops/github_examples.md` - Detailed GitHub examples
- `agent/DOCKER_GITHUB_UPGRADE_SUMMARY.md` - Overview of Docker/GitHub support
