# Subflow: Python Feature Delivery

**Stack:** Python
**Parent:** `../feature_delivery.md`

## Build & Test

```bash
# Install dependencies
pip install -r requirements.txt

# Run Tests
pytest -v
```

## Linting

```bash
# Format
ruff format .

# Check
ruff check .
```

## Missing Environment

If the environment cannot run tests (e.g. valid cross-compile toolchain missing):
1. **Reproduce:** Document setup in `REPRODUCE.md`.
2. **Minimal Test:** Create a script to run available tests.
3. **Confidence:** Downgrade confidence until verified on target.

## Role Checklist: Tester

**Reference:** `agent/stacks/packs/python/TESTING.md`

- [ ] **Install:** `pip install` works cleanly.
- [ ] **Tests:** `pytest` passes (100%).
- [ ] **Lint:** `ruff` or `flake8` is clean.
- [ ] **Types:** `mypy` check passes (if enforced).
