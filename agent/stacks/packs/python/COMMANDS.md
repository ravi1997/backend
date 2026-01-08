# Python Command Map

## Toolchain Selection Rules
1. **Poetry**: If `pyproject.toml` and `poetry.lock` exist -> Use `poetry run`.
2. **Pipenv**: If `Pipfile` exists -> Use `pipenv run`.
3. **Venv**: If `venv/` or `.venv/` exists -> Source it, then use python/pip directly.
4. **Default**: `python3 -m ...`

## Canonical Commands

### Build
**Wheel/Sdist**
```bash
python3 -m build
# OR
poetry build
```

### Test
**Pytest**
```bash
python3 -m pytest
# OR
poetry run pytest
```

### Lint/Format
**Ruff (Recommended)**
```bash
ruff check . --fix
ruff format .
```

**Black & Flake8**
```bash
black .
flake8 .
```

### Run
**Standard Script**
```bash
python3 main.py
```

**Module**
```bash
python3 -m mypackage.main
```

### Package
**Twine (Upload)**
```bash
python3 -m twine upload dist/*
```

### CI
**GitHub Actions (Example)**
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: "3.10"
- run: pip install -r requirements.txt
- run: python -m pytest
```
