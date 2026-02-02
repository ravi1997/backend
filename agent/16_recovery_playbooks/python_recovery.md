# Python Recovery Playbook

Issue-Key `Issue-Key: PYTHON-<hash>`. Map to HC-PY-XXX.

## RECOVERY-PY-001: Environment/Dependency Issues
- Confirm interpreter/venv: `which python`, `python -m pip --version`; activate correct venv.
- Resolve conflicts with constraints; regenerate lock using pip-tools/poetry/uv; purge bad cache (`pip cache purge`).
- Install build essentials when wheels fail; prefer manylinux/musllinux wheels.
- Validate: `pip check` passes; app imports succeed.

## RECOVERY-PY-002: Packaging/pyproject Failures
- Inspect pyproject build-system; ensure backend/requirements set; run `python -m build` to reproduce.
- Fix MANIFEST/package_data/entry_points; rebuild wheel/sdist and inspect contents.
- Validate: `pip install dist/*.whl` in clean venv; console scripts run.

## RECOVERY-PY-003: Import/Circular/Namespace Problems
- Trace import graph; move imports inside functions; clean site-packages of old dists; rename overlapping packages.
- Validate: run unit tests and module import smoke test.

## RECOVERY-PY-004: Async/Concurrency Bugs
- Enable asyncio debug; remove nested `asyncio.run`; offload blocking calls; add locks or use multiprocessing where needed.
- Validate: async tests with timeouts; no event loop runtime errors.

## RECOVERY-PY-005: Security/Logging Issues
- Remove eval/exec on user input; sanitize shell calls; enforce allowlists.
- Add secret masking in logs; enforce UTF-8 and timezone-aware datetimes.
- Validate: security scans clean; targeted tests for traversal/injection.

## RECOVERY-PY-006: Testing & Flakiness
- Ensure conftest discovery; fix fixture names; control randomness/time; stub external calls.
- Validate: pytest runs stable locally and in CI with `-n auto` or repeated runs.

## RECOVERY-PY-007: Performance Hotspots
- Profile with cProfile/py-spy; optimize hot functions; add caching/vectorization.
- Validate: performance tests meet baseline; monitor CPU/latency metrics.
