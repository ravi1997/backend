# Autofill: Path & Service Inference Rules

Goal: Automatically detecting project structure and details using universal language patterns.
**If `AUTO_CONTEXT` is incomplete, use these rules to fill gaps.**

## 1. Repo Root & Project Type (Detection)

Detect the `repo_root` (where the config file lives) and `project_type`.

| Rule                                   | Output                                |
|:---------------------------------------|:--------------------------------------|
| `pyproject.toml` or `requirements.txt` | `project_type="python"`               |
| `package.json`                         | `project_type="nodejs"`               |
| `pom.xml`                              | `project_type="java"` (setup: maven)  |
| `build.gradle` / `build.gradle.kts`    | `project_type="java"` (setup: gradle) |
| `CMakeLists.txt`                       | `project_type="cpp"` (setup: cmake)   |
| `go.mod`                               | `project_type="go"`                   |
| `pubspec.yaml`                         | `project_type="flutter"`              |
| `Cargo.toml`                           | `project_type="rust"`                 |

## 2. Backend Directory (`backend_dir` or `source_dir`)

*Where is the code?*

1. **Standard:** `src/`, `app/`, or `lib/` (standard for Java/C++/Rust).
2. **Explicit:** `backend/`, `server/`, `api/`.
3. **Root:** If `src/` is missing and config files (like `app.py`, `package.json`) are at root, set `source_dir="."`.

## 3. Package/App Identification

*What is the main namespace or app name?*

- **Python:** Look for `setup.py` name, or directory with `__init__.py`.
- **Java:** Look in `pom.xml` (`<artifactId>`) or `build.gradle` (`rootProject.name`).
- **Node.js:** Look in `package.json` (`"name"` field).
- **Go:** Look in `go.mod` (`module <name>`).
- **C++:** Look in `CMakeLists.txt` (`project(<NAME>)`).

## 4. Entrypoint Inference

*How do I start it?*

- **Python (Flask/Django):** `wsgi.py`, `app.py`, `manage.py`.
- **Node.js:** `package.json` -> `"main"` or `"scripts": {"start": "..."}`.
- **Java:** Look for `public static void main` or Spring Boot's `@SpringBootApplication`.
- **Go:** `main.go` or `cmd/server/main.go`.
- **Flutter:** `lib/main.dart`.
- **C++:** Look for `add_executable` in CMakeLists.

## 5. Docker Compose Service Names

*Scanning `docker-compose.yml`...*

- `compose_backend_service`: Services running `flask`, `node`, `java`, `go run`, or building from `backend/`.
- `compose_frontend_service`: Services running `npm start`, `nginx` (if pure static), or building from `frontend/`.
- `compose_db_service`: Images like `postgres`, `mysql`, `mongo`.

## 6. Port Detection

- **Docker:** `ports: ["8000:8000"]` -> `app_port=8000`.
- **Node:** `"start": "PORT=3000 node index.js"` -> `3000`.
- **Python:** `app.run(port=5000)` -> `5000`.
- **Spring Boot:** `application.properties` -> `server.port`.
- **Go:** `http.ListenAndServe(":8080"` -> `8080`.

## 7. Systemd Unit Name

- Search `systemd/` or `deploy/` for `*.service`.
- Fallback: `{app_name}.service`.

## 8. Log Locations

- **Nginx:** `/var/log/nginx/access.log`, `/var/log/nginx/error.log`.
- **Systemd:** `journalctl -u {systemd_unit} -e`.
- **Docker:** `docker compose logs -f {service_name}`.

## 9. Minimal "Human in the Loop"

Only ask if **Critical** fields are missing:

1. `project_type` (if ambigous, e.g., Python AND Node both present).
2. `env` (default to `production` if unsure for safety).
3. `app_name` (if no config file found).
