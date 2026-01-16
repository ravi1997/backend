# Go Testing Guide

## Framework

- **Standard Library**: `testing` package is preferred.
- **Assertions**: Use `testify/assert` if needed, but standard `if got != want` is idiomatic.

## Commands

### Run All Tests

```bash
go test ./...
```

### Run Specific Test

```bash
go test -run TestName ./pkg/mypkg
```

### Coverage

```bash
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

## Best Practices

- **Table Driven Tests**: Use slice of structs for test cases.
- **Subtests**: Use `t.Run("desc", func(t *testing.T) { ... })`.
- **Mocks**: Use interfaces to mock dependencies.
