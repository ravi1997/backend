# Docker Development Setup

This project is set up to run with Docker and Docker Compose. This ensures a consistent environment for all developers.

## Prerequisites

- Docker and Docker Compose installed on your machine.
- (Optional) `make` installed for quick commands.

## Getting Started

1. **Environment Variables**:
   A `.env` file has been created from `.env.example`. You can customize it if needed.

2. **Start Development Server**:
   Run the following command to start the backend with hot-reloading enabled:

   ```bash
   make up-dev
   ```

   Or without `make`:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

3. **Install LLM Models (Ollama)**:
   Once the services are up, you need to pull the required models:

   ```bash
   make pull-models
   ```

4. **Accessing the App**:
   The backend will be available at `http://localhost:5000`.

## Common Commands

| Command | Description |
|---------|-------------|
| `make build` | Build the Docker images |
| `make up-dev` | Start dev environment (hot-reloading) |
| `make down` | Stop all services |
| `make logs` | View real-time logs |
| `make shell` | Open a shell inside the backend container |
| `make test` | Run tests inside the container |
| `make pull-models` | Pull the default LLM model (llama3) |
| `make clean` | Stop services and remove volumes (Wipes DB!) |

## Troubleshooting

- **Database Connection**: If the backend fails to connect to MongoDB, ensure the `db` service is healthy (`docker compose ps`).
- **Permissions**: If you encounter permission issues with `uploads/` or `logs/` folders, you may need to adjust their owners or run with `sudo` (not recommended).
- **Network Issues**: The setup uses an internal network `app_net`. If you have conflicting networks, you may need to prune them: `docker network prune`.
