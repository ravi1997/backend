.PHONY: build up up-dev down restart restart-dev logs shell test clean help

# Default target
all: help

build: ## Build the docker image
	docker compose build

up: ## Start the services in production mode
	docker compose up -d

up-dev: ## Start the services in development mode with hot-reloading
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

down: ## Stop all services
	docker compose down

restart: down up ## Restart all services

restart-dev: down up-dev ## Restart all services in development mode

logs: ## View logs from all services
	docker compose logs -f backend

shell: ## Enter the backend container shell
	docker compose exec backend bash

test: ## Run tests inside the container
	docker compose exec backend pytest

pull-models: ## Pull Ollama models
	docker compose exec ollama ollama pull llama3
	docker compose exec ollama ollama pull nomic-embed-text

clean: ## Remove all containers and volumes
	docker compose down -v

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
