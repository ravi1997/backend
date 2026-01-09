from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models.Form import Form, FormResponse
from app.routes.v1.form.helper import get_current_user, has_form_permission
from datetime import datetime
import re

ai_bp = Blueprint("ai", __name__)

def simple_sentiment_analyzer(text):
    positive_words = {"good", "great", "excellent", "happy", "satisfied", "positive", "amazing", "wonderful", "best"}
    negative_words = {"bad", "poor", "unhappy", "dissatisfied", "negative", "terrible", "worst", "error", "fail", "slow", "broken"}
    
    words = re.findall(r'\w+', text.lower())
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    
    score = pos_count - neg_count
    if score > 0:
        return "positive", score
    elif score < 0:
        return "negative", score
    else:
        return "neutral", 0

@ai_bp.route("/<form_id>/responses/<response_id>/analyze", methods=["POST"])
@jwt_required()
def analyze_response_ai(form_id, response_id):
    """
    Perform AI tasks (Sentiment, PII detection) on a response.
    """
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403
            
        response = FormResponse.objects.get(id=response_id, form=form.id)
        
        # 1. Sentiment Analysis
        # Extract all text values
        all_text = []
        def extract_text(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    extract_text(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item)
            elif isinstance(obj, str):
                all_text.append(obj)
        
        extract_text(response.data)
        combined_text = " ".join(all_text)
        
        sentiment, score = simple_sentiment_analyzer(combined_text)
        
        # 2. PII Detection (Basic)
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        phone_pattern = r'\b\d{10}\b'
        
        pii_found = {
            "emails": re.findall(email_pattern, combined_text),
            "phones": re.findall(phone_pattern, combined_text)
        }
        
        # Update results
        ai_results = {
            "sentiment": {
                "label": sentiment,
                "score": score,
                "analyzed_at": datetime.utcnow().isoformat()
            },
            "pii_scan": {
                "found_count": len(pii_found["emails"]) + len(pii_found["phones"]),
                "details": pii_found if (len(pii_found["emails"]) + len(pii_found["phones"])) > 0 else None
            },
            "summary": "Processed by Antigravity AI Helper"
        }
        
        response.update(set__ai_results=ai_results)
        
        return jsonify({
            "message": "AI analysis complete",
            "results": ai_results
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
