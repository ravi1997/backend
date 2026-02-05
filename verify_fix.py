
import sys
from typing import List, Dict, Any

def is_model_loaded(check_model, loaded_names):
    if check_model in loaded_names:
        return True
    # If model doesn't have a tag, check for :latest
    if ":" not in check_model:
        if f"{check_model}:latest" in loaded_names:
            return True
    return False

def test_verification():
    # Case 1: Exact match
    assert is_model_loaded("llama3", ["llama3"]) == True
    
    # Case 2: Implicit :latest match (The reported issue)
    assert is_model_loaded("llama3", ["llama3:latest"]) == True
    
    # Case 3: Tagged match
    assert is_model_loaded("llama3:latest", ["llama3:latest"]) == True
    
    # Case 4: Mis-match
    assert is_model_loaded("llama3", ["mistral"]) == False
    
    print("VERIFICATION SUCCESS: All model loading scenarios passed.")

if __name__ == "__main__":
    test_verification()
