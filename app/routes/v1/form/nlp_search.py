"""
NLP Search Routes

Natural language search endpoints for form responses.
Provides semantic search, sentiment filtering, and query parsing.

Task: T-M2-02 - NLP Search Enhancement
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from typing import Dict, Any
import time

from app.models.Form import FormResponse
from app.services.nlp_service import NLPSearchService
from app.services.ollama_service import OllamaService
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.v1.form.helper import get_current_user
from app.utils.redis_client import redis_client


nlp_search_bp = Blueprint('nlp_search', __name__, url_prefix='/api/v1/ai/forms')


@nlp_search_bp.route('/<form_id>/nlp-search', methods=['POST'])
@jwt_required()
def nlp_search(form_id: str):
    """
    Natural language search across form responses.
    
    Request Body:
        {
            "query": "Show me all users who were unhappy with delivery",
            "options": {
                "max_results": 50,
                "include_sentiment": true,
                "semantic_search": true,
                "cache_results": true
            }
        }
    
    Returns:
        {
            "query": "Show me all users who were unhappy with delivery",
            "parsed_intent": {
                "sentiment_filter": "negative",
                "topic": "delivery",
                "entities": ["delivery", "users"]
            },
            "results_count": 15,
            "results": [...],
            "processing_time_ms": 245,
            "cached": false
        }
    """
    user = get_current_user()
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({"error": "Query is required"}), 400
    
    query = data['query']
    options = data.get('options', {})
    
    max_results = options.get('max_results', 50)
    include_sentiment = options.get('include_sentiment', True)
    use_semantic = options.get('semantic_search', True)
    use_cache = options.get('cache_results', True)
    
    start_time = time.time()
    
    # Check cache first
    cache_key = NLPSearchService.generate_cache_key(form_id, query, "nlp")
    if use_cache:
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return jsonify({
                **cached_result,
                "cached": True
            })
    
    # Parse the query
    parsed = NLPSearchService.parse_query(query)
    entities = NLPSearchService.extract_entities(query)
    parsed['entities'] = entities
    
    # Build MongoDB query
    mongo_query = NLPSearchService.build_mongo_query(parsed)
    mongo_query['form_id'] = form_id
    
    # Fetch responses (simplified - would need proper pagination in production)
    responses = FormResponse.objects(**mongo_query).limit(max_results * 2)
    
    # Prepare documents for search
    documents = []
    for resp in responses:
        resp_data = {
            "response_id": str(resp.id),
            "data": resp.data,
            "submitted_at": resp.submitted_at.isoformat() if resp.submitted_at else None
        }
        
        # Include sentiment if available
        if include_sentiment and hasattr(resp, 'ai_results') and resp.ai_results:
            resp_data["sentiment"] = resp.ai_results.get('sentiment', {})
        
        documents.append(resp_data)
    
    # Perform search
    if use_semantic:
        try:
            results = NLPSearchService.semantic_search(
                query, documents, 
                similarity_threshold=0.7,
                max_results=max_results
            )
        except (ConnectionError, TimeoutError):
            # Fallback to keyword search
            results = NLPSearchService._keyword_search(query, documents, max_results)
    else:
        results = NLPSearchService._keyword_search(query, documents, max_results)
    
    processing_time = int((time.time() - start_time) * 1000)
    
    # Build response
    response = {
        "query": query,
        "parsed_intent": parsed,
        "results_count": len(results),
        "results": results[:max_results],
        "processing_time_ms": processing_time,
        "cached": False
    }
    
    # Cache results (1 hour TTL)
    if use_cache:
        redis_client.set(cache_key, response, ttl=3600)
        response["cached"] = False  # Just cached
    
    return jsonify(response)


@nlp_search_bp.route('/<form_id>/semantic-search', methods=['POST'])
@jwt_required()
def semantic_search(form_id: str):
    """
    Pure semantic search using Ollama embeddings.
    
    Request Body:
        {
            "query": "What are the main complaints about product quality?",
            "similarity_threshold": 0.7,
            "max_results": 20
        }
    
    Returns:
        {
            "query": "What are the main complaints about product quality?",
            "embedding_model": "nomic-embed-text",
            "results_count": 8,
            "results": [...]
        }
    """
    user = get_current_user()
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({"error": "Query is required"}), 400
    
    query = data['query']
    similarity_threshold = data.get('similarity_threshold', 0.7)
    max_results = data.get('max_results', 20)
    
    # Fetch('max_results', all responses for this form
    responses = FormResponse.objects(form_id=form_id).limit(500)
    
    # Prepare documents
    documents = [
        {
            "response_id": str(resp.id),
            "text": str(resp.data),
            "submitted_at": resp.submitted_at.isoformat() if resp.submitted_at else None
        }
        for resp in responses
    ]
    
    # Perform semantic search
    try:
        results = NLPSearchService.semantic_search(
            query, documents,
            similarity_threshold=similar_threshold,
            max_results=max_results
        )
        
        return jsonify({
            "query": query,
            "embedding_model": OllamaService.get_embedding_model(),
            "results_count": len(results),
            "results": results
        })
        
    except (ConnectionError, TimeoutError):
        return jsonify({
            "error": "Ollama service is not available",
            "message": "Ensure Ollama is running with embedding support"
        }), 503


@nlp_search_bp.route('/<form_id>/search-stats', methods=['GET'])
@jwt_required()
def search_stats(form_id: str):
    """
    Get search-related statistics for a form.
    
    Returns:
        {
            "total_responses": 250,
            "indexed_responses": 250,
            "ollama_available": true,
            "supported_query_types": ["sentiment", "topic", "semantic", "time"]
        }
    """
    user = get_current_user()
    
    total_responses = FormResponse.objects(form_id=form_id).count()
    
    # Check Ollama availability
    ollama_health = OllamaService.health_check()
    ollama_available = ollama_health.get("available", False)
    
    return jsonify({
        "form_id": form_id,
        "total_responses": total_responses,
        "indexed_responses": total_responses,  # All responses indexed by default
        "ollama_available": ollama_available,
        "ollama_models": ollama_health.get("models", []),
        "supported_query_types": [
            "sentiment",
            "topic",
            "semantic",
            "keyword",
            "time_based"
        ],
        "cache_ttl_seconds": 3600
    })


@nlp_search_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check for NLP search service.
    
    Returns:
        {
            "status": "healthy",
            "ollama": {...},
            "nlp": {...}
        }
    """
    ollama_status = OllamaService.health_check()
    
    return jsonify({
        "status": "healthy" if ollama_status.get("available") else "degraded",
        "ollama": ollama_status,
        "timestamp": datetime.utcnow().isoformat()
    })
