from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models.Form import Form, FormResponse
from datetime import datetime, timezone

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """System-wide Dashboard Analytics"""
    try:
        total_forms = Form.objects().count()
        published_forms = Form.objects(status='published').count()
        total_responses = FormResponse.objects(deleted=False).count()

        # Recent Activity: Last 5 Submissions
        recent_activity = []
        recent_submissions = FormResponse.objects(deleted=False).order_by('-submitted_at').limit(5)
        
        for r in recent_submissions:
            try:
                # Safely get form title if form exists
                form_title = r.form.title if r.form else "Deleted Form"
                timestamp = r.submitted_at.isoformat() if r.submitted_at else datetime.now(timezone.utc).isoformat()
                
                recent_activity.append({
                    "type": "New Submission",
                    "details": f"Response received for '{form_title}'",
                    "timestamp": timestamp,
                    "id": str(r.id)
                })
            except Exception as e:
                current_app.logger.warning(f"Error processing recent submission {r.id}: {e}")
                continue

        # Recent Activity: Last 5 Created Forms (if you want to mix them)
        # For now, let's stick to submissions or maybe mix them. Submissions are more dynamic.

        return jsonify({
            "total_forms": total_forms,
            "active_forms": published_forms,
            "total_responses": total_responses,
            "recent_activity": recent_activity
        }), 200

    except Exception as e:
        current_app.logger.error(f"Dashboard Stats Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
