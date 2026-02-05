# Bug Fix: Ollama Model Loading Health Check Failure

## Issue

The Ollama health check reports a "Degraded" status because it fails to find the default model (e.g., `llama3`) in the list of available models. This happens because Ollama often appends `:latest` to the model name (e.g., `llama3:latest`), but the health check performs an exact string match.

## Root Cause

In `app/services/ollama_service.py`, the code uses `default_model in model_names`, which is an exact match. If `default_model` is `llama3` and `model_names` contains `llama3:latest`, it returns `False`.

## Plan

1. **Modify `OllamaService._perform_health_check`**: Update the check to handle cases where the model name in Ollama includes a tag (like `:latest`) while the configured name does not.
2. **Update `Makefile`**: Add `nomic-embed-text` to `pull-models` to ensure the default embedding model is also available.
3. **Verify**: Run the reproduction script (updated to reflect the fix) and check the actual health status in the container if possible.

## Technical Details

Update `app/services/ollama_service.py`:

```python
def is_model_available(target, available_models):
    if target in available_models:
        return True
    if ":" not in target:
        if f"{target}:latest" in available_models:
            return True
    return False
```

Apply this logic to both `default_model` and `embedding_model` checks.
