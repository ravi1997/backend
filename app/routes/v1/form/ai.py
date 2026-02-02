from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models.Form import Form, FormResponse
from app.routes.v1.form.helper import get_current_user, has_form_permission
from datetime import datetime, timezone
import re

ai_bp = Blueprint("ai", __name__)

def simple_sentiment_analyzer(text):
    positive_words = {
        "good", "great", "excellent", "happy", "satisfied", "positive", "amazing", "wonderful", "best",
        "love", "perfect", "easy", "helpful", "fast", "efficient", "thanks"
    }
    negative_words = {
        "bad", "poor", "unhappy", "dissatisfied", "negative", "terrible", "worst", "error", "fail", "slow", 
        "broken", "hate", "hard", "useless", "expensive", "issue", "problem", "difficult"
    }
    
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
        all_text = []
        def extract_text(obj):
            if isinstance(obj, dict):
                for v in obj.values(): extract_text(v)
            elif isinstance(obj, list):
                for item in obj: extract_text(item)
            elif isinstance(obj, str): all_text.append(obj)
        
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
        ai_results = getattr(response, 'ai_results', {})
        ai_results.update({
            "sentiment": {
                "label": sentiment,
                "score": score,
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            },
            "pii_scan": {
                "found_count": len(pii_found["emails"]) + len(pii_found["phones"]),
                "details": pii_found if (len(pii_found["emails"]) + len(pii_found["phones"])) > 0 else None
            },
            "summary": "Processed by Antigravity AI Helper"
        })
        
        response.update(set__ai_results=ai_results)
        
        return jsonify({
            "message": "AI analysis complete",
            "results": ai_results
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@ai_bp.route("/<form_id>/responses/<response_id>/moderate", methods=["POST"])
@jwt_required()
def moderate_response_ai(form_id, response_id):
    """
    Deep Content Moderation:
    - Extended PII (SSN, Credit Cards)
    - PHI (Medical terminology)
    - Profanity Filtering
    - Injection Detection (XSS/SQL)
    """
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403
            
        response = FormResponse.objects.get(id=response_id, form=form.id)
        
        # 1. Extract all text
        all_text = []
        def extract_text(obj):
            if isinstance(obj, dict):
                for v in obj.values(): extract_text(v)
            elif isinstance(obj, list):
                for item in obj: extract_text(item)
            elif isinstance(obj, str): all_text.append(obj)
        
        extract_text(response.data)
        text = " ".join(all_text)
        text_lower = text.lower()
        
        # 2. Moderation Engines
        flags = []
        
        # PII Detection (Sensitive)
        pii_patterns = {
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b(?:\d[ -]*?){13,16}\b',
            "email": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
            "phone": r'\b\d{10}\b'
        }
        found_pii = {}
        for key, pattern in pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                 found_pii[key] = len(matches)
                 flags.append(f"PII Detected: {key.upper()}")

        # PHI Detection (Medical)
        phi_keywords = {"diabetes", "hiv", "cancer", "medication", "prescription", "diagnosis", "treatment", "therapy"}
        found_phi = [w for w in phi_keywords if w in text_lower]
        if found_phi:
            flags.append(f"PHI Potential: {', '.join(found_phi)}")

        # Profanity Detection (Basic)
        profanity_list = {"abuse", "offensive", "violent", "vulgar"} # Expanded in real life
        found_profanity = [w for w in profanity_list if w in text_lower]
        if found_profanity:
            flags.append("Warning: Profane or inappropriate language detected")

        # Injection Detection (Security)
        injection_patterns = [r'<script', r'javascript:', r'or 1=1', r'drop table', r'select \*']
        found_injection = any(re.search(p, text_lower) for p in injection_patterns)
        if found_injection:
            flags.append("CRITICAL: Potential Code/SQL Injection attempt")

        # Update ai_results
        moderation_results = {
            "is_safe": not (found_profanity or found_injection),
            "flags": flags,
            "pii_summary": found_pii,
            "phi_detected": found_phi,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }
        
        current_results = getattr(response, 'ai_results', {})
        current_results["moderation"] = moderation_results
        response.update(set__ai_results=current_results)
        
        return jsonify({
            "message": "Content moderation complete",
            "moderation": moderation_results
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
from app.services.ai_service import AIService

@ai_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_form_ai():
    """
    AI Form Generation using local LLM.
    """
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        current_form = data.get("current_form") # Optional context
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        form_structure = AIService.generate_form(prompt, current_form)

        return jsonify({
            "message": "Form generated successfully",
            "suggestion": form_structure
        }), 200

    except Exception as e:
        current_app.logger.error(f"Generate AI Form Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

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

@ai_bp.route("/<form_id>/sentiment", methods=["GET"])
@jwt_required()
def get_form_sentiment_trends(form_id):
    """
    Get sentiment distribution and trends for all responses in a form.
    """
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "view"):
             return jsonify({"error": "Unauthorized"}), 403

        responses = FormResponse.objects(form=form.id, deleted=False)
        
        counts = {"positive": 0, "negative": 0, "neutral": 0, "unprocessed": 0}
        total_score = 0
        analyzed_count = 0

        for resp in responses:
            results = getattr(resp, 'ai_results', {})
            sentiment_data = results.get('sentiment')
            if sentiment_data:
                label = sentiment_data.get('label', 'neutral')
                counts[label] += 1
                total_score += sentiment_data.get('score', 0)
                analyzed_count += 1
            else:
                counts["unprocessed"] += 1
        
        return jsonify({
            "form_id": form_id,
            "total_responses": len(responses),
            "analyzed_responses": analyzed_count,
            "distribution": counts,
            "average_score": (total_score / analyzed_count) if analyzed_count > 0 else 0
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@ai_bp.route("/<form_id>/search", methods=["POST"])
@jwt_required()
def ai_powered_search(form_id):
    """
    AI-Powered Smart Search for form responses.
    Translates Natural Language queries into filters.
    """
    try:
        data = request.get_json()
        query = data.get("query", "").lower()
        if not query:
            return jsonify({"error": "Search query is required"}), 400

        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "view"):
             return jsonify({"error": "Unauthorized"}), 403

        # Base filter
        filters = {"form": form.id, "deleted": False}

        # Simulated NL Parsing
        # 1. Age patterns: "over 60", "under 30", "older than 25"
        age_gt_match = re.search(r'(?:over|older than|above)\s+(\d+)', query)
        age_lt_match = re.search(r'(?:under|younger than|below)\s+(\d+)', query)
        
        # 2. Keyword extraction (naive)
        # We'll look for words that aren't common stop words/operators
        stop_words = {"find", "all", "patients", "with", "who", "are", "over", "under", "is", "a", "the", "and"}
        words = re.findall(r'\w+', query)
        keywords = [w for w in words if w not in stop_words and not w.isdigit()]

        results = FormResponse.objects(**filters)
        
        # In-memory filtering for demo/simulation (since data is dict/dynamic)
        final_results = []
        for resp in results:
            match = True
            resp_data_str = str(resp.data).lower()
            
            # Check keywords
            for kw in keywords:
                if kw not in resp_data_str:
                    match = False
                    break
            
            if not match: continue

            # Check Age (if found in query and exists in data)
            # Naive: looks for any number in the data that could be age
            if age_gt_match or age_lt_match:
                # Try to find a number in resp.data that looks like an age
                # For this simulation, we'll just check if any value in the dict is a number
                def find_numbers(d):
                    nums = []
                    if isinstance(d, dict):
                        for v in d.values(): nums.extend(find_numbers(v))
                    elif isinstance(d, list):
                        for v in d: nums.extend(find_numbers(v))
                    elif isinstance(d, (int, float)):
                        nums.append(d)
                    elif isinstance(d, str) and d.isdigit():
                        nums.append(int(d))
                    return nums

                resp_nums = find_numbers(resp.data)
                
                if age_gt_match:
                    threshold = int(age_gt_match.group(1))
                    if not any(n > threshold for n in resp_nums):
                        match = False
                
                if age_lt_match:
                    threshold = int(age_lt_match.group(1))
                    if not any(n < threshold for n in resp_nums):
                        match = False

            if match:
                final_results.append(resp)

        return jsonify({
            "query": query,
            "count": len(final_results),
            "results": [str(r.id) for r in final_results] # Return IDs
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@ai_bp.route("/<form_id>/anomalies", methods=["POST"])
@jwt_required()
def detect_form_anomalies(form_id):
    """
    Scans form responses for anomalies:
    1. Duplicate content (Spam detection)
    2. Statistical Outliers in numerical fields
    3. Gibberish/Short text detection
    """
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "view"):
             return jsonify({"error": "Unauthorized"}), 403

        responses = FormResponse.objects(form=form.id, deleted=False)
        if len(responses) < 3:
            return jsonify({"message": "Not enough data for anomaly detection (min 3 responses required)", "anomalies": []}), 200

        flagged = []
        
        # 1. Duplicate Detection
        content_hashes = {}
        
        # 2. Outlier detection prep
        num_values_per_question = {} # {qid: [list of values]}
        
        def process_data(data, resp_id):
            flat_items = []
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, (int, float)):
                        num_values_per_question.setdefault(k, []).append((v, resp_id))
                    elif isinstance(v, str):
                        flat_items.append(v)
                    elif isinstance(v, (dict, list)):
                        flat_items.extend(process_data(v, resp_id))
            return flat_items

        all_resp_text = {} # {resp_id: combined_text}

        for resp in responses:
            rid = str(resp.id)
            text_parts = process_data(resp.data, rid)
            combined = " ".join(text_parts).strip()
            all_resp_text[rid] = combined
            
            # Duplicate check
            if combined and combined in content_hashes:
                flagged.append({
                    "response_id": rid,
                    "type": "duplicate",
                    "confidence": 0.9,
                    "reason": f"Content matches response {content_hashes[combined]}"
                })
            content_hashes[combined] = rid

            # 3. Gibberish Check (Simple heuristic: very short or low vowel count)
            if combined and len(combined) > 0:
                vowels = len(re.findall(r'[aeiou]', combined.lower()))
                if len(combined) > 10 and vowels / len(combined) < 0.1:
                    flagged.append({
                        "response_id": rid,
                        "type": "low_quality",
                        "confidence": 0.7,
                        "reason": "Text pattern looks like gibberish (low vowel ratio)"
                    })

        # Statistical Outliers (Z-Score method baseline)
        import math
        for qid, items in num_values_per_question.items():
            if len(items) < 3: continue
            
            vals = [x[0] for x in items]
            mean = sum(vals) / len(vals)
            variance = sum((x - mean) ** 2 for x in vals) / len(vals)
            std_dev = math.sqrt(variance)
            
            if std_dev == 0: continue
            
            for val, rid in items:
                z_score = abs(val - mean) / std_dev
                if z_score > 2: # 2 Sigma threshold
                    flagged.append({
                        "response_id": rid,
                        "type": "outlier",
                        "confidence": min(0.9, z_score / 5),
                        "reason": f"Value {val} is a statistical outlier for field {qid}"
                    })

        return jsonify({
            "form_id": form_id,
            "total_scanned": len(responses),
            "anomaly_count": len(flagged),
            "anomalies": flagged
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
@ai_bp.route("/<form_id>/security-scan", methods=["POST"])
@jwt_required()
def scan_form_security_ai(form_id):
    """
    Automated Security Scanning for Form Definitions.
    Analyzes questions, settings, and permissions for vulnerabilities.
    """
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "edit"):
             return jsonify({"error": "Unauthorized"}), 403

        findings = []
        recommendations = []
        score = 100

        # 1. Public Access Check
        is_public = getattr(form, 'is_public', False)
        
        # 2. Section/Question Scan
        sensitive_keywords = {"ssn", "password", "credit card", "pin", "otp", "medical", "health", "bank"}
        text_fields_without_validation = 0
        sensitive_fields_found = []

        for section in form.versions[-1].sections:
            for question in section.questions:
                label_lower = question.label.lower()
                
                # Identify sensitive fields
                if any(kw in label_lower for kw in sensitive_keywords):
                    sensitive_fields_found.append(question.label)
                    if is_public:
                        findings.append({
                            "severity": "HIGH",
                            "issue": f"Sensitive field '{question.label}' exposed on Public Form",
                            "detail": "Asking for sensitive information on a form without authentication is a significant privacy risk."
                        })
                        score -= 20

                # Spam risk check
                if question.field_type in ["input", "textarea"]:
                    # Check if any validation exists (required or regex rules)
                    has_validation = question.is_required or getattr(question, 'validation_rules', None)
                    if not has_validation:
                        text_fields_without_validation += 1

        if text_fields_without_validation > 3:
            findings.append({
                "severity": "MEDIUM",
                "issue": "High Spam Risk",
                "detail": f"{text_fields_without_validation} open text fields found without validation rules."
            })
            score -= 10
            recommendations.append("Add regex or length constraints to open text fields to prevent automated spam.")

        # 3. Custom Script Scan
        custom_script = getattr(form, 'custom_script', None)
        if custom_script:
            findings.append({
                "severity": "LOW",
                "issue": "Active Custom Script",
                "detail": "Custom scripts can execute server-side logic. Ensure this script is audited for security."
            })
            recommendations.append("Regularly review custom scripts for potential injection or data leakage vulnerabilities.")

        # Final Score Logic
        score = max(0, score)
        status = "PASSED" if score >= 80 else "WARNING" if score >= 50 else "FAILED"

        report = {
            "form_id": form_id,
            "security_score": score,
            "status": status,
            "findings": findings,
            "recommendations": recommendations,
            "scanned_at": datetime.now(timezone.utc).isoformat()
        }

        # Store report in form if necessary (optional)
        # form.update(set__security_report=report)

        return jsonify(report), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@ai_bp.route("/cross-analysis", methods=["POST"])
@jwt_required()
def compare_forms_ai():
    """
    Compare multiple forms' performance and sentiment.
    Payload: { "form_ids": ["id1", "id2"] }
    """
    try:
        data = request.get_json()
        form_ids = data.get("form_ids", [])
        
        if not form_ids or not isinstance(form_ids, list):
            return jsonify({"error": "form_ids list is required"}), 400
            
        current_user = get_current_user()
        
        results = []
        global_stats = {
            "total_forms": len(form_ids),
            "total_responses": 0,
            "average_sentiment_score": 0
        }
        
        total_sentiment_sum = 0
        forms_with_sentiment = 0
        
        for fid in form_ids:
            try:
                form = Form.objects.get(id=fid)
                # Check permission for each form
                if not has_form_permission(current_user, form, "view"):
                    # For security, we can either fail hard or skip. 
                    # Failing hard is safer to prevent enumeration.
                    return jsonify({"error": f"Unauthorized access to form {fid}"}), 403
                
                responses = FormResponse.objects(form=fid, deleted=False)
                resp_count = len(responses)
                
                # Aggregation
                sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0, "unprocessed": 0}
                form_total_score = 0
                analyzed_count = 0
                
                for r in responses:
                    res = getattr(r, 'ai_results', {})
                    sent = res.get('sentiment')
                    if sent:
                        label = sent.get('label', 'neutral')
                        sentiment_counts[label] = sentiment_counts.get(label, 0) + 1
                        form_total_score += sent.get('score', 0)
                        analyzed_count += 1
                    else:
                        sentiment_counts["unprocessed"] += 1
                
                avg_score = (form_total_score / analyzed_count) if analyzed_count > 0 else 0
                
                results.append({
                    "form_id": str(form.id),
                    "title": form.title,
                    "response_count": resp_count,
                    "sentiment_distribution": sentiment_counts,
                    "average_sentiment": avg_score
                })
                
                global_stats["total_responses"] += resp_count
                if analyzed_count > 0:
                    total_sentiment_sum += avg_score
                    forms_with_sentiment += 1
                    
            except Form.DoesNotExist:
                return jsonify({"error": f"Form {fid} not found"}), 404
        
        global_stats["average_sentiment_score"] = (total_sentiment_sum / forms_with_sentiment) if forms_with_sentiment > 0 else 0
        
        return jsonify({
            "summary": global_stats,
            "details": results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
