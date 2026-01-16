# Go Troubleshooting

## Common Errors

### 1. `missing go.sum entry`

**Symptom:** Build fails with missing sum.
**Fix:**

```bash

go mod tidy

```

### 2. `imports ...: cannot find package`

**Symptom:** Dependencies not found.
**Fix:**

```bash

go get ./...

# OR

go mod download

```

### 3. `cgo: C compiler "gcc" not found`

**Cause:** Missing C compiler for CGO.
**Fix:** Install `build-essential` (Linux) or `mingw` (Windows). Or disable CGO:

```bash

CGO_ENABLED=0 go build ...

```

### 4. `connection refused` (Docker)

**Cause:** App listening on `127.0.0.1` instead of `0.0.0.0`.
**Fix:** Change `http.ListenAndServe("localhost:8080", ...)` to `http.ListenAndServe(":8080", ...)` or `0.0.0.0:8080`.
