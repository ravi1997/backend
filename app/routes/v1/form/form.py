import traceback
import csv
import io
from app.routes.v1.form.helper import get_current_user, has_form_permission, apply_translations
from app.routes.v1.form import form_bp
from flask import current_app, request, jsonify
from flask_jwt_extended import jwt_required
from mongoengine import DoesNotExist
from app.models import Form
from app.models.User import User
from app.models.User import Role
from app.schemas.form_schema import FormSchema, FormVersionSchema, SectionSchema
from app.utils.decorator import require_roles
from app.models.Form import Form, FormResponse, Option
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

        # Filter fields that exist in Form model
        valid_fields = set(Form._fields.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        form = Form(**filtered_data)
        form.created_by = str(current_user.id)
        form.editors = [str(current_user.id)]
        if form.versions:
            form.active_version = form.versions[-1].version
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

        lang = request.args.get("lang")
        version_req = request.args.get("v")
        
        form_dict = form.to_mongo().to_dict()
        
        # If version explicitly requested, filter version list to only show that one
        if version_req:
            target_v = next((v for v in form_dict.get("versions", []) if v["version"] == version_req), None)
            if target_v:
                form_dict["versions"] = [target_v]
            else:
                return jsonify({"error": "Version not found"}), 404
        elif form.active_version:
            # Fallback to active version in the list? 
            # Or just show all (current behavior)?
            # Usually for preview/submit we want specific one.
            pass

        if lang:
            form_dict = apply_translations(form_dict, lang)

        return jsonify(form_dict), 200
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
        # Filter fields that exist in Form model
        valid_fields = set(Form._fields.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        form.update(**filtered_data)
        return jsonify({"message": "Form updated"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_bp.route("/<form_id>/translations", methods=["POST"])
@jwt_required()
def update_form_translations(form_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized"}), 403
            
        data = request.get_json()
        lang_code = data.get("lang_code")
        translations = data.get("translations")
        
        if not lang_code or not translations:
            return jsonify({"error": "Missing lang_code or translations"}), 400
            
        if not form.versions:
            return jsonify({"error": "Form has no versions"}), 400
            
        latest_version = form.versions[-1]
        if not latest_version.translations:
            latest_version.translations = {}
            
        latest_version.translations[lang_code] = translations
        
        # Add to supported_languages if not already there
        if lang_code not in form.supported_languages:
            form.supported_languages.append(lang_code)
            
        form.save()
        return jsonify({"message": f"Translations for '{lang_code}' updated"}), 200
        
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
        FormResponse.objects(form=form.id).delete()
        
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


# -------------------- Reordering --------------------

@form_bp.route("/<form_id>/reorder-sections", methods=["PATCH"])
@jwt_required()
def reorder_sections(form_id):
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized to edit form"}), 403
            
        data = request.get_json()
        new_order = data.get("order") # List of section IDs
        v_str = request.args.get("v")
        
        if not new_order or not isinstance(new_order, list):
            return jsonify({"error": "Invalid order list"}), 400
            
        if not form.versions:
            return jsonify({"error": "Form has no versions"}), 400
            
        # Find target version
        if v_str:
            target_version = next((v for v in form.versions if v.version == v_str), None)
            if not target_version:
                return jsonify({"error": f"Version {v_str} not found"}), 404
        else:
            target_version = form.versions[-1]

        existing_sections = {str(s.id): s for s in target_version.sections}
        
        if len(new_order) != len(existing_sections):
            return jsonify({"error": "Order list length mismatch"}), 400
            
        # Verify all IDs exist
        for sid in new_order:
            if sid not in existing_sections:
                return jsonify({"error": f"Section ID {sid} not found in form"}), 400
        
        # Reconstruct sections list in new order
        reordered_sections = [existing_sections[sid] for sid in new_order]
        
        # Update each section's order field (optional but good practice)
        for idx, section in enumerate(reordered_sections):
            section.order = idx
            
        target_version.sections = reordered_sections
        form.save()
        
        return jsonify({"message": "Sections reordered successfully"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Reorder sections error: {str(e)}")
        return jsonify({"error": str(e)}), 400

@form_bp.route("/<form_id>/section/<section_id>/reorder-questions", methods=["PATCH"])
@jwt_required()
def reorder_questions(form_id, section_id):
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized to edit form"}), 403
            
        data = request.get_json()
        new_order = data.get("order") # List of question IDs
        v_str = request.args.get("v")
        
        if not new_order or not isinstance(new_order, list):
            return jsonify({"error": "Invalid order list"}), 400
            
        if not form.versions:
            return jsonify({"error": "Form has no versions"}), 400
            
        # Find target version
        if v_str:
            target_version = next((v for v in form.versions if v.version == v_str), None)
            if not target_version:
                return jsonify({"error": f"Version {v_str} not found"}), 404
        else:
            target_version = form.versions[-1]
        
        target_section = None
        for s in target_version.sections:
            if str(s.id) == section_id:
                target_section = s
                break
                
        if not target_section:
            return jsonify({"error": "Section not found"}), 404
            
        existing_questions = {str(q.id): q for q in target_section.questions}
        
        if len(new_order) != len(existing_questions):
            return jsonify({"error": "Order list length mismatch"}), 400
            
        for qid in new_order:
            if qid not in existing_questions:
                return jsonify({"error": f"Question ID {qid} not found in section"}), 400
                
        reordered_questions = [existing_questions[qid] for qid in new_order]
        
        for idx, question in enumerate(reordered_questions):
            question.order = idx
            
        target_section.questions = reordered_questions
        form.save()
        
        return jsonify({"message": "Questions reordered successfully"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Reorder questions error: {str(e)}")
        return jsonify({"error": str(e)}), 400

# -------------------- Bulk Option Import --------------------
@form_bp.route("/<form_id>/section/<section_id>/question/<question_id>/options/import", methods=["POST"])
@jwt_required()
def bulk_import_options(form_id, section_id, question_id):
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized to edit form"}), 403

        replace = request.args.get("replace", "false").lower() == "true"
        v_str = request.args.get("v")
        file = request.files.get("file")
        
        if not file:
            return jsonify({"error": "No file uploaded"}), 400
            
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        
        new_options = []
        for row in reader:
            label = row.get("label") or row.get("option_label")
            value = row.get("value") or row.get("option_value") or label
            
            if label:
                new_options.append(Option(
                    option_label=label,
                    option_value=value,
                    description=row.get("description", "")
                ))

        if not new_options:
            return jsonify({"error": "No valid options found in CSV. Required headers: 'label', 'value' (optional)"}), 400

        if not form.versions:
            return jsonify({"error": "Form has no versions"}), 400
            
        # Find target version
        if v_str:
            target_version = next((v for v in form.versions if v.version == v_str), None)
            if not target_version:
                return jsonify({"error": f"Version {v_str} not found"}), 404
        else:
            target_version = form.versions[-1]
            
        target_question = None
        for s in target_version.sections:
            if str(s.id) == section_id:
                for q in s.questions:
                    if str(q.id) == question_id:
                        target_question = q
                        break
                if target_question: break
                
        if not target_question:
            return jsonify({"error": "Question not found"}), 404

        if replace:
            target_question.options = new_options
        else:
            target_question.options.extend(new_options)
            
        form.save()
        return jsonify({"message": f"Imported {len(new_options)} options"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# -------------------- Version Management --------------------

@form_bp.route("/<form_id>/versions", methods=["POST"])
@jwt_required()
def create_new_version(form_id):
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized"}), 403
            
        data = request.get_json()
        new_v_str = data.get("version")
        sections_data = data.get("sections")
        
        if not new_v_str or not sections_data:
            return jsonify({"error": "Missing version string or sections"}), 400
            
        # Check if version string already exists
        if any(v.version == new_v_str for v in form.versions):
            return jsonify({"error": f"Version {new_v_str} already exists"}), 400
            
        from app.schemas.form_schema import FormVersionSchema
        from app.models.Form import FormVersion
        
        version_dict = FormVersionSchema().load(data)
        # FormVersionSchema load returns a dict, if we want the actual model we might need to instantiate or use it directly
        # Actually our schema is configured to return dict or objects based on meta. We'll use dict and cast if needed or just use current pattern.
        # Let's check how other routes do it. Usually they use data directly for EmbeddedDocument if structure matches.
        
        form.update(push__versions=version_dict)
        
        # Reload to handle activation
        form.reload()
        if data.get("activate", False):
            form.active_version = new_v_str
            form.save()
            
        return jsonify({"message": f"Version {new_v_str} created"}), 201
        
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@form_bp.route("/<form_id>/versions", methods=["GET"])
@jwt_required()
def list_form_versions(form_id):
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403
            
        versions = []
        for v in form.versions:
            v_dict = v.to_mongo().to_dict()
            versions.append(v_dict)
            
        return jsonify(versions), 200
        
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_bp.route("/<form_id>/versions/<v_str>/activate", methods=["PATCH"])
@jwt_required()
def activate_version(form_id, v_str):
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized"}), 403
            
        version_exists = any(v.version == v_str for v in form.versions)
        if not version_exists:
            return jsonify({"error": "Version not found"}), 404
            
        form.active_version = v_str
        form.save()
        return jsonify({"message": f"Version {v_str} is now active"}), 200
        
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_bp.route("/<form_id>/versions/<v_str>", methods=["GET"])
@jwt_required()
def get_form_version(form_id, v_str):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403

        version = next((v for v in form.versions if v.version == v_str), None)
        if not version:
            return jsonify({"error": "Version not found"}), 404

        return jsonify(version.to_mongo().to_dict()), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_bp.route("/<form_id>/versions/<v_str>", methods=["PUT"])
@jwt_required()
def update_form_version(form_id, v_str):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        
        # Find the index of the version to update
        version_idx = next((i for i, v in enumerate(form.versions) if v.version == v_str), None)
        if version_idx is None:
            return jsonify({"error": "Version not found"}), 404

        # Validate data using schema
        from app.schemas.form_schema import FormVersionSchema
        from app.models.Form import FormVersion
        
        # We might need to handle the case where version ID (v_str) is being updated in the data
        # But usually version string should be the identifier provided.
        # Ensure the 'version' in data matches v_str or we allow renaming?
        # For simplicity, we use v_str as the identifier and let data override it if present.
        
        version_dict = FormVersionSchema().load(data)
        
        # Update the version in the list
        update_key = f"set__versions__{version_idx}"
        form.update(**{update_key: version_dict})
        
        # If this was the active version and the version string changed, update active_version
        if form.active_version == v_str and version_dict.get("version") != v_str:
            form.update(active_version=version_dict.get("version"))

        return jsonify({"message": f"Version {v_str} updated"}), 200
        
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        import traceback
        current_app.logger.error(f"Update version error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 400


