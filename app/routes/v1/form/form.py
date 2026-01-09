import traceback
from app.routes.v1.form.helper import get_current_user, has_form_permission
from app.routes.v1.form import form_bp
from flask import current_app, request, jsonify
from flask_jwt_extended import jwt_required
from mongoengine import DoesNotExist
from app.models import Form
from app.models.User import User
from app.models.User import Role
from app.schemas.form_schema import FormSchema, FormVersionSchema, SectionSchema
from app.utils.decorator import require_roles
from app.models.Form import Form, FormResponse
from app.utils.file_handler import delete_file
import os
from datetime import datetime, timezone


# -------------------- Form CRUD --------------------

@form_bp.route("/", methods=["POST"])
@jwt_required()
@require_roles(Role.CREATOR.value, Role.ADMIN.value)
def create_form():
    data = request.get_json()
    current_user = get_current_user()
    try:
        current_app.logger.info(f"User {current_user.username} (ID: {current_user.id}) is attempting to create a form with data: {data}")
        
        # Manually parse dates
        for date_field in ['publish_at', 'expires_at']:
            if date_field in data and data[date_field]:
                try:
                    data[date_field] = datetime.fromisoformat(data[date_field])
                except ValueError:
                    pass # Let MongoEngine handle or raise error if invalid format

        form = Form(**data)
        form.created_by = str(current_user.id)
        form.editors = [str(current_user.id)]
        form.save()
        
        current_app.logger.info(f"Form {form.id} created successfully by user {current_user.username} (ID: {current_user.id})")
        return jsonify({"message": "Form created", "form_id": str(form.id)}), 201
    
    except Exception as e:
        error_trace = traceback.format_exc()
        current_app.logger.error(f"Error creating form for user {current_user.username} (ID: {current_user.id}): {str(e)}\n{error_trace}")
        return jsonify({"error": str(e)}), 400


@form_bp.route("/", methods=["GET"])
@jwt_required()
def list_forms():
    current_user = get_current_user()
    # Forms where user is editor or creator
    forms = Form.objects(__raw__={
        '$or': [
            {'created_by': str(current_user.id)},
            {'editors': str(current_user.id)}
        ]
    })
    return jsonify([f.to_mongo().to_dict() for f in forms]), 200


@form_bp.route("/<form_id>", methods=["GET"])
@jwt_required()
def get_form(form_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403

        # Check Scheduled status for non-editors
        now = datetime.now(timezone.utc)
        is_editor = has_form_permission(current_user, form, "edit") 
        if form.publish_at and now < form.publish_at.replace(tzinfo=timezone.utc) and not is_editor:
                return jsonify({"error": "Form is not yet available"}), 403

        return jsonify(form.to_mongo().to_dict()), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404


@form_bp.route("/<form_id>", methods=["PUT"])
@jwt_required()
def update_form(form_id):
    data = request.get_json()
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized to edit"}), 403
        form.update(**data)
        return jsonify({"message": "Form updated"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_bp.route("/<form_id>", methods=["DELETE"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def delete_form(form_id):
    try:
        form = Form.objects.get(id=form_id)
        # Delete all associated responses
        responses = FormResponse.objects(form=form)
        for response in responses:
            # Clean up any uploaded files associated with this response
            for section_id, section_data in response.data.items():
                if isinstance(section_data, dict):
                    for question_id, answer in section_data.items():
                        if isinstance(answer, dict) and 'filepath' in answer:
                            # This is a file upload response, delete the file
                            file_path = answer.get('filepath')
                            if file_path:
                                delete_file(file_path)
                elif isinstance(section_data, list):
                    # Handle repeatable sections
                    for entry in section_data:
                        if isinstance(entry, dict):
                            for question_id, answer in entry.items():
                                if isinstance(answer, dict) and 'filepath' in answer:
                                    file_path = answer.get('filepath')
                                    if file_path:
                                        delete_file(file_path)
        
        form.delete()
        return jsonify({"message": "Form deleted"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404