# Component: Backend App

**Component ID**: `app`
**Path**: `app`
**Confidence**: `High`
**Description**: The main Flask application source code.

## Detected Stacks

- **python**: Core language.
- **flask**: Web framework.
- **sqlalchemy**: ORM.

## Capabilities

| Category  | Command                  | Description                                       |
|:----------|:-------------------------|:--------------------------------------------------|
| **Test**  | `pytest tests/`          | Run tests for the app.                            |
| **Lint**  | `ruff check app/`        | Lint the app source code.                         |
| **Format**| `ruff format app/`       | Format the app source code.                       |

## Dependencies

- **python**: 3.10+
- **pip**: Requirements in `requirements.txt`

## Component Dependencies

- **depends_on**:
  - `root` (Infrastructure)

## Paths

- **owned_paths**:
  - `app/**`
  - `tests/**`

- **shared_paths**:
  - `agent/workflows/_stack/python_*.md`
