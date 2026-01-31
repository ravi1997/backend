from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.Form import CustomFieldTemplate, Question
from app.routes.v1.form.helper import get_current_user
import traceback

library_bp = Blueprint("library", __name__)

@library_bp.route("/", methods=["GET"])
@jwt_required()
def list_field_templates():
    try:
        current_user_id = get_jwt_identity()
        category = request.args.get("category")
        
        query = {"user_id": str(current_user_id)}
        if category:
            query["category"] = category
            
        templates = CustomFieldTemplate.objects(**query)
        result = []
        for t in templates:
            result.append({
                "id": str(t.id),
                "name": t.name,
                "category": t.category,
                "question_data": t.question_data.to_mongo().to_dict() if t.question_data else None,
                "created_at": t.created_at.isoformat()
            })
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error listing field templates: {str(e)}")
        return jsonify({"error": str(e)}), 400

@library_bp.route("/", methods=["POST"])
@jwt_required()
def save_field_template():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        name = data.get("name")
        category = data.get("category")
        question_data_raw = data.get("question_data")
        
        if not name or not question_data_raw:
            return jsonify({"error": "Missing name or question_data"}), 400
            
        # Parse question data into Question model
        # We can use the model constructor
        question = Question(**question_data_raw)
        
        template = CustomFieldTemplate(
            user_id=str(current_user_id),
            name=name,
            category=category,
            question_data=question
        )
        template.save()
        
        return jsonify({"message": "Field template saved", "id": str(template.id)}), 201
    except Exception as e:
        current_app.logger.error(f"Error saving field template: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 400

@library_bp.route("/<template_id>", methods=["DELETE"])
@jwt_required()
def delete_field_template(template_id):
    try:
        current_user_id = get_jwt_identity()
        template = CustomFieldTemplate.objects.get(id=template_id, user_id=str(current_user_id))
        template.delete()
        return jsonify({"message": "Field template deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
