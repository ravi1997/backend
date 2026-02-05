# KI-20260205-ollama-model-mismatch: Ollama Health Check Degraded Status

## Symptoms

The backend logs show the following warning:
`WARNING:app:Ollama health check: Degraded status - Default model 'llama3' is not loaded`
even after running `make pull-models` and confirming that the model exists in `ollama list`.

## Root Cause

The `OllamaService` performed an exact string match between the configured model name (e.g., `llama3`) and the names returned by the Ollama API (e.g., `llama3:latest`). Ollama often appends `:latest` to models pulled without a specific tag.

## Fix / Mitigation

The health check logic in `app/services/ollama_service.py` was updated to handle implicit `:latest` tags. If an exact match is not found, the service now checks if the model name with `:latest` appended exists in the available models.

Additionally, the `Makefile` was updated to ensure all required models (including embedding models) are pulled during the `pull-models` step.

## Verification

1. Run `make pull-models`.
2. check logs: `docker compose logs backend`.
3. The health check should now report "healthy" if the model exists even with a `:latest` tag.

## See Also

- `app/services/ollama_service.py`
- `Makefile`
- `plans/BugFixes/FIX-OllamaModelLoading.md`
