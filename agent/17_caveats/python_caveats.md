# Python Caveats & Footguns

Issue-Key example: `Issue-Key: PYTHON-1834fa`.

- Always use `python -m pip`; plain `pip` may target different interpreter.
- Enforce venv per project; fail CI if `sys.prefix` not inside repo venv.
- Lock dependencies (pip-tools/poetry/uv) and check with hashes; avoid unpinned `latest`.
- Native builds on Alpine require musl-compatible wheels; prefer manylinux or compile with proper toolchain.
- Avoid circular imports by keeping side effects out of top-level modules; prefer src/ layout.
- Logging must mask secrets; disable debug logging in prod; avoid logging request bodies.
- `eval`/`exec`/`subprocess.*shell=True` with user input are banned unless justified.
- Datetimes must be timezone-aware; set `TZ=UTC` and use `datetime.now(timezone.utc)`.
- For async apps, never block event loop—use async libraries or executors.
- Clean MANIFEST/package_data; missing assets break wheels; verify via `python -m build` in CI.
