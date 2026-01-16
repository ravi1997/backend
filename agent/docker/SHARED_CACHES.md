# Shared Package Caching Guide

To significantly speed up builds and save disk space, you should share package caches across your Docker projects.

## Strategy: Host Bind Mounts (Recommended)

The most effective way to share packages across projects is to bind mount your **Host System's** cache directories into the container.

### 1. Node.js / Web

- **Host Path**: `~/.npm` (or `~/.cache/pnpm`)
- **Container Path**: `/root/.npm` (or `/root/.local/share/pnpm`)
- **Compose Config**:

  ```yaml
  volumes:
    - .:/app
    # Shared NPM Cache
    - ${HOME}/.npm:/root/.npm
  ```

### 2. Python (Pip)

- **Host Path**: `~/.cache/pip`
- **Container Path**: `/root/.cache/pip`
- **Compose Config**:

  ```yaml
  volumes:
    - .:/app
    # Shared Pip Cache
    - ${HOME}/.cache/pip:/root/.cache/pip
  ```

### 3. Java (Maven/Gradle)

- **Maven Host**: `~/.m2`
- **Maven Container**: `/root/.m2`
- **Gradle Host**: `~/.gradle`
- **Gradle Container**: `/root/.gradle`
- **Compose Config**:

  ```yaml
  volumes:
    - .:/app
    # Shared Maven Cache
    - ${HOME}/.m2:/root/.m2
  ```

### 4. Go (Golang)

- **Host Path**: `~/go/pkg/mod`
- **Container Path**: `/go/pkg/mod`
- **Compose Config**:

  ```yaml
  environment:
    - GOCACHE=/go/cache
  volumes:
    - .:/app
    # Shared Module Cache
    - ${HOME}/go/pkg/mod:/go/pkg/mod
    # Shared Build Cache
    - ${HOME}/.cache/go-build:/go/cache
  ```

### 5. Flutter

- **Host Path**: `~/.pub-cache`
- **Container Path**: `/root/.pub-cache` (or `/home/flutter/.pub-cache` depending on user)
- **Compose Config**:

  ```yaml
  volumes:
    - .:/app
    # Shared Pub Cache
    - ${HOME}/.pub-cache:/root/.pub-cache
  ```

## Alternative: External Named Volumes

If you prefer not to mount host directories directly, create global Docker volumes once:

1. **Create Volume**: `docker volume create npm_global_cache`
2. **Use in Compose**:

```yaml
version: '3.8'

services:
  app:
    volumes:
      - npm_global_cache:/root/.npm

volumes:
  npm_global_cache:
    external: true
```
