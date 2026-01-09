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
@ai_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_form_ai():
    """
    Simulated AI Form Generation.
    Parses a prompt and generates a structured form object.
    """
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").lower()
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Simulation Logic: Keyword-based template selection
        form_structure = {
            "title": "AI Generated Form",
            "description": f"Generated based on: {prompt}",
            "sections": []
        }

        if "patient" in prompt or "intake" in prompt:
            form_structure["title"] = "Patient Intake Form"
            form_structure["sections"] = [
                {
                    "title": "Personal Information",
                    "questions": [
                        {"label": "Full Name", "field_type": "input", "is_required": True},
                        {"label": "Date of Birth", "field_type": "date", "is_required": True},
                        {"label": "Gender", "field_type": "select", "options": [
                            {"option_label": "Male", "option_value": "m"},
                            {"option_label": "Female", "option_value": "f"},
                            {"option_label": "Other", "option_value": "o"}
                        ]}
                    ]
                },
                {
                    "title": "Medical History",
                    "questions": [
                        {"label": "Have you ever had surgery?", "field_type": "boolean"},
                        {"label": "Please list any allergies", "field_type": "textarea"}
                    ]
                }
            ]
        elif "job" in prompt or "apply" in prompt or "application" in prompt:
            form_structure["title"] = "Job Application Form"
            form_structure["sections"] = [
                {
                    "title": "Contact Details",
                    "questions": [
                        {"label": "Email", "field_type": "input", "is_required": True},
                        {"label": "Phone Number", "field_type": "input"},
                        {"label": "Resume Upload", "field_type": "file_upload"}
                    ]
                },
                {
                    "title": "Experience",
                    "questions": [
                        {"label": "Years of Experience", "field_type": "rating"},
                        {"label": "Cover Letter", "field_type": "textarea"}
                    ]
                }
            ]
        else:
            # Generic fallback
            form_structure["title"] = "General Feedback Form"
            form_structure["sections"] = [
                {
                    "title": "Your Feedback",
                    "questions": [
                        {"label": "Overall Satisfaction", "field_type": "rating", "is_required": True},
                        {"label": "Comments", "field_type": "textarea"}
                    ]
                }
            ]

        # Add IDs to everything (required by model)
        import uuid
        for sec in form_structure["sections"]:
            sec["id"] = str(uuid.uuid4())
            for q in sec["questions"]:
                q["id"] = str(uuid.uuid4())
                if "options" in q:
                    for opt in q["options"]:
                        opt["id"] = str(uuid.uuid4())

        return jsonify({
            "message": "Form generated successfully",
            "suggestion": form_structure
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@ai_bp.route("/suggestions", methods=["POST"])
@jwt_required()
def get_field_suggestions():
    """
    Simulated AI Field Suggestions.
    """
    try:
        data = request.get_json()
        theme = data.get("theme", "").lower()
        
        suggestions = []
        if "feedback" in theme or "survey" in theme:
            suggestions = [
                {"label": "How did you hear about us?", "field_type": "select", "options": ["Social Media", "Friend", "Ad"]},
                {"label": "On a scale of 1-10, how likely are you to recommend us?", "field_type": "rating"}
            ]
        elif "contact" in theme:
             suggestions = [
                {"label": "Preferred method of contact", "field_type": "radio", "options": ["Email", "Phone", "SMS"]},
                {"label": "Best time to call", "field_type": "input"}
            ]
        else:
             suggestions = [
                {"label": "Additional Comments", "field_type": "textarea"},
                {"label": "Tags", "field_type": "select", "is_repeatable_question": True}
            ]

        return jsonify({
            "theme": theme,
            "suggestions": suggestions
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@ai_bp.route("/templates", methods=["GET"])
@jwt_required()
def list_ai_templates():
    """
    List available AI form templates.
    """
    templates = [
        {"id": "patient_reg", "name": "Patient Registration", "category": "Medical"},
        {"id": "emp_boarding", "name": "Employee Onboarding", "category": "HR"},
        {"id": "survey_feedback", "name": "Survey/Feedback", "category": "General"},
        {"id": "event_reg", "name": "Event Registration", "category": "Events"},
        {"id": "app_form", "name": "Application Form", "category": "General"},
        {"id": "incident_report", "name": "Incident Report", "category": "Safety"}
    ]
    return jsonify({"templates": templates}), 200

@ai_bp.route("/templates/<template_id>", methods=["GET"])
@jwt_required()
def get_ai_template(template_id):
    """
    Get a specific AI template structure.
    """
    import uuid
    
    # Base structure
    template = {
        "title": template_id.replace("_", " ").title(),
        "sections": []
    }

    if template_id == "patient_reg":
        template["sections"] = [
            {"title": "Patient Info", "questions": [
                {"label": "Name", "field_type": "input"},
                {"label": "DOB", "field_type": "date"},
                {"label": "Insurance ID", "field_type": "input"}
            ]}
        ]
    elif template_id == "emp_boarding":
        template["sections"] = [
            {"title": "Job Details", "questions": [
                {"label": "Department", "field_type": "select", "options": [{"option_label": "IT", "option_value": "it"}, {"option_label": "HR", "option_value": "hr"}]},
                {"label": "Start Date", "field_type": "date"}
            ]}
        ]
    elif template_id == "incident_report":
        template["sections"] = [
            {"title": "Incident Details", "questions": [
                {"label": "Date of Incident", "field_type": "date"},
                {"label": "Location", "field_type": "input"},
                {"label": "Describe what happened", "field_type": "textarea"}
            ]}
        ]
    else:
        # Generic Template
        template["sections"] = [
            {"title": "Section 1", "questions": [{"label": "Sample Question", "field_type": "input"}]}
        ]

    # Assign UUIDs
    for sec in template["sections"]:
        sec["id"] = str(uuid.uuid4())
        for q in sec["questions"]:
            q["id"] = str(uuid.uuid4())
            if "options" in q:
                for opt in q["options"]:
                    opt["id"] = str(uuid.uuid4())

    return jsonify({"template": template}), 200
