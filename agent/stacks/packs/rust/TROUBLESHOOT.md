# Rust Troubleshooting

## Common Errors

### 1. `linker 'cc' not found`

**Cause:** Missing C compiler (needed for linking).
**Fix:** Install `build-essential` (Linux) or `Visual Studio Build Tools` (Windows).

### 2. `mismatched types`

**Cause:** Strict type system.
**Fix:** Read the compiler error carefully. It usually explains exactly what type is expected vs found. Use `.into()` or explicit casting if safe.

### 3. `borrow of moved value`

**Cause:** Ownership rules.
**Fix:**

- Use `.clone()` if you need a copy.
- Pass by reference (`&value`) if the function doesn't need ownership.
- Use `Rc<RefCell<T>>` or `Arc<Mutex<T>>` for shared state (advanced).

### 4. `dependency not found`

**Fix:**

```bash

cargo clean
cargo update

```
