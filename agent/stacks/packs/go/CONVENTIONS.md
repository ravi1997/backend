# Go Coding Conventions

## Formatting

- **Tool**: `gofmt` or `goimports` MUST be used.
- **Rule**: Standard Go formatting is non-negotiable.

## Structure

- **Package Layout**: Follow standard Go project layout.
  - `cmd/`: Main applications.
  - `pkg/`: Library code ok to use by external apps.
  - `internal/`: Private library code.
- **Error Handling**:
  - Return errors as the last return value.
  - Don't panic unless startup fails.
  - Use `errors.Is` and `errors.As`.

## Naming

- **Interfaces**: End in `-er` (e.g., `Reader`, `Writer`).
- **Getters**: No `Get` prefix (e.g., `Owner()`, not `GetOwner()`).
- **Interfaces**: Accept interfaces, return structs.

## Dependencies

- Use `go mod` for dependency management.
- Vendor dependencies if build reproducibility is critical: `go mod vendor`.
