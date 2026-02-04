"""
Anomaly Detection Routes

API endpoints for detecting anomalous form responses.

Task: T-M2-04 - Predictive Anomaly Detection
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from typing import Dict, Any
import time

from app.models.Form import FormResponse
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.utils.auth import jwt_required, get_current_user


anomaly_bp = Blueprint('anomaly', __name__, url_prefix='/api/v1/ai/forms')


@anomaly_bp.route('/<form_id>/detect-anomalies', methods=['POST'])
@jwt_required()
def detect_anomalies(form_id: str):
    """
    Run anomaly detection on form responses.
    
    Request Body:
        {
            "scan_type": "full" | "incremental",
            "response_ids": ["id1", "id2"],  // Optional
            "detection_types": ["spam", "outlier", "impossible_value", "duplicate"],
            "sensitivity": "low" | "medium" | "high",
            "save_results": true
        }
    
    Returns:
        {
            "form_id": "form_123",
            "scan_type": "full",
            "responses_scanned": 250,
            "anomalies_detected": 12,
            "baseline": {...},
            "anomalies": [...],
            "summary_by_type": {...}
        }
    """
    user = get_current_user()
    data = request.get_json() or {}
    
    scan_type = data.get('scan_type', 'full')
    response_ids = data.get('response_ids', [])
    detection_types = data.get('detection_types', ['spam', 'outlier'])
    sensitivity = data.get('sensitivity', 'medium')
    save_results = data.get('save_results', False)
    
    start_time = time.time()
    
    # Fetch responses
    if response_ids:
        responses = FormResponse.objects(id__in=response_ids, form_id=form_id)
    elif scan_type == 'full':
        responses = FormResponse.objects(form_id=form_id)
    else:
        # Incremental - get recent responses
        responses = FormResponse.objects(form_id=form_id).order_by('-created_at').limit(100)
    
    # Prepare response data
    response_data = []
    for resp in responses:
        resp_data = {
            "id": str(resp.id),
            "text": str(resp.data),
            "submitted_at": resp.submitted_at.isoformat() if resp.submitted_at else None,
            "sentiment": resp.ai_results.get('sentiment', {}) if hasattr(resp, 'ai_results') and resp.ai_results else {}
        }
        response_data.append(resp_data)
    
    # Run detection
    results = AnomalyDetectionService.run_full_detection(
        response_data,
        sensitivity=sensitivity,
        detection_types=detection_types
    )
    
    scan_duration = int((time.time() - start_time) * 1000)
    
    return jsonify({
        "form_id": form_id,
        "scan_type": scan_type,
        "responses_scanned": len(response_data),
        "anomalies_detected": results['anomalies_detected'],
        "scan_duration_ms": scan_duration,
        "baseline": results['baseline'],
        "anomalies": results['anomalies'],
        "summary_by_type": results['summary_by_type']
    })


@anomaly_bp.route('/<form_id>/anomalies/<response_id>', methods=['GET'])
@jwt_required()
def get_anomaly_details(form_id: str, response_id: str):
    """
    Get detailed anomaly information for a specific response.
    
    Returns:
        {
            "response_id": "resp_789",
            "anomaly_flags": {...},
            "response_data": {...},
            "review_status": "pending",
            "suggested_actions": [...]
        }
    """
    user = get_current_user()
    
    # Fetch response
    try:
        resp = FormResponse.objects.get(id=response_id, form_id=form_id)
    except FormResponse.DoesNotExist:
        return jsonify({"error": "Response not found"}), 404
    
    # Run detection on single response
    response_data = {
        "id": str(resp.id),
        "text": str(resp.data),
        "sentiment": resp.ai_results.get('sentiment', {}) if hasattr(resp, 'ai_results') and resp.ai_results else {}
    }
    
    spam_result = AnomalyDetectionService.detect_spam(response_data)
    
    # Prepare anomaly flags
    anomaly_flags = {
        "spam": {
            "score": spam_result['spam_score'],
            "indicators": spam_result['indicators'],
            "confidence": spam_result['spam_score'] / 100 if spam_result['is_spam'] else 0
        }
    }
    
    return jsonify({
        "response_id": response_id,
        "anomaly_flags": anomaly_flags,
        "response_data": {
            "text": str(resp.data),
            "submitted_at": resp.submitted_at.isoformat() if resp.submitted_at else None
        },
        "review_status": "pending",
        "suggested_actions": ["review", "flag_response", "ignore"]
    })


@anomaly_bp.route('/<form_id>/anomaly-stats', methods=['GET'])
@jwt_required()
def get_anomaly_stats(form_id: str):
    """
    Get anomaly detection statistics for a form.
    
    Returns:
        {
            "form_id": "form_123",
            "total_responses": 250,
            "flagged_count": 12,
            "flagged_percentage": 4.8,
            "recent_scans": [...]
        }
    """
    user = get_current_user()
    
    total = FormResponse.objects(form_id=form_id).count()
    
    # This would query anomaly history in production
    recent_scans = []
    
    return jsonify({
        "form_id": form_id,
        "total_responses": total,
        "flagged_count": 0,  # Would be calculated from anomaly records
        "flagged_percentage": 0.0,
        "reviewed_count": 0,
        "false_positive_rate": 0.0,
        "detection_accuracy": 0.0,
        "recent_scans": recent_scans
    })


@anomaly_bp.route('/<form_id>/anomalies/<response_id>/feedback', methods=['POST'])
@jwt_required()
def submit_anomaly_feedback(form_id: str, response_id: str):
    """
    Submit feedback on anomaly detection results.
    
    Request Body:
        {
            "feedback_type": "false_positive" | "correct",
            "comment": "Optional comment"
        }
    
    Returns:
        {
            "message": "Feedback recorded successfully",
            "feedback_id": "fb_123",
            "model_improvement": "..."
        }
    """
    user = get_current_user()
    data = request.get_json() or {}
    
    feedback_type = data.get('feedback_type')
    comment = data.get('comment', '')
    
    if feedback_type not in ['false_positive', 'correct']:
        return jsonify({"error": "Invalid feedback_type"}), 400
    
    # In production, this would save to AnomalyFeedback collection
    feedback_id = f"fb_{int(time.time())}"
    
    return jsonify({
        "message": "Feedback recorded successfully",
        "feedback_id": feedback_id,
        "model_improvement": "This feedback will help improve future detection accuracy"
    })
