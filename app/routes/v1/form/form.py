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
    
    is_template = request.args.get('is_template', 'false').lower() == 'true'
    
    # Forms where user is editor or creator
    query = {
        '$or': [
            {'created_by': str(current_user.id)},
            {'editors': str(current_user.id)}
        ]
    }
    
    # If explicitly asking for templates, we filter for them.
    # Otherwise, default behavior might be to show EVERYTHING or just non-templates?
    # Usually "Forms" list implies real forms. "Templates" implies templates.
    # But let's support filtering. 
    if is_template:
        query['is_template'] = True
    else:
        # If not asking for templates, maybe show non-templates? 
        # Or show all? Let's show all for backward compatibility, unless specified.
        # SRS D.1 says "Form Templates" is a feature.
        pass

    forms = Form.objects(__raw__=query)
    result = []
    for f in forms:
        item = f.to_mongo().to_dict()
        if '_id' in item:
            item['id'] = str(item.pop('_id'))
        result.append(item)
    return jsonify(result), 200


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
# -------------------- Cloning --------------------

@form_bp.route("/<form_id>/clone", methods=["POST"])
@jwt_required()
def clone_form(form_id):
    try:
        current_user = get_current_user()
        original_form = Form.objects.get(id=form_id)
        
        if not has_form_permission(current_user, original_form, "view"):
            return jsonify({"error": "Unauthorized to clone"}), 403
            
        data = request.get_json() or {}
        
        # New Slug
        import uuid
        new_slug = data.get("slug") or f"{original_form.slug}-copy-{uuid.uuid4().hex[:6]}"
        
        # New Title
        new_title = data.get("title") or f"Copy of {original_form.title}"
        
        # Is Template Override
        new_is_template = data.get("is_template", original_form.is_template)
        
        # Prepare Versions: Take latest only
        new_versions = []
        if original_form.versions:
            latest = original_form.versions[-1]
            # Create a copy of the structure (via mongo/dict conversion to avoid object reference issues)
            # We must use proper Schema or dict.
            # Using mongoengine's to_mongo().to_dict() is safest.
            latest_dict = latest.to_mongo().to_dict()
            latest_dict["version"] = "1.0"
            latest_dict["created_at"] = datetime.now(timezone.utc)
            latest_dict["created_by"] = str(current_user.id)
            new_versions.append(latest_dict)
            
        new_form = Form(
            title=new_title,
            slug=new_slug,
            description=original_form.description,
            created_by=str(current_user.id),
            status="draft", # reset to draft
            ui=original_form.ui,
            is_template=new_is_template,
            is_public=False, # reset to private
            versions=new_versions, # Only latest
            tags=original_form.tags,
            editors=[str(current_user.id)],
            # Copy other settings?
            notification_emails=original_form.notification_emails,
            webhooks=original_form.webhooks
        )
        
        new_form.save()
        
        current_app.logger.info(f"Form {original_form.id} cloned to {new_form.id} by {current_user.username}")
        
        return jsonify({
            "message": "Form cloned",
            "form_id": str(new_form.id),
            "slug": new_slug
        }), 201
        
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        error_trace = traceback.format_exc()
        current_app.logger.error(f"Clone error: {str(e)}\n{error_trace}")
        return jsonify({"error": str(e)}), 400
