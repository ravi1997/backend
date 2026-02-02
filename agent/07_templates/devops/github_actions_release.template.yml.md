# Template: GitHub Actions Release Workflow

## Purpose

This template provides an automated release workflow that creates GitHub releases, builds artifacts, and publishes Docker images.

## Template

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
        type: string

permissions:
  contents: write
  packages: write

jobs:
  validate:
    name: Validate Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Validate version format
        run: |
          VERSION=${{ github.ref_name }}
          if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "Invalid version format: $VERSION"
            echo "Expected format: v1.2.3"
            exit 1
          fi

  build:
    name: Build Artifacts
    runs-on: ubuntu-latest
    needs: validate
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup environment
        uses: {{SETUP_ACTION}}
        with:
          {{LANGUAGE}}-version: '{{VERSION}}'
          cache: '{{PACKAGE_MANAGER}}'

      - name: Install dependencies
        run: {{INSTALL_CMD}}

      - name: Run tests
        run: {{TEST_CMD}}

      - name: Build application
        run: {{BUILD_CMD}}

      - name: Package artifacts
        run: |
          tar -czf dist.tar.gz {{BUILD_OUTPUT}}
          sha256sum dist.tar.gz > dist.tar.gz.sha256

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: release-artifacts
          path: |
            dist.tar.gz
            dist.tar.gz.sha256

  docker:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    needs: validate
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

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
          echo "VERSION_NO_V=${VERSION#v}" >> $GITHUB_OUTPUT

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ steps.version.outputs.VERSION }}
            ghcr.io/${{ github.repository }}:${{ steps.version.outputs.VERSION_NO_V }}
            ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
          labels: |
            org.opencontainers.image.source=${{ github.server_url }}/${{ github.repository }}
            org.opencontainers.image.version=${{ steps.version.outputs.VERSION }}
            org.opencontainers.image.created=${{ github.event.head_commit.timestamp }}
            org.opencontainers.image.revision=${{ github.sha }}

  release:
    name: Create GitHub Release
    runs-on: ubuntu-latest
    needs: [build, docker]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: release-artifacts

      - name: Extract changelog
        id: changelog
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          if [ -f CHANGELOG.md ]; then
            sed -n "/## \[${VERSION}\]/,/## \[/p" CHANGELOG.md | sed '$d' > release_notes.md
          else
            echo "Release $VERSION" > release_notes.md
          fi

      - name: Create GitHub Release
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

## Example: Node.js Release

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
    name: Build
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
        run: npm run build

      - name: Package
        run: |
          tar -czf dist.tar.gz dist/
          sha256sum dist.tar.gz > dist.tar.gz.sha256

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: |
            dist.tar.gz
            dist.tar.gz.sha256

  docker:
    name: Docker
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
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
    name: Release
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
          name: build

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
          files: |
            dist.tar.gz
            dist.tar.gz.sha256
```

## Example: Python Package Release

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
```

## Notes

- Trigger on tag push matching semantic version pattern
- Validate version format before proceeding
- Build and test before creating release
- Push Docker images with version tags and `latest`
- Extract changelog from CHANGELOG.md if available
- Attach build artifacts to GitHub release
- Use minimal permissions for security

## Related Files

- `agent/11_rules/github_rules.md`
- `agent/06_skills/devops/skill_github_release_flow.md`
- `agent/04_workflows/10_release_process.md`
