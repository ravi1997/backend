# Component: Root

**Component ID**: `root`
**Path**: `.`
**Confidence**: `High`
**Description**: The backend project repository for the Brain AI, built with Python and Flask.

## Detected Stacks

- **python**: Core language for the backend application.
- **flask**: Web framework used for the API.
- **docker**: Containerization for development and deployment.
- **markdown**: Documentation and agent configuration.

## Capabilities

| Category  | Command                  | Description                                       |
|:----------|:-------------------------|:--------------------------------------------------|
| **Build** | `docker compose build`   | Build the backend services.                       |
| **Test**  | `pytest`                 | Run the test suite.                               |
| **Run**   | `docker compose up`      | Run the application stack locally.                |
| **Lint**  | `ruff check .`           | Lint the codebase using Ruff.                     |
| **Format**| `ruff format .`          | Format the codebase using Ruff.                   |

## Dependencies

- **python**: 3.10+
- **docker**: Engine & Compose

## Deploy / Release

- **Type**: `service`
- **Release**: Deployment via Docker artifacts.

## Component Dependencies

- **depends_on**: []

## Paths

- **owned_paths**:
  - `app/` (Application Source)
  - `agent/` (Agent Configuration)
  - `tests/` (Test Suite)
  - `*.py` (Root scripts)
  - `docker-compose*.yml` (Infrastructure)

- **shared_paths**:
  - `agent/workflows/_stack/*.md`
