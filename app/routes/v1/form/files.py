from app.routes.v1.form.helper import get_current_user, has_form_permission
from app.routes.v1.form import form_bp
from flask import current_app, request, jsonify, send_file
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from mongoengine import DoesNotExist
from app.models import Form
from app.models.User import Role
from app.utils.decorator import require_roles
import os

@form_bp.route("/<form_id>/files/<question_id>/<filename>", methods=["GET"])
def get_file(form_id, question_id, filename):
    """Serve uploaded files. Can be accessed by users with view permissions or for public forms"""
    try:
        # Check if the request has JWT token, if yes verify permissions
        try:
            verify_jwt_in_request()
            current_user = get_current_user()
            form = Form.objects.get(id=form_id)
            
            # User has JWT token, check permissions
            if not has_form_permission(current_user, form, "view"):
                return jsonify({"error": "Unauthorized to access this form"}), 403
        except:
            # No JWT token provided, check if form is public
            form = Form.objects.get(id=form_id)
            if not form.is_public:
                return jsonify({"error": "Unauthorized - form not public"}), 403
        
        # Check if the question is of file_upload type
        question_found = False
        for section in form.versions[-1].sections:
            for question in section.questions:
                if str(question.id) == str(question_id) and question.field_type == "file_upload":
                    question_found = True
                    break
            if question_found:
                break
        
        if not question_found:
            return jsonify({"error": "File access denied"}), 403
        
        # Build file path and verify it exists
        file_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 
                                str(form_id), str(question_id), filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
            
        return send_file(file_path)
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error serving file: {str(e)}")
        return jsonify({"error": "Error serving file"}), 500