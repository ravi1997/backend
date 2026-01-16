# Snippet: Dockerfile for Go (Multi-stage Scratch)

```dockerfile

# Scope: Go (Golang)

# Metadata: multi-stage, scratch, small-image

# CLARIFY: go_version (e.g. 1.21)

# --- Build Stage ---

FROM golang:1.21-alpine AS builder

WORKDIR /app

# Install git if needed for dependencies

RUN apk add --no-cache git

COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Build statically linked binary

RUN CGO_ENABLED=0 GOOS=linux go build -o /app/main .

# --- Runtime Stage ---

# Use 'scratch' for smallest possible image

FROM scratch

WORKDIR /app

# Copy CA certificates if making external requests

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy binary

COPY --from=builder /app/main .

# Copy any necessary config files or templates

# COPY --from=builder /app/config ./config

# Run as non-privileged user (cannot run commands in scratch, but can set user ID of process)

USER 1001

EXPOSE 8080

CMD ["./main"]

```
