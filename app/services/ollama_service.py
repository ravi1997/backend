"""
Ollama Integration Service

Provides unified interface for Ollama LLM operations including:
- Chat completions
- Embedding generation
- Model management

This service is a dependency for all M2 AI features:
- T-M2-02: NLP Search Enhancement
- T-M2-03: Automated Summarization
- T-M2-04: Predictive Anomaly Detection
"""

import requests
import json
import time
from flask import current_app, request
from typing import List, Dict, Any, Optional


class OllamaService:
    """Service for interacting with Ollama LLM API."""
    
    BASE_TIMEOUT = 120  # seconds
    
    @classmethod
    def get_base_url(cls) -> str:
        """Get Ollama API base URL from config."""
        return current_app.config.get("OLLAMA_API_URL", "http://localhost:11434")
    
    @classmethod
    def get_default_model(cls) -> str:
        """Get default Ollama model from config."""
        return current_app.config.get("OLLAMA_MODEL", "llama3.2")
    
    @classmethod
    def get_embedding_model(cls) -> str:
        """Get embedding model for semantic search."""
        return current_app.config.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    @classmethod
    def chat(cls, prompt: str, system_prompt: Optional[str] = None, 
             model: Optional[str] = None, temperature: float = 0.7,
             stream: bool = False) -> Dict[str, Any]:
        """
        Send a chat message to Ollama and get response.
        
        Args:
            prompt: User message
            system_prompt: System instruction (optional)
            model: Model to use (defaults to config)
            temperature: Response creativity (0-1)
            stream: Whether to stream response
            
        Returns:
            Dict with 'response', 'model', 'timing' keys
        """
        base_url = cls.get_base_url()
        model = model or cls.get_default_model()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json=payload,
                timeout=cls.BASE_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            
            elapsed = time.time() - start_time
            
            return {
                "response": result.get("message", {}).get("content", ""),
                "model": model,
                "timing_ms": int(elapsed * 1000)
            }
            
        except requests.exceptions.ConnectionError:
            current_app.logger.error("Ollama connection failed - ensure Ollama is running")
            raise ConnectionError("Ollama service is not available. Please ensure Ollama is running.")
        except requests.exceptions.Timeout:
            current_app.logger.error("Ollama request timed out")
            raise TimeoutError("Ollama request timed out")
        except requests.exceptions.HTTPError as e:
            current_app.logger.error(f"Ollama HTTP error: {str(e)}")
            raise
    
    @classmethod
    def generate_embedding(cls, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generate semantic embedding for text using Ollama embeddings API.
        
        Args:
            text: Text to embed
            model: Embedding model (defaults to config)
            
        Returns:
            List of embedding floats
        """
        base_url = cls.get_base_url()
        model = model or cls.get_embedding_model()
        
        payload = {
            "model": model,
            "prompt": text
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/embeddings",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            return result.get("embedding", [])
            
        except requests.exceptions.ConnectionError:
            current_app.logger.error("Ollama embeddings connection failed")
            raise ConnectionError("Ollama embeddings service is not available")
        except requests.exceptions.HTTPError as e:
            current_app.logger.error(f"Ollama embeddings HTTP error: {str(e)}")
            raise
    
    @classmethod
    def generate_completion(cls, prompt: str, model: Optional[str] = None,
                          temperature: float = 0.7, system_prompt: Optional[str] = None) -> str:
        """
        Generate a text completion (non-chat format).
        
        Args:
            prompt: Generation prompt
            model: Model to use
            temperature: Response creativity
            system_prompt: System instruction
            
        Returns:
            Generated text string
        """
        base_url = cls.get_base_url()
        model = model or cls.get_default_model()
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                f"{base_url}/api/generate",
                json=payload,
                timeout=cls.BASE_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            
            return result.get("response", "")
            
        except requests.exceptions.HTTPError as e:
            current_app.logger.error(f"Ollama generate error: {str(e)}")
            raise
    
    @classmethod
    def list_models(cls) -> List[Dict[str, Any]]:
        """
        List available Ollama models.
        
        Returns:
            List of model info dictionaries
        """
        base_url = cls.get_base_url()
        
        try:
            response = requests.get(
                f"{base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            return result.get("models", [])
            
        except requests.exceptions.RequestException:
            return []
    
    @classmethod
    def is_available(cls) -> bool:
        """
        Check if Ollama service is reachable.
        
        Returns:
            True if Ollama is available
        """
        try:
            models = cls.list_models()
            return len(models) > 0
        except Exception:
            return False
    
    @classmethod
    def health_check(cls) -> Dict[str, Any]:
        """
        Perform health check on Ollama service.
        
        Returns:
            Dict with 'status', 'models', 'error' keys
        """
        try:
            models = cls.list_models()
            model_names = [m.get("name", "") for m in models]
            
            return {
                "status": "healthy",
                "available": True,
                "models": model_names,
                "default_model": cls.get_default_model(),
                "embedding_model": cls.get_embedding_model()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "available": False,
                "error": str(e),
                "models": [],
                "default_model": cls.get_default_model()
            }
