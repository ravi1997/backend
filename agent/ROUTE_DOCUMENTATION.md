# Agent Route Documentation

This document details the routing logic for the AI Agent. It is designed for DEVELOPERS to understand how to interact with the agent to trigger specific workflows, similar to an API documentation.

## Core Routing Principles

The agent routes requests based on **Intent** (what you want to do) and **Stack/Scope** (which component you are working on).

**Routing Priority:**

1. **Scope:** Identify the active component (e.g., `backend`, `frontend`, `auth-service`).
2. **Stack:** Identify the technology (e.g., `python`, `react`, `docker`).
3. **Intent:** Match the user's request to a specific **Route** below.

---

## 🔴 Priority 1: Incidents (Production/Dev Support)

High-priority routes for handling system failures and errors.

### 1.1 HTTP Proxy Errors

* **Route Intent:** `HTTP 5xx`
* **Trigger Keywords:** `502`, `504`, `bad gateway`, `gateway timeout`
* **Target Workflow:** `workflows/nginx_502_504.md`
* **Description:** Diagnoses and fixes Nginx/Reverse Proxy errors. Checks upstream servers, log files, and configuration syntax.
* **Usage Example:** "Fix the 502 Bad Gateway error on the staging server."

### 1.2 Service Failures

* **Route Intent:** `Service Down`
* **Trigger Keywords:** `systemctl`, `failed`, `dead`, `inactive`
* **Target Workflow:** `workflows/systemd_failures.md`
* **Description:** Investigates crashed or failed system services. Checks journalctl logs, service status, and restarts services if safe.
* **Usage Example:** "The backend service is inactive/dead."

### 1.3 Database Issues

* **Route Intent:** `Database`
* **Trigger Keywords:** `connection refused`, `deadlock`, `migration fail`
* **Target Workflow:** `workflows/db_migrations.md`
* **Description:** Handles database connection issues and migration failures. Can run migration status checks, rollback, or apply pending migrations.
* **Usage Example:** "I'm getting a connection refused error from the database."

---

## 🟡 Priority 2: Build & Configuration

Routes for resolving build environments and configuration problems.

### 2.1 Build Failure (Docker)

* **Route Intent:** `Build Fail` (Stack: Docker)
* **Trigger Keywords:** `build failed`, `make error`
* **Target Workflow:** `workflows/docker_dev_loop.md`
* **Description:** diagnosing Docker build failures. Checks Dockerfile syntax, dependency installation, and container logs.
* **Usage Example:** "The docker build is failing."

### 2.2 Build Failure (C++)

* **Route Intent:** `Build Fail` (Stack: C++)
* **Trigger Keywords:** `build failed`, `make error`
* **Target Workflow:** `workflows/cpp_build_test.md`
* **Description:** Handles C++ compilation and linking errors. Runs make/cmake and parses error output.
* **Usage Example:** "Make error in the main target."

### 2.3 Build Failure (Web)

* **Route Intent:** `Build Fail` (Stack: Web/JS)
* **Trigger Keywords:** `build failed`, `npm error`
* **Target Workflow:** `workflows/web_build.md`
* **Description:** Addresses frontend build issues (Webpack/Vite/Next.js). Checks package.json, node_modules, and build scripts.
* **Usage Example:** "The frontend build failed with an npm error."

### 2.4 Configuration Update

* **Route Intent:** `Config`
* **Trigger Keywords:** `env var`, `settings`
* **Target Workflow:** `skills/config_update.md`
* **Description:** Safe updates to configuration files or environment variables. Updates `01_PROJECT_CONTEXT.md` or `.env` files.
* **Usage Example:** "Update the API key in the environment variables."

---

## 🟢 Priority 3: Feature & Changes

Routes for implementing new code or modifying existing code.

### 3.1 New Feature Delivery

* **Route Intent:** `New Feature`
* **Trigger Keywords:** `add`, `create`, `implement`, `feature`
* **Target Workflow:** `workflows/feature_delivery.md` (and stack-specific subflows)
* **Description:** End-to-end flow for delivering features. Includes planning, implementation, testing, and PR creation.
* **Usage Example:** "Implement a new user login endpoint."

### 3.2 Refactoring

* **Route Intent:** `Refactor`
* **Trigger Keywords:** `refactor`, `clean up`, `optimize`
* **Target Workflow:** `workflows/feature_delivery.md`
* **Description:** Uses the Feature Delivery workflow but focuses on code structure improvements without changing behavior.
* **Usage Example:** "Refactor the authentication logic."

---

## 🔵 Priority 4: Testing & Quality

Routes for ensuring code quality and correctness.

### 4.1 Test Failure

* **Route Intent:** `Test Fail`
* **Trigger Keywords:** `test`, `fail`, `pytest`, `junit`
* **Target Workflow:** `skills/pytest_debugging.md` (Python), `workflows/java_dev_loop.md` (Java), etc.
* **Description:** Iteratively runs tests and fixes failures. Analyzes assertions and traceback.
* **Usage Example:** "The auth tests are failing."

### 4.2 Linting & Style

* **Route Intent:** `Linting`
* **Trigger Keywords:** `lint`, `format`, `style`
* **Target Workflow:** `skills/python_linting.md`, `skills/flutter_linting.md`
* **Description:** Runs code formatters (ruff, black, prettier) and linters. Fixes auto-fixable issues.
* **Usage Example:** "Fix the linting errors in this file."

---

## 🟣 Operations & Security

Advanced capabilities inferred from available workflows.

### 5.1 Deployment

* **Route Intent:** `Deploy`
* **Target Workflow:** `workflows/deploy_and_migrate.md`
* **Description:** Orchestrates deployment validation, migration application, and service restart.
* **Usage Example:** "Deploy the current branch to staging."

### 5.2 Security Incident

* **Route Intent:** `Security`
* **Target Workflow:** `workflows/security_incident.md`
* **Description:** Specialized response for security breaches or vulnerability reports.
* **Usage Example:** "We have a potential SQL injection vulnerability."

### 5.3 Performance Profiling

* **Route Intent:** `Performance`
* **Target Workflow:** `workflows/performance_profiling.md`
* **Description:** Runs profiling tools to identify bottlenecks in the code.
* **Usage Example:** "Profile the API for performance bottlenecks."

---

## Developer Reference

* **Source of Truth:** `agent/ROUTING_RULES.md`
* **Workflow Directory:** `agent/workflows/`
* **Skills Directory:** `agent/skills/`
