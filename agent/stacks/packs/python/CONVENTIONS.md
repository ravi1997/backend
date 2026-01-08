# Python Conventions

## File Structure
- `src/`: Source code (optional but recommended for packaging).
- `tests/`: Test files.
- `docs/`: Documentation (Sphinx/MkDocs).
- `pyproject.toml`: Modern configuration file.

## Naming
- **Modules/Packages**: lowercase, short, unique.
- **Classes**: CamelCase.
- **Functions/Variables**: snake_case.
- **Constants**: SCREAMING_SNAKE_CASE.
- **Private API**: _leading_underscore.

## Code Style
- Adhere to **PEP 8**.
- Use type hints (PEP 484) everywhere.
- Use docstrings (Google or NumPy style).
- Sort imports (isort or ruff).
