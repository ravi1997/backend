# Python Packaging Checklist (Add-On)

- Verify correct Python version/venv (`python -V`, sys.prefix) and use `python -m pip` exclusively.
- Build artifacts locally: `python -m build`; inspect wheel/sdist for package data and metadata.
- Lock dependencies with hashes (pip-tools/poetry/uv); run `pip check` after install.
- Ensure entry_points/console_scripts present and tested in clean venv.
- Confirm MANIFEST/package_data includes templates/static assets; no stray .pyc or cache directories.
- Wheels are manylinux/musllinux where needed; avoid platform mismatch for target deploys.
- Security: scan for `eval/exec/shell=True`, secret logging, and ensure license/classifiers set.
