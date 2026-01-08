# Python Release & Packaging

## Packaging Formats
- **Wheel (.whl)**: Built distribution (faster installation).
- **Sdist (.tar.gz)**: Source distribution.
- **Docker**: Container image.
- **PEX/Shiv**: Executable zip files.

## Release Checklist
- [ ] Update version in `pyproject.toml` or `__init__.py`.
- [ ] Tag git commit.
- [ ] Build distribution (`build` module).
- [ ] Upload to PyPI (TestPyPI first).

## Command Example
```bash
# Build
python3 -m build

# Check metadata
twine check dist/*

# Upload
twine upload dist/*
```
