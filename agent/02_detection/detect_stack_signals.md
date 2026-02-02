# Detection: Stack Signals

## Purpose

Identifies specific languages, frameworks, and build tools using "fingerprints".

## Identification Logic

| Stack component | Signals (Files/Strings) | Fingerprint File | Notes |
|---|---|---|---|
| **Python (General)** | `requirements.txt`, `pyproject.toml`, `Pipfile`, `.py` | `stack_fingerprints/python_*.md` | Check for Flask/FastAPI |
| **Python Flask** | `from flask import`, `Flask(__name__)`, `requirements.txt` with `flask` | `stack_fingerprints/python_flask.md` | Web framework |
| **Python FastAPI** | `from fastapi import`, `FastAPI()`, `requirements.txt` with `fastapi` | `stack_fingerprints/python_fastapi.md` | API framework |
| **Node.js (General)** | `package.json`, `node_modules` | `stack_fingerprints/node_express.md` | Check for Express/Next.js |
| **Node.js Express** | `"express"` in package.json, `require('express')` | `stack_fingerprints/node_express.md` | Backend framework |
| **Next.js** | `"next"` in package.json, `next.config.js`, `pages/` or `app/` | `stack_fingerprints/nextjs.md` | React framework |
| **React/Vite** | `vite.config.ts`, `React` imports, `"react"` in package.json | `stack_fingerprints/react_vite.md` | Frontend framework |
| **Java (General)** | `pom.xml`, `build.gradle`, `.java` | `stack_fingerprints/java_spring.md` | Check for Spring |
| **Java Spring** | `spring-boot` in pom.xml/build.gradle, `@SpringBootApplication` | `stack_fingerprints/java_spring.md` | Enterprise framework |
| **C (General)** | `Makefile`, `.c`, `.h`, no `.cpp` files | `stack_fingerprints/c_make.md` | Pure C projects |
| **C++ (General)** | `CMakeLists.txt`, `.cpp`, `.hpp`, `.h` | `stack_fingerprints/cpp_cmake.md` | Check C++ standard |
| **C++17** | `set(CMAKE_CXX_STANDARD 17)` or `-std=c++17` in CMakeLists.txt | `stack_fingerprints/cpp_cmake.md` | C++17 standard |
| **C++20** | `set(CMAKE_CXX_STANDARD 20)` or `-std=c++20` in CMakeLists.txt | `stack_fingerprints/cpp_cmake.md` | C++20 standard |
| **C++23** | `set(CMAKE_CXX_STANDARD 23)` or `-std=c++23` in CMakeLists.txt | `stack_fingerprints/cpp_cmake.md` | C++23 standard |
| **CMake** | `CMakeLists.txt`, `cmake/` directory, `*.cmake` files | `stack_fingerprints/cpp_cmake.md` | Build system |
| **Flutter** | `pubspec.yaml`, `lib/main.dart`, `flutter` command | `stack_fingerprints/flutter.md` | Mobile framework |
| **Static Web** | `index.html` + no build system (no package.json, no build tools) | `stack_fingerprints/static_web.md` | Pure HTML/CSS/JS |
| **Docker** | `Dockerfile`, `docker-compose.yml`, `.dockerignore` | DevOps stack | Containerization |
| **Docker Compose** | `docker-compose.yml`, `docker-compose.override.yml`, `compose.yaml` | DevOps stack | Multi-container |
| **Docker Multi-Stage** | `FROM ... AS builder` in Dockerfile | DevOps stack | Optimized builds |
| **DevContainer** | `.devcontainer/devcontainer.json`, `.devcontainer.json` | DevOps stack | Dev environment |
| **Container Registry** | `ghcr.io`, Docker Hub references in configs | DevOps stack | Image hosting |
| **GitHub Actions** | `.github/workflows/*.yml`, `.github/workflows/*.yaml` | DevOps stack | CI/CD |
| **GitHub Templates** | `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/` | DevOps stack | Collaboration |
| **GitHub Governance** | `.github/CODEOWNERS`, `.github/dependabot.yml` | DevOps stack | Repository management |

## Procedure

1. **File Check**: Look for filenames in the root.
2. **Content Check**: If filenames are missing, grep for keywords in common entry files.
3. **Version Check**: Determine tool versions (e.g., `python --version`).
4. **Update State**: Write the detected stack to `agent/09_state/STACK_STATE.md`.

## Failure modes

- If conflicting signals are found (e.g. `pom.xml` AND `package.json`), identify if it's a monorepo.

## Related Files

- `stack_fingerprints/`
