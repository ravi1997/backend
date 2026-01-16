# Rust Command Map

## Toolchain Selection

1. **Cargo**: The standard build system. Always use `cargo`.
2. **Rustup**: For toolchain management (stable/nightly).

## Canonical Commands

### Build

#### Development

```bash

cargo build

```

#### Release

```bash

cargo build --release

```

### Test

#### Standard

```bash

cargo test

```

### Lint/Format

#### Format

```bash

cargo fmt

```

#### Lint (Clippy)

```bash

cargo clippy -- -D warnings

```

### Run

#### Dev

```bash

cargo run

```

### Package

#### Docker

```bash

docker build -t my-rust-app .

# Use multistage build with smaller base image (distroless)

```

### CI

#### GitHub Actions

```yaml

- uses: actions-rs/toolchain@v1
  with:
    toolchain: stable
- run: cargo test

```
