# Python Hard Cases & Failure Scenarios

Issue-Key example: `Issue-Key: PYTHON-b41c2d`. Prompt: `prompts/hard_cases/python_hard_cases.txt`.

## Environments & Dependencies

### HC-PY-001: venv Mismatch
**Symptom:**
```
ModuleNotFoundError: No module named 'app'
```
**Likely Causes:** using global interpreter; wrong venv activated.
**Fast Diagnosis:** `which python`, `python -c "import sys;print(sys.prefix)"`.
**Fix Steps:** create/activate correct venv; pin python version; use `.python-version`/tox/uv.
**Prevention:** activate via scripts; CI enforces venv usage.

### HC-PY-002: Dependency Resolver Conflicts
**Symptom:**
```
ResolutionImpossible: ... because these package versions have conflicting dependencies
```
**Likely Causes:** incompatible pins; mixed constraints.
**Fast Diagnosis:** `pip check`; `pip install -r requirements.txt --dry-run`.
**Fix Steps:** relax/pin versions; use constraints file; upgrade pip resolver.
**Prevention:** lock deps with pip-tools/poetry/uv; CI `pip check` gate.

### HC-PY-003: Compiled Dep Build Fail
**Symptom:**
```
Failed building wheel for cryptography
```
**Likely Causes:** missing build essentials, openssl headers, rust.
**Fast Diagnosis:** `python -m pip debug --verbose | grep -i external`; check system packages.
**Fix Steps:** install build deps (build-essential, libssl-dev, rust); use manylinux wheels.
**Prevention:** pin manylinux wheels; containerize builds.

### HC-PY-004: Platform Mismatch (arm64 vs amd64 wheels)
**Symptom:**
```
ERROR: <pkg> has no compatible wheel
```
**Likely Causes:** installing x86 wheels on arm; missing universal wheels.
**Fast Diagnosis:** `python - <<'PY'
import platform;print(platform.machine())
PY`
**Fix Steps:** use platform-specific wheels; build from source with proper toolchain or use `--platform` with pip download.
**Prevention:** provide cross-built wheels; test on target arch.

### HC-PY-005: Editable Install Breakage
**Symptom:** import fails after moving files; `pip install -e .` outdated.
**Likely Causes:** setup.cfg/pyproject paths wrong; src layout mismatch.
**Fast Diagnosis:** `pip show -f <pkg>`; check `PYTHONPATH`.
**Fix Steps:** re-install editable; correct package name/package_dir; use src/ layout.
**Prevention:** prefer src layout; run `pip install -e .` in CI.

### HC-PY-006: Multiple Interpreters in PATH
**Symptom:** running `python` differs from `pip` target.
**Likely Causes:** pip installs to different interpreter.
**Fast Diagnosis:** `python -m pip --version`; `pip --version`.
**Fix Steps:** always use `python -m pip`; align PATH/venv.
**Prevention:** scripts call `python -m pip`; use tools like pipx/uv.

### HC-PY-007: Pip Cache Poisoning
**Symptom:** corrupted wheel causes repeated failure.
**Likely Causes:** broken cache entry.
**Fast Diagnosis:** `pip cache list | head`; compare checksum.
**Fix Steps:** `pip cache purge` or remove offending wheel.
**Prevention:** periodic cache cleanup; use hashes in requirements.

### HC-PY-008: pyproject Misconfiguration
**Symptom:**
```
Backend 'setuptools.build_meta' is missing
```
**Likely Causes:** build-backend missing/typo; missing build-system requires.
**Fast Diagnosis:** inspect pyproject `[build-system]`; `pip build` output.
**Fix Steps:** add correct `build-backend` and `requires`; pin versions.
**Prevention:** validate with `pipx run build .`; CI builds sdist/wheel.

### HC-PY-009: Circular Imports
**Symptom:**
```
ImportError: cannot import name 'X' from partially initialized module
```
**Likely Causes:** modules import each other at top-level.
**Fast Diagnosis:** inspect import graph; `pip install snakeviz`? (optional). Use `python -X importtime` to see cycle.
**Fix Steps:** move imports inside functions; refactor shared utilities; avoid side effects on import.
**Prevention:** lint for cyclic imports; architecture guidelines.

### HC-PY-010: Namespace Package Collisions
**Symptom:** wrong module loaded when name overlaps.
**Likely Causes:** overlapping namespace packages or old dist left behind.
**Fast Diagnosis:** `python - <<'PY'
import pkg_resources;print([d for d in pkg_resources.working_set if 'mypkg' in d.project_name])
PY`
**Fix Steps:** uninstall conflicting dist; rename package; clean site-packages.
**Prevention:** unique package names; clean venv before install.

