# Go Deployment Guide

## Build Strategy

Go produces static binaries, making deployment simple.

### Build Binary

```bash
# Disable CGO for static linking if possible
CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./cmd/app
```

## Docker Deployment

See `agent/snippets/Dockerfile.go.md` for reference.

### Multi-Stage Build

1. **Builder**: Compiles binary.
2. **Runner**: `scratch` or `alpine` image containing only binary and CA certs.

## Environment Variables

- Config should be read from ENV.
- Use libraries like `kelseyhightower/envconfig` or `viper`.

## Health Checks

- Expose `/health` or `/ready` endpoint.
