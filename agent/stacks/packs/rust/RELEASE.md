# Rust Release Policy

## Versioning

- Semantic Versioning in `Cargo.toml`.
- `version = "1.0.0"`

## Optimization

- Always build with `--release`.
- Stripping symbols: Add to `Cargo.toml`:

  ```toml

  [profile.release]
  strip = true
  lto = true
```

## Checklist

- [ ] `cargo test` passes.
- [ ] `cargo clippy` passes (no warnings).
- [ ] `cargo audit` (if installed) shows no vulnerabilities.
- [ ] Documentation updated (`cargo doc`).