## Runtime & Async

### HC-PY-011: Asyncio Event Loop Misuse
**Symptom:**
```
RuntimeError: This event loop is already running
```
**Likely Causes:** nested `asyncio.run`, mixing sync/async.
**Fast Diagnosis:** check call stack; search for `asyncio.run` in code.
**Fix Steps:** use `asyncio.get_event_loop` appropriately; avoid nested run; use `await` properly.
**Prevention:** async patterns review; tests for async functions.

### HC-PY-012: Blocking Calls in Async Context
**Symptom:** high latency; warnings about blocking event loop.
**Likely Causes:** heavy CPU/I/O in async without threads.
**Fast Diagnosis:** `asyncio` debug mode; tracebacks show blocking call.
**Fix Steps:** offload to executor (`loop.run_in_executor`), use aiohttp/async clients.
**Prevention:** lint for blocking calls; load tests on async paths.

### HC-PY-013: Thread Safety Issues
**Symptom:** random data corruption in multithreaded code.
**Likely Causes:** shared mutable state; not using locks.
**Fast Diagnosis:** add logging; use `faulthandler.dump_traceback_later`; run under `PYTHONHASHSEED=0`.
**Fix Steps:** protect shared data with locks/queues; prefer multiprocessing for CPU bound.
**Prevention:** concurrency guidelines; tests with race detectors (pytest-randomly, stress).

