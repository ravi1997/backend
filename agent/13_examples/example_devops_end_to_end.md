# Example: DevOps End-to-End

## Purpose

Complete workflow from adding Docker to releasing with GitHub Actions.

## Agent OS Integration

- **Workflows**: All in `agent/04_workflows/`
- **Gates**: All in `agent/05_gates/global/`
- **Skills**: All DevOps skills in `agent/06_skills/devops/`

## Scenario

Node.js Express API - complete DevOps setup.

## Phase 1: Add Docker

### Create Files

```bash
# Dockerfile
cat > Dockerfile << 'EOF'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

FROM node:20-alpine
WORKDIR /app
COPY --from=builder --chown=node:node /app /app
EXPOSE 3000
HEALTHCHECK CMD wget --spider http://localhost:3000/health || exit 1
USER node
CMD ["node", "src/index.js"]
EOF

# docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
volumes: {}
EOF

# .dockerignore
cat > .dockerignore << 'EOF'
node_modules
.git
.env
tests
EOF
```

### Test

```bash
docker build -t myapi .
docker compose up
curl http://localhost:3000/health
```

## Phase 2: Add GitHub Actions

### Create CI Workflow

```bash
mkdir -p .github/workflows

cat > .github/workflows/ci.yml << 'EOF'
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
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test

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
          cache-from: type=gha
          cache-to: type=gha,mode=max
EOF
```

### Commit and Push

```bash
git add .
git commit -m "ci: add Docker and GitHub Actions"
git push origin main
```

## Phase 3: Feature Development

### Create Feature Branch

```bash
git checkout -b feature/add-users
```

### Implement Feature

```javascript
// src/routes/users.js
router.get('/users', async (req, res) => {
  const users = await User.findAll();
  res.json(users);
});
```

### Test Locally

```bash
npm test
docker compose up --build
curl http://localhost:3000/users
```

### Open PR

```bash
git add src/routes/users.js
git commit -m "feat: add users endpoint"
git push origin feature/add-users
# Open PR on GitHub
# Wait for CI to pass
# Get approval
# Merge
```

## Phase 4: Release

### Create Release Workflow

```bash
cat > .github/workflows/release.yml << 'EOF'
name: Release
on:
  push:
    tags:
      - 'v*.*.*'

permissions:
  contents: write
  packages: write

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ steps.version.outputs.VERSION }}
            ghcr.io/${{ github.repository }}:latest

  release:
    runs-on: ubuntu-latest
    needs: [docker]
    steps:
      - uses: actions/checkout@v4
      - uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
EOF
```

### Create Release

```bash
# Update version
npm version minor  # Updates package.json

# Commit
git add package.json
git commit -m "chore: bump version to v1.1.0"
git push origin main

# Tag
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# GitHub Actions automatically:
# - Builds Docker image
# - Pushes to GHCR
# - Creates GitHub Release
```

## Validation Checklist

### Docker Gate

- [x] Build succeeds
- [x] Multi-stage build
- [x] Non-root user
- [x] No secrets
- [x] Healthcheck

### CI Gate

- [x] Lint runs
- [x] Tests run
- [x] Docker builds
- [x] Caching works

### Release Gate

- [x] Version follows SemVer
- [x] Docker image published
- [x] GitHub Release created

## Complete Guide

See `prompts/examples_devops/docker_github_end_to_end.md` for detailed step-by-step guide with troubleshooting.
