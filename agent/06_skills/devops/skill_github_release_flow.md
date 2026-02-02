# Skill: GitHub Release Flow

## Purpose

Automate the release process using GitHub Actions, including version tagging, changelog generation, artifact building, and GitHub Release creation.

## Inputs

- **Version Number**: Semantic version (e.g., `v1.2.3`)
- **Release Branch**: Typically `main` or `master`
- **Changelog**: From `CHANGELOG.md` or auto-generated
- **Build Artifacts**: Compiled binaries, Docker images, or distribution packages

## Outputs

- `.github/workflows/release.yml`
- Git tag (e.g., `v1.2.3`)
- GitHub Release with notes and artifacts
- Optional: Published Docker images to registry

## Procedure

### Step 1: Create Release Workflow

Create `.github/workflows/release.yml` that triggers on:

- Tag push matching `v*.*.*` pattern
- Manual workflow dispatch with version input

### Step 2: Define Release Jobs

1. **Validate**:
   - Ensure tag follows semantic versioning
   - Verify all tests pass
   - Check changelog is updated

2. **Build**:
   - Build application for all target platforms
   - Run final tests on built artifacts
   - Generate checksums for artifacts

3. **Docker** (if applicable):
   - Build production Docker image
   - Tag with version number and `latest`
   - Push to container registry (GHCR, Docker Hub)

4. **Create Release**:
   - Extract release notes from CHANGELOG.md
   - Create GitHub Release
   - Upload build artifacts
   - Publish release

### Step 3: Configure Secrets

Ensure GitHub secrets are configured:

- `GITHUB_TOKEN`: Automatically provided
- `DOCKER_USERNAME`: For Docker Hub (if used)
- `DOCKER_PASSWORD`: For Docker Hub (if used)
- Any other deployment credentials

### Step 4: Version Bumping Strategy

Document in `CONTRIBUTING.md`:

1. Update version in package files (`package.json`, `pyproject.toml`, etc.)
2. Update `CHANGELOG.md` with release notes
3. Commit changes: `git commit -m "chore: bump version to v1.2.3"`
4. Create tag: `git tag -a v1.2.3 -m "Release v1.2.3"`
5. Push: `git push origin main --tags`

### Step 5: Automate Changelog

Options:

- Manual: Update `CHANGELOG.md` before release
- Semi-auto: Use conventional commits + `standard-version` or `semantic-release`
- Full-auto: Generate from commit messages in workflow

### Step 6: Document Release Process

Add to `README.md` or `CONTRIBUTING.md`:

```markdown
## Releases

This project follows [Semantic Versioning](https://semver.org/).

To create a release:

1. Update version in package files
2. Update CHANGELOG.md
3. Commit and push to main
4. Create and push tag: `git tag v1.2.3 && git push --tags`
5. GitHub Actions will automatically create the release
```

## Failure Modes

### Release Workflow Fails

- **Cause**: Build errors, missing secrets, network issues
- **Fix**: Check workflow logs, verify secrets, retry failed jobs

### Tag Already Exists

- **Cause**: Attempting to create duplicate tag
- **Fix**: Delete old tag or increment version number

### Artifacts Not Uploaded

- **Cause**: Build path incorrect, artifact size too large
- **Fix**: Verify build output paths, check GitHub limits

### Docker Push Fails

- **Cause**: Authentication failure, registry unavailable
- **Fix**: Verify credentials, check registry status

## Examples

### Node.js Release Workflow

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (e.g., v1.2.3)'
        required: true

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate version
        run: |
          VERSION=${{ github.ref_name }}
          if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "Invalid version format: $VERSION"
            exit 1
          fi

  build:
    runs-on: ubuntu-latest
    needs: validate
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
      
      - name: Package
        run: |
          tar -czf dist.tar.gz dist/
          sha256sum dist.tar.gz > dist.tar.gz.sha256
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: |
            dist.tar.gz
            dist.tar.gz.sha256

  docker:
    runs-on: ubuntu-latest
    needs: validate
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
        run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT
      
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
    runs-on: ubuntu-latest
    needs: [build, docker]
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-artifacts
      
      - name: Extract changelog
        id: changelog
        run: |
          VERSION=${GITHUB_REF#refs/tags/}
          sed -n "/## \[${VERSION#v}\]/,/## \[/p" CHANGELOG.md | sed '$d' > release_notes.md
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: release_notes.md
          files: |
            dist.tar.gz
            dist.tar.gz.sha256
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Python Package Release

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install build tools
        run: pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Check package
        run: twine check dist/*
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: python-package
          path: dist/

  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          docker build -t ghcr.io/${{ github.repository }}:${VERSION} .
          docker tag ghcr.io/${{ github.repository }}:${VERSION} ghcr.io/${{ github.repository }}:latest
          docker push ghcr.io/${{ github.repository }}:${VERSION}
          docker push ghcr.io/${{ github.repository }}:latest

  release:
    runs-on: ubuntu-latest
    needs: [build, docker]
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: python-package
          path: dist/
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
          files: dist/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Related Files

- `agent/04_workflows/10_release_process.md`
- `agent/05_gates/global/gate_global_release.md`
- `agent/07_templates/devops/github_actions_release.template.yml.md`
