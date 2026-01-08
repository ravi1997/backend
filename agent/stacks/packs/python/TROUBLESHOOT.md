# Python Troubleshooting

## Common Issues

### ImportError / ModuleNotFoundError
- **Symptom**: Python can't find a package.
- **Fix**: Check `sys.path`, ensure environment is activated (`which python`), check `__init__.py` files.

### Dependency Conflicts
- **Symptom**: Version mismatch errors during install.
- **Fix**: Use `pipdeptree` to inspect graph. Use `poetry` or `pip-tools` for lock files.

### GIL / Performance
- **Symptom**: CPU-bound task is slow and not using all cores.
- **Fix**: Use `multiprocessing` instead of `threading`. Use C extensions or JIT (PyPy, Numba).

### Encoding Errors
- **Symptom**: `UnicodeDecodeError`.
- **Fix**: Explicitly specify `encoding='utf-8'` when opening files.
