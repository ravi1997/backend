"""
Summarization Routes

API endpoints for automated response summarization.

Task: T-M2-03 - Automated Summarization
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from typing import Dict, Any
import time

from app.models.Form import FormResponse
from app.services.summarization_service import SummarizationService
from app.services.ollama_service import OllamaService
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.v1.form.helper import get_current_user
from app.utils.redis_client import redis_client


summarization_bp = Blueprint('summarization', __name__, url_prefix='/api/v1/ai/forms')


@summarization_bp.route('/<form_id>/summarize', methods=['POST'])
@jwt_required()
def summarize(form_id: str):
    """
    Generate summary from form responses.
    """
    user = get_current_user()
    data = request.get_json() or {}
    
    response_ids = data.get('response_ids', [])
    strategy = data.get('strategy', 'hybrid')
    format_type = data.get('format', 'bullet_points')
    config = data.get('config', {})
    
    start_time = time.time()
    
    if response_ids:
        responses = FormResponse.objects(id__in=response_ids, form_id=form_id)
    else:
        responses = FormResponse.objects(form_id=form_id).limit(200)
    
    response_texts = []
    for resp in responses:
        resp_data = {
            "id": str(resp.id),
            "text": str(resp.data),
            "sentiment": resp.ai_results.get('sentiment', {}) if hasattr(resp, 'ai_results') else {}
        }
        response_texts.append(resp_data)
    
    summary = SummarizationService.hybrid_summarize(
        response_texts,
        strategy=strategy,
        format_type=format_type,
        config=config
    )
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return jsonify({
        "form_id": form_id,
        "responses_analyzed": len(response_texts),
        "strategy_used": strategy,
        "summary": summary,
        "metadata": {
            "processing_time_ms": processing_time,
            "model_used": OllamaService.get_default_model() if strategy != "extractive" else "tfidf",
            "cached": False
        }
    })


@summarization_bp.route('/<form_id>/executive-summary', methods=['POST'])
@jwt_required()
def executive_summary(form_id: str):
    """
    Generate executive summary for leadership.
    """
    user = get_current_user()
    data = request.get_json() or {}
    
    response_ids = data.get('response_ids', [])
    audience = data.get('audience', 'leadership')
    tone = data.get('tone', 'formal')
    
    if response_ids:
        responses = FormResponse.objects(id__in=response_ids, form_id=form_id)
    else:
        responses = FormResponse.objects(form_id=form_id).limit(200)
    
    response_texts = [str(resp.data) for resp in responses]
    
    exec_summary = SummarizationService.generate_executive_summary(
        response_texts,
        audience=audience,
        tone=tone
    )
    
    return jsonify({
        "form_id": form_id,
        "executive_summary": exec_summary,
        "generated_at": datetime.utcnow().isoformat()
    })


@summarization_bp.route('/<form_id>/theme-summary', methods=['POST'])
@jwt_required()
def theme_summary(form_id: str):
    """
    Generate theme-based summary.
    """
    user = get_current_user()
    data = request.get_json() or {}
    
    themes = data.get('themes', ['delivery', 'product', 'support', 'pricing'])
    include_quotes = data.get('include_quote_examples', True)
    sentiment_per_theme = data.get('sentiment_per_theme', True)
    
    responses = FormResponse.objects(form_id=form_id).limit(200)
    
    response_texts = [str(resp.data) for resp in responses]
    
    theme_analysis = SummarizationService._analyze_themes(response_texts)
    
    theme_summary = {}
    for theme, theme_data in theme_analysis.items():
        summary_item = {
            "sentiment": theme_data.get('sentiment', 'mixed'),
            "mention_count": theme_data.get('mentions', 0),
            "summary": f"Analysis of {theme_data.get('mentions', 0)} responses related to {theme}."
        }
        theme_summary[theme] = summary_item
    
    return jsonify({
        "form_id": form_id,
        "theme_summary": theme_summary
    })
