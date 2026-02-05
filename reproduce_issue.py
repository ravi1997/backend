
import sys
from typing import List, Dict, Any

def check_model_loaded(model_name: str, model_names: List[str]) -> bool:
    """Simulate the logic in OllamaService._perform_health_check"""
    return model_name in model_names

def test_reproduction():
    default_model = "llama3"
    model_names_from_api = ["llama3:latest"]
    
    loaded = check_model_loaded(default_model, model_names_from_api)
    
    print(f"Default model: {default_model}")
    print(f"Models from API: {model_names_from_api}")
    print(f"Is loaded: {loaded}")
    
    if not loaded:
        print("REPRODUCED: Model 'llama3' is reported as not loaded even though 'llama3:latest' exists.")
    else:
        print("NOT REPRODUCED: Model is reported as loaded.")

if __name__ == "__main__":
    test_reproduction()