### HC-PY-014: Encoding Problems
**Symptom:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```
**Likely Causes:** wrong encoding assumption.
**Fast Diagnosis:** check file encoding; `file -bi filename`.
**Fix Steps:** open files with explicit encoding; normalize inputs.
**Prevention:** enforce UTF-8; add `PYTHONIOENCODING=utf-8` in env.

### HC-PY-015: Timezone Bugs
**Symptom:** timestamps shifted.
**Likely Causes:** naive datetime usage.
**Fast Diagnosis:** search for `datetime.now()` without tz.
**Fix Steps:** use `datetime.now(tz=timezone.utc)`; store TZ-aware; use pendulum/arrow if needed.
**Prevention:** linters banning naive datetime; tests with fixed tz offset.

### HC-PY-016: Path Traversal in File Uploads
**Symptom:** files saved outside intended dir.
**Likely Causes:** unsanitized filenames.
**Fast Diagnosis:** review upload handlers; test with `../` payloads.
**Fix Steps:** normalize with `os.path.basename` and allowlist extensions; use safe directories.
**Prevention:** security review for file handling; tests for traversal.

### HC-PY-017: Unsafe eval/exec
**Symptom:** security review flags dynamic eval of user data.
**Likely Causes:** using eval on inputs.
**Fast Diagnosis:** `rg "eval\(" src`.
**Fix Steps:** replace with safe parsers; sandbox or remove.
**Prevention:** lint banning eval/exec; code review policy.

### HC-PY-018: Secrets in Logs
**Symptom:** tokens/keys visible in logs.
**Likely Causes:** logging request bodies/config.
**Fast Diagnosis:** `rg "password|secret|token" logs || true`.
**Fix Steps:** mask secrets; avoid logging sensitive fields; use structured logging filters.
**Prevention:** logging policy; automated scanners in CI.

### HC-PY-019: Command Injection
**Symptom:** unexpected shell commands executed from user input.
**Likely Causes:** using `shell=True` with unsanitized data.
**Fast Diagnosis:** search for `subprocess.*shell=True`.
**Fix Steps:** use list args without shell; sanitize inputs; apply allowlists.
**Prevention:** lint rules; security review.

## Packaging & Distribution

### HC-PY-020: Entry Points Missing
**Symptom:** console script not installed.
**Likely Causes:** entry_points not declared correctly.
**Fast Diagnosis:** inspect pyproject/setup.cfg entry_points; `pip show -f` output.
**Fix Steps:** add correct `entry_points.console_scripts`; reinstall.
**Prevention:** add smoke test calling console script in CI.

### HC-PY-021: Wheel Metadata Wrong
**Symptom:** install places package under wrong name/version.
**Likely Causes:** metadata mismatch.
**Fast Diagnosis:** `pip debug --verbose`; inspect `*.dist-info` metadata.
**Fix Steps:** align package name/version; set `name`/`version` in pyproject; rebuild wheel.
**Prevention:** build wheels in CI and inspect metadata automatically.

### HC-PY-022: Incomplete MANIFEST/Package Data
**Symptom:** templates/data files missing in sdist/wheel.
**Likely Causes:** MANIFEST.in missing include; package_data not set.
**Fast Diagnosis:** `tar -tf dist/*.tar.gz`; check wheel contents.
**Fix Steps:** add include directives; use `include_package_data=True` and package_data entries; rebuild.
**Prevention:** packaging tests verifying resources present.

### HC-PY-023: Native Extensions Missing ABI Tag
**Symptom:** wheel rejected by pip for platform tag.
**Likely Causes:** build backend not producing abi3 or correct tags.
**Fast Diagnosis:** `pip debug --verbose` shows tags; inspect wheel filename.
**Fix Steps:** set `py_limited_api`/abi3 if applicable; build per-ABI wheels; audit setup.cfg.
**Prevention:** CI builds wheels for target ABIs; use cibuildwheel.

### HC-PY-024: Namespace Collisions in Build Artifacts
**Symptom:** multiple wheels provide same package; runtime import confusion.
**Likely Causes:** old wheels in env; dev editable plus installed release.
**Fast Diagnosis:** `pip show -f <pkg>` to see file origins.
**Fix Steps:** uninstall duplicates; clean site-packages; rebuild with unique package names.
**Prevention:** clean venv between installs; enforce unique package names.

### HC-PY-025: PyInstaller/Executable Build Fails
**Symptom:**
```
failed to execute script main
```
**Likely Causes:** missing data files, hidden imports.
**Fast Diagnosis:** inspect PyInstaller warnings; run with `--log-level=DEBUG`.
**Fix Steps:** add hiddenimports, collect data files, set correct entry script.
**Prevention:** reproducible spec file; CI build and smoke test executable.

### HC-PY-026: ImportError in Frozen Apps
**Symptom:** modules missing in packaged app.
**Likely Causes:** dynamic imports not detected.
**Fast Diagnosis:** review code for `importlib.import_module` calls; check PyInstaller analysis.
**Fix Steps:** list hidden imports; include packages explicitly.
**Prevention:** packaging tests exercising dynamic paths.

## Testing & Tooling

### HC-PY-027: pytest Fixture Misuse
**Symptom:**
```
fixture 'client' not found
```
**Likely Causes:** conftest not discovered; wrong scope name.
**Fast Diagnosis:** ensure conftest in test path; `pytest --fixtures`.
**Fix Steps:** move conftest to correct package; rename fixture; ensure __init__.py not blocking discovery when needed.
**Prevention:** test layout lint; template fixtures.

### HC-PY-028: Flaky Tests (Timing/Random)
**Symptom:** tests fail intermittently.
**Likely Causes:** randomness, time-based asserts, external services.
**Fast Diagnosis:** run with `pytest -n auto --maxfail=1 --durations=5`; seed randomness.
**Fix Steps:** control time/random seeds; add retries/backoff for IO; stub external services.
**Prevention:** mark flaky; quarantine list; run deterministic seeds in CI.

### HC-PY-029: mypy Typing Errors / Strictness
**Symptom:** mypy fails on strict config.
**Likely Causes:** missing stubs, strict optional issues.
**Fast Diagnosis:** run `mypy --strict` to see errors; check `mypy.ini`.
**Fix Steps:** add typing stubs; use TypedDict/Protocol; narrow `Any` usage.
**Prevention:** enforce typing CI; incremental adoption plan.

### HC-PY-030: Performance Hotspots
**Symptom:** high CPU/slow endpoints.
**Likely Causes:** unvectorized loops, JSON serialization overhead.
**Fast Diagnosis:** profile with cProfile/py-spy; inspect top functions.
**Fix Steps:** optimize hot paths; use caching; consider C extensions or numpy.
**Prevention:** perf tests in CI; monitor latency budgets.

### HC-PY-031: Packaging License/Compliance Gaps
**Symptom:** missing LICENSE classifiers or bundled license files.
**Likely Causes:** metadata not set; files not included.
**Fast Diagnosis:** inspect `PKG-INFO`; check wheel contents.
**Fix Steps:** set classifiers; include LICENSE in MANIFEST; rebuild.
**Prevention:** packaging checklist; automated license audit.

### HC-PY-032: CLI Argument Parsing Errors
**Symptom:**
```
error: unrecognized arguments
```
**Likely Causes:** argparse config mismatch.
**Fast Diagnosis:** run `cmd --help`; inspect parser definitions.
**Fix Steps:** align parser with docs; add tests for CLI args.
**Prevention:** CLI contract tests; keep docs and parser in sync.

## Issue-Key and Prompt Mapping
- Example Issue-Key: `Issue-Key: PYTHON-5bd8e2`
- Use prompt: `prompts/hard_cases/python_hard_cases.txt`
