# LLM Integration Plan - AI Form Builder

This plan outlines the implementation of an offline AI-powered form generation feature for the backend.

## Overview

The goal is to provide a local LLM capability using Ollama that can generate valid `IForm` JSON structures from natural language prompts.

## Infrastructure Updates

### 1. Docker Environment (`docker-compose.yml`)

Add an `ollama` service to the existing setup:

```yaml
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - app_net

volumes:
  ollama_data:
```

### 2. Environment Variables (`.env`)

```env
LLM_PROVIDER=ollama
LLM_API_URL=http://ollama:11434/v1
LLM_MODEL=llama3
```

---

## Milestone 1: Core LLM Infrastructure

### Tasks

- [ ] **AI Service**: Create `app/services/ai_service.py` to handle chat completion requests.
- [ ] **System Prompt**: Define the schema and constraints in a centralized location.
- [ ] **Generate Endpoint**: Implement `POST /api/ai/generate` in `app/routes/ai_routes.py`.
- [ ] **JWT Protection**: Secure the endpoint with existing authentication logic.

---

## Milestone 2: Schema Processing & Verification

### Tasks

- [ ] **JSON Extractor**: Implement logic to strip possible markdown blocks (e.g., ` ```json ... ``` `).
- [ ] **UUID Injection**: Replace placeholders with real UUID v4 strings for `id` fields.
- [ ] **Index Normalization**: Reset `order_index` for sections and questions to ensure they are sequential.
- [ ] **Field Type Enforcement**: Validate that `field_type` belongs to the supported list.

---

## Milestone 3: Advanced Features

### Tasks

- [ ] **Logic Generation**: Update prompt to support `visibility_rules`.
- [ ] **Incremental Updates**: Update endpoint to accept `current_form` for context-aware generations.

---

## Offline Strategy

1. **Setup**: The user runs `docker compose up -d`.
2. **Model Download**: One-time execution of `docker exec -it ollama ollama pull llama3`.
3. **Pure Offline**: From this point on, all LLM inference happens locally within the Docker network.

## Execution Order

1. Update `docker-compose.yml`.
2. Add environment variables.
3. Implement `AIService`.
4. Implement `AIRoute`.
5. Add post-processing logic.
