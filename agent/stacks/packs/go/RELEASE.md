# Go Release Policy

## Versioning

- Use Semantic Versioning (v1.0.0).
- Tag releases in git: `git tag v1.0.0`.

## Build Artifacts

- **Binaries:** Compile for target OS/Arch.

  ```bash

  GOOS=linux GOARCH=amd64 go build -o app-linux-amd64
```

- **Docker:** Multi-stage build producing slim/scratch image.

## Checklist

- [ ] `go vet ./...` passes.
- [ ] `go test -race ./...` passes (check data races).
- [ ] `golangci-lint` passes.
- [ ] `go.mod` is tidy (`go mod tidy`).
