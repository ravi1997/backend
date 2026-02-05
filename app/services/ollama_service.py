"""
Ollama Integration Service

Provides unified interface for Ollama LLM operations including:
- Chat completions
- Embedding generation
- Model management
- Health monitoring

This service is a dependency for all M2 AI features:
- T-M2-02: NLP Search Enhancement
- T-M2-03: Automated Summarization
- T-M2-04: Predictive Anomaly Detection
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
from flask import current_app, request
from typing import List, Dict, Any, Optional, Generator, Union
from queue import Queue, Empty, Full


class OllamaService:
    """Service for interacting with Ollama LLM API."""
    
    BASE_TIMEOUT = 120  # seconds
    HEALTH_CACHE_TTL = 60  # seconds (1 minute)
    PERIODIC_CHECK_INTERVAL = 300  # seconds (5 minutes)
    LATENCY_WARNING_THRESHOLD = 5000  # milliseconds (5 seconds)
    
    # Default fallback models to try when primary model fails
    FALLBACK_MODELS = ["llama3.1", "mistral:7b", "gemma:2b"]
    
    # Class-level cache for health status
    _health_cache: Dict[str, Any] = {
        "data": None,
        "timestamp": None
    }
    _cache_lock = threading.Lock()
    _scheduler_thread = None
    _scheduler_running = False
    
    # Connection pool
    _connection_pool: Optional[Queue] = None
    _pool_lock = threading.Lock()
    _max_pool_size = 5
    _pool_timeout = 30
    _connection_timeout = 10
    
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
    def _initialize_pool(cls) -> None:
        """Initialize the connection pool if not already initialized."""
        with cls._pool_lock:
            if cls._connection_pool is None:
                cls._max_pool_size = current_app.config.get("OLLAMA_POOL_SIZE", 5)
                cls._pool_timeout = current_app.config.get("OLLAMA_POOL_TIMEOUT", 30)
                cls._connection_timeout = current_app.config.get("OLLAMA_CONNECTION_TIMEOUT", 10)
                cls._connection_pool = Queue(maxsize=cls._max_pool_size)
                current_app.logger.info(f"Ollama connection pool initialized with max size: {cls._max_pool_size}")
    
    @classmethod
    def _get_connection(cls) -> requests.Session:
        """
        Get a connection from the pool or create a new one.
        
        Returns:
            requests.Session object for HTTP requests
            
        Raises:
            TimeoutError: If unable to get connection from pool within timeout
        """
        cls._initialize_pool()
        
        try:
            # Try to get an existing connection from the pool
            session = cls._connection_pool.get(block=True, timeout=cls._pool_timeout)
            current_app.logger.debug("Retrieved connection from pool")
            return session
        except Empty:
            # Pool is empty, create a new connection
            current_app.logger.debug("Creating new connection")
            session = requests.Session()
            # Set connection timeout
            session.timeout = cls._connection_timeout
            return session
    
    @classmethod
    def _return_connection(cls, session: requests.Session) -> None:
        """
        Return a connection to the pool.
        
        Args:
            session: The requests.Session object to return to the pool
        """
        cls._initialize_pool()
        
        try:
            # Try to return the connection to the pool
            cls._connection_pool.put_nowait(session)
            current_app.logger.debug("Returned connection to pool")
        except Full:
            # Pool is full, close the connection
            current_app.logger.debug("Pool full, closing connection")
            session.close()
    
    @classmethod
    def _close_pool(cls) -> None:
        """Close all connections in the pool and clear the pool."""
        with cls._pool_lock:
            if cls._connection_pool is not None:
                while not cls._connection_pool.empty():
                    try:
                        session = cls._connection_pool.get_nowait()
                        session.close()
                    except Empty:
                        break
                cls._connection_pool = None
                current_app.logger.info("Ollama connection pool closed")
    
    @classmethod
    def chat(cls, prompt: str, system_prompt: Optional[str] = None,
             model: Optional[str] = None, temperature: float = 0.7,
             stream: bool = False, fallback_models: Optional[List[str]] = None) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Send a chat message to Ollama and get response.
        
        Args:
            prompt: User message
            system_prompt: System instruction (optional)
            model: Model to use (defaults to config)
            temperature: Response creativity (0-1)
            stream: Whether to stream response (returns generator if True)
            fallback_models: Optional list of model names to try if primary fails
            
        Returns:
            If stream=False: Dict with 'response', 'model', 'timing' keys
            If stream=True: Generator yielding dicts with 'content', 'done', 'model' keys
        """
        if stream:
            return cls.chat_stream(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=temperature
            )
        
        base_url = cls.get_base_url()
        model = model or cls.get_default_model()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        start_time = time.time()
        session = None
        
        try:
            session = cls._get_connection()
            try:
                response = session.post(
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
        finally:
            if session:
                cls._return_connection(session)
    
    @classmethod
    def chat_stream(cls, prompt: str, system_prompt: Optional[str] = None,
                    model: Optional[str] = None, temperature: float = 0.7) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a chat response from Ollama, yielding chunks as they arrive.
        
        Args:
            prompt: User message
            system_prompt: System instruction (optional)
            model: Model to use (defaults to config)
            temperature: Response creativity (0-1)
            
        Yields:
            Dict with 'content' (partial text), 'done' (bool), 'model' (str) keys
            Final chunk has 'done': True and includes 'model_used' key
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
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }
        
        start_time = time.time()
        session = None
        
        try:
            session = cls._get_connection()
            try:
                response = session.post(
                    f"{base_url}/api/chat",
                    json=payload,
                    timeout=cls.BASE_TIMEOUT,
                    stream=True
                )
                response.raise_for_status()
                
                # Process streaming response line by line
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            message = chunk.get("message", {})
                            content = message.get("content", "")
                            done = chunk.get("done", False)
                            
                            if content or done:
                                yield {
                                    "content": content,
                                    "done": done,
                                    "model": model
                                }
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue
                
                # Send final metadata chunk
                elapsed = time.time() - start_time
                yield {
                    "content": "",
                    "done": True,
                    "model": model,
                    "model_used": model,
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
        finally:
            if session:
                cls._return_connection(session)
    
    @classmethod
    def chat_with_fallback(cls, prompt: str, system_prompt: Optional[str] = None,
                           model: Optional[str] = None, temperature: float = 0.7,
                           stream: bool = False, fallback_models: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send a chat message to Ollama with automatic fallback to backup models.
        
        Tries the primary model first, then iterates through fallback models on failure.
        Returns response from the first successful model.
        
        Args:
            prompt: User message
            system_prompt: System instruction (optional)
            model: Primary model to use (defaults to config)
            temperature: Response creativity (0-1)
            stream: Whether to stream response
            fallback_models: Optional list of model names to try if primary fails
                            (defaults to FALLBACK_MODELS class constant)
            
        Returns:
            Dict with 'response', 'model', 'timing', 'fallback_used' keys
        """
        primary_model = model or cls.get_default_model()
        fallback_list = fallback_models if fallback_models is not None else cls.FALLBACK_MODELS
        
        # Try primary model first
        try:
            result = cls.chat(
                prompt=prompt,
                system_prompt=system_prompt,
                model=primary_model,
                temperature=temperature,
                stream=stream
            )
            result["fallback_used"] = False
            result["fallback_model"] = None
            current_app.logger.info(f"Ollama chat: Successfully used primary model '{primary_model}'")
            return result
        except (ConnectionError, TimeoutError, requests.exceptions.RequestException) as e:
            current_app.logger.warning(f"Ollama chat: Primary model '{primary_model}' failed: {str(e)}")
        
        # Try each fallback model in order
        for fallback_model in fallback_list:
            try:
                result = cls.chat(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=fallback_model,
                    temperature=temperature,
                    stream=stream
                )
                result["fallback_used"] = True
                result["fallback_model"] = fallback_model
                current_app.logger.info(f"Ollama chat: Successfully used fallback model '{fallback_model}' after primary failure")
                return result
            except (ConnectionError, TimeoutError, requests.exceptions.RequestException) as e:
                current_app.logger.warning(f"Ollama chat: Fallback model '{fallback_model}' failed: {str(e)}")
                continue
        
        # All models failed
        error_msg = f"All Ollama models failed (primary: '{primary_model}', fallbacks: {fallback_list})"
        current_app.logger.error(error_msg)
        raise ConnectionError(error_msg)
    
    @classmethod
    def chat_stream_with_fallback(cls, prompt: str, system_prompt: Optional[str] = None,
                                   model: Optional[str] = None, temperature: float = 0.7,
                                   fallback_models: Optional[List[str]] = None) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a chat response from Ollama with automatic fallback to backup models.
        
        Tries the primary model first, then iterates through fallback models on failure.
        Yields response chunks from the first successful model.
        
        Args:
            prompt: User message
            system_prompt: System instruction (optional)
            model: Primary model to use (defaults to config)
            temperature: Response creativity (0-1)
            fallback_models: Optional list of model names to try if primary fails
                            (defaults to FALLBACK_MODELS class constant)
            
        Yields:
            Dict with 'content' (partial text), 'done' (bool), 'model' (str) keys
            Final chunk has 'done': True and includes 'model_used' and 'fallback_used' keys
        """
        primary_model = model or cls.get_default_model()
        fallback_list = fallback_models if fallback_models is not None else cls.FALLBACK_MODELS
        
        # Try primary model first
        try:
            start_time = time.time()
            for chunk in cls.chat_stream(
                prompt=prompt,
                system_prompt=system_prompt,
                model=primary_model,
                temperature=temperature
            ):
                # Add fallback metadata to the final chunk
                if chunk.get("done"):
                    chunk["fallback_used"] = False
                    chunk["fallback_model"] = None
                    chunk["model_used"] = primary_model
                yield chunk
            current_app.logger.info(f"Ollama chat stream: Successfully used primary model '{primary_model}'")
            return
        except (ConnectionError, TimeoutError, requests.exceptions.RequestException) as e:
            current_app.logger.warning(f"Ollama chat stream: Primary model '{primary_model}' failed: {str(e)}")
        
        # Try each fallback model in order
        for fallback_model in fallback_list:
            try:
                start_time = time.time()
                for chunk in cls.chat_stream(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=fallback_model,
                    temperature=temperature
                ):
                    # Add fallback metadata to the final chunk
                    if chunk.get("done"):
                        chunk["fallback_used"] = True
                        chunk["fallback_model"] = fallback_model
                        chunk["model_used"] = fallback_model
                    yield chunk
                current_app.logger.info(f"Ollama chat stream: Successfully used fallback model '{fallback_model}' after primary failure")
                return
            except (ConnectionError, TimeoutError, requests.exceptions.RequestException) as e:
                current_app.logger.warning(f"Ollama chat stream: Fallback model '{fallback_model}' failed: {str(e)}")
                continue
        
        # All models failed
        error_msg = f"All Ollama models failed for streaming (primary: '{primary_model}', fallbacks: {fallback_list})"
        current_app.logger.error(error_msg)
        raise ConnectionError(error_msg)
    
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
        
        session = None
        try:
            session = cls._get_connection()
            try:
                response = session.post(
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
        finally:
            if session:
                cls._return_connection(session)
    
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
        
        session = None
        try:
            session = cls._get_connection()
            try:
                response = session.post(
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
        finally:
            if session:
                cls._return_connection(session)
    
    @classmethod
    def list_models(cls) -> List[Dict[str, Any]]:
        """
        List available Ollama models.
        
        Returns:
            List of model info dictionaries
        """
        base_url = cls.get_base_url()
        session = None
        
        try:
            session = cls._get_connection()
            try:
                response = session.get(
                    f"{base_url}/api/tags",
                    timeout=10
                )
                response.raise_for_status()
                result = response.json()
                
                return result.get("models", [])
            except requests.exceptions.RequestException:
                return []
        finally:
            if session:
                cls._return_connection(session)
    
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
    def _check_model_loaded(cls, model_name: str) -> bool:
        """
        Check if a specific model is loaded in Ollama.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model is loaded, False otherwise
        """
        session = None
        try:
            session = cls._get_connection()
            try:
                base_url = cls.get_base_url()
                response = session.post(
                    f"{base_url}/api/show",
                    json={"name": model_name},
                    timeout=10
                )
                return response.status_code == 200
            except Exception:
                return False
        finally:
            if session:
                cls._return_connection(session)
    
    @classmethod
    def _measure_latency(cls) -> int:
        """
        Measure response latency by making a simple API call.
        
        Returns:
            Latency in milliseconds
        """
        session = None
        try:
            session = cls._get_connection()
            try:
                start_time = time.time()
                base_url = cls.get_base_url()
                
                # Use a simple tags call to measure latency
                response = session.get(
                    f"{base_url}/api/tags",
                    timeout=10
                )
                response.raise_for_status()
                
                elapsed = time.time() - start_time
                return int(elapsed * 1000)
            except Exception:
                return -1
        finally:
            if session:
                cls._return_connection(session)
    
    @classmethod
    def _perform_health_check(cls) -> Dict[str, Any]:
        """
        Perform actual health check on Ollama service (internal method).
        
        Returns:
            Dict with health status details
        """
        session = None
        try:
            session = cls._get_connection()
            try:
                base_url = cls.get_base_url()
                default_model = cls.get_default_model()
                embedding_model = cls.get_embedding_model()
                
                # Check server connection and list models
                start_time = time.time()
                response = session.get(
                    f"{base_url}/api/tags",
                    timeout=10
                )
                response.raise_for_status()
                result = response.json()
                models = result.get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Measure latency
                latency_ms = cls._measure_latency()
                
                # Check model loading status
                def is_model_loaded(check_model, loaded_names):
                    if check_model in loaded_names:
                        return True
                    # If model doesn't have a tag, check for :latest
                    if ":" not in check_model:
                        if f"{check_model}:latest" in loaded_names:
                            return True
                    return False

                default_model_loaded = is_model_loaded(default_model, model_names)
                embedding_model_loaded = is_model_loaded(embedding_model, model_names)
                
                # Determine overall status
                if latency_ms == -1:
                    status = "unavailable"
                elif latency_ms > cls.LATENCY_WARNING_THRESHOLD:
                    status = "degraded"
                elif not default_model_loaded:
                    status = "degraded"
                else:
                    status = "healthy"
                
                return {
                    "status": status,
                    "available": True,
                    "models": model_names,
                    "default_model": default_model,
                    "embedding_model": embedding_model,
                    "default_model_loaded": default_model_loaded,
                    "embedding_model_loaded": embedding_model_loaded,
                    "latency_ms": latency_ms
                }
            except requests.exceptions.ConnectionError:
                current_app.logger.error("Ollama health check: Connection failed")
                return {
                    "status": "unavailable",
                    "available": False,
                    "models": [],
                    "default_model": cls.get_default_model(),
                    "embedding_model": cls.get_embedding_model(),
                    "default_model_loaded": False,
                    "embedding_model_loaded": False,
                    "latency_ms": -1,
                    "error": "Ollama service is not reachable"
                }
            except requests.exceptions.Timeout:
                current_app.logger.error("Ollama health check: Timeout")
                return {
                    "status": "unavailable",
                    "available": False,
                    "models": [],
                    "default_model": cls.get_default_model(),
                    "embedding_model": cls.get_embedding_model(),
                    "default_model_loaded": False,
                    "embedding_model_loaded": False,
                    "latency_ms": -1,
                    "error": "Ollama service timed out"
                }
            except Exception as e:
                current_app.logger.error(f"Ollama health check error: {str(e)}")
                return {
                    "status": "unavailable",
                    "available": False,
                    "models": [],
                    "default_model": cls.get_default_model(),
                    "embedding_model": cls.get_embedding_model(),
                    "default_model_loaded": False,
                    "embedding_model_loaded": False,
                    "latency_ms": -1,
                    "error": str(e)
                }
        finally:
            if session:
                cls._return_connection(session)
    
    @classmethod
    def health_check(cls, use_cache: bool = True) -> Dict[str, Any]:
        """
        Perform health check on Ollama service with caching support.
        
        Args:
            use_cache: Whether to use cached results if available
            
        Returns:
            Dict with 'status', 'models', 'error' keys
        """
        with cls._cache_lock:
            now = datetime.utcnow()
            
            # Check if we have a valid cached result
            if use_cache and cls._health_cache["data"] is not None:
                cache_time = cls._health_cache["timestamp"]
                if cache_time and (now - cache_time).total_seconds() < cls.HEALTH_CACHE_TTL:
                    return cls._health_cache["data"]
            
            # Perform actual health check
            result = cls._perform_health_check()
            
            # Update cache
            cls._health_cache["data"] = result
            cls._health_cache["timestamp"] = now
            
            return result
    
    @classmethod
    def _periodic_health_check(cls, app):
        """
        Background thread for periodic health checks.
        Logs warnings if issues are detected.
        """
        while cls._scheduler_running:
            try:
                with app.app_context():
                    # Perform health check without using cache
                    result = cls.health_check(use_cache=False)
                    
                    # Log warnings for issues
                    if result["status"] == "unavailable":
                        current_app.logger.warning(
                            f"Ollama health check: Service unavailable - {result.get('error', 'Unknown error')}"
                        )
                    elif result["status"] == "degraded":
                        warnings = []
                        if not result.get("default_model_loaded", False):
                            warnings.append(f"Default model '{result['default_model']}' is not loaded")
                        if result.get("latency_ms", -1) > cls.LATENCY_WARNING_THRESHOLD:
                            warnings.append(f"Latency {result['latency_ms']}ms exceeds threshold of {cls.LATENCY_WARNING_THRESHOLD}ms")
                        
                        if warnings:
                            current_app.logger.warning(
                                f"Ollama health check: Degraded status - {'; '.join(warnings)}"
                            )
            except Exception as e:
                # Use app.logger as fallback if current_app is not available
                app.logger.error(f"Ollama periodic health check error: {str(e)}")
            
            # Wait for next check
            time.sleep(cls.PERIODIC_CHECK_INTERVAL)
    
    @classmethod
    def start_periodic_health_checks(cls, app):
        """
        Start the periodic health check background thread.
        """
        if not cls._scheduler_running:
            cls._scheduler_running = True
            cls._scheduler_thread = threading.Thread(
                target=cls._periodic_health_check,
                args=(app,),
                daemon=True,
                name="OllamaHealthCheckScheduler"
            )
            cls._scheduler_thread.start()
            app.logger.info("Ollama periodic health checks started")
    
    @classmethod
    def stop_periodic_health_checks(cls):
        """
        Stop the periodic health check background thread.
        """
        cls._scheduler_running = False
        if cls._scheduler_thread:
            cls._scheduler_thread.join(timeout=5)
