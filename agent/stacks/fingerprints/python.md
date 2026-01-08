# Python Project Fingerprint

## Signatures

| File / Pattern | Type | Confidence | Notes |
| :--- | :--- | :--- | :--- |
| `pyproject.toml` | Config | 1.0 | Modern Python project standard |
| `requirements.txt` | Dependencies | 0.9 | Standard pip requirements |
| `Pipfile` | Config | 1.0 | Pipenv project |
| `poetry.lock` | Lockfile | 1.0 | Poetry project |
| `uv.lock` | Lockfile | 1.0 | uv project |
| `setup.py` | Build Definition | 0.9 | Legacy packaging (check if it's the primary build) |
| `manage.py` | Framework | 1.0 | Django specific |
| `*.py` | Source Code | 0.3 | Presence of source files only |

## Related Tools

-   **Build/Package**: `pip`, `poetry`, `flit`, `hatch`, `uv`
-   **Environment**: `venv`, `virtualenv`, `conda`
-   **Test**: `pytest`, `unittest`, `tox`, `nox`
