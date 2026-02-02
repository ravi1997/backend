# Python Diagnostics Bundle

- Interpreter/env: `which python`, `python -V`, `python -c "import sys;print(sys.prefix)"`.
- Package health: `python -m pip list`, `pip check`, `python -m pip debug --verbose`.
- Dependency resolution: `python -m pip install -r requirements.txt --dry-run` (or `pip-compile --dry-run` if pip-tools used).
- Build: `python -m build` to create sdist/wheel; inspect `dist/` contents (`tar -tf dist/*.tar.gz | head`).
- Imports: `python -X importtime -c "import app"` for cycles; `python -c "import pkg_resources, sys; print([d.project_name for d in pkg_resources.working_set])"`.
- Async/threads: run app/tests with `PYTHONASYNCIODEBUG=1`; enable faulthandler `python -X faulthandler ...`.
- Security: `rg "eval\(|exec\(" src`; `rg "shell=True" src`.
- Performance: profile with `python -m cProfile -o profile.out -m pytest tests/target_test.py` or `py-spy record` (if available).
