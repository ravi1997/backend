# Go Command Map

## Toolchain Selection

1. **Modules**: If `go.mod` exists, use `go` commands.
2. **Make**: If `Makefile` exists, prefer `make <target>`.

## Canonical Commands

### Build

#### Standard

```bash

go build -o bin/app ./cmd/app

# OR

go build .

```

### Test

#### Standard

```bash

go test ./... -v

```

#### With Coverage

```bash

go test ./... -coverprofile=coverage.out

```

### Lint/Format

#### Format

```bash

go fmt ./...

```

#### Lint (GolangCI-Lint)

```bash

golangci-lint run

```

### Run

#### Dev

```bash

go run main.go

# OR

go run ./cmd/app

```

### Package

#### Docker

```bash

docker build -t my-go-app .

```

### CI

#### GitHub Actions

```yaml

- uses: actions/setup-go@v4
  with:
    go-version: '1.21'
- run: go test ./...

```
