
from app.routes.v1.form.helper import get_current_user, has_form_permission
from app.routes.v1.form import form_bp
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongoengine import DoesNotExist
from app.models import Form
from app.models.User import Role
from app.utils.decorator import require_roles
from app.models.Form import Form, FormResponse

# -------------------- Additional Functional Routes --------------------

@form_bp.route("/<form_id>/publish", methods=["PATCH"])
@jwt_required()
@require_roles(Role.EDITOR.value, Role.ADMIN.value)
def publish_form(form_id):
    try:
        form = Form.objects.get(id=form_id)
        form.update(status="published")
        return jsonify({"message": "Form published"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404


@form_bp.route("/slug-available", methods=["GET"])
@jwt_required()
def check_slug():
    slug = request.args.get("slug")
    exists = Form.objects(slug=slug).first() is not None
    return jsonify({"available": not exists}), 200


@form_bp.route("/<form_id>/clone", methods=["POST"])
@jwt_required()
def clone_form(form_id):
    try:
        original = Form.objects.get(id=form_id)
        current_user = get_current_user()
        new_form = Form(
            title=original.title + " (Clone)",
            description=original.description,
            slug=original.slug + "-copy",
            created_by=str(current_user.id),
            editors=[str(current_user.id)],
            view=original.view,
            sections=original.sections,
            response_templates=original.response_templates,
            is_public=False,
        )
        new_form.save()
        return jsonify({"message": "Form cloned", "new_form_id": new_form.id}), 201
    except DoesNotExist:
        return jsonify({"error": "Original form not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_bp.route("/<form_id>/share", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def share_form(form_id):
    data = request.get_json()
    try:
        form = Form.objects.get(id=form_id)
        form.update(
            add_to_set__editors=data.get("editors", []),
            add_to_set__viewers=data.get("viewers", []),
            add_to_set__submitters=data.get("submitters", [])
        )
        return jsonify({"message": "Permissions updated"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404


@form_bp.route("/<form_id>/archive", methods=["PATCH"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def archive_form(form_id):
    try:
        form = Form.objects.get(id=form_id)
        form.update(set__status="archived")
        return jsonify({"message": "Form archived"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

@form_bp.route("/<form_id>/restore", methods=["PATCH"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def restore_form(form_id):
    try:
        form = Form.objects.get(id=form_id, status="archived")
        form.update(set__status="draft")
        return jsonify({"message": "Form restored"}), 200
    except DoesNotExist:
        return jsonify({"error": "Archived form not found"}), 404
    

# -------------------- Delete All Responses --------------------
@form_bp.route("/<form_id>/responses", methods=["DELETE"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def delete_all_responses(form_id):
    try:
        form = Form.objects.get(id=form_id)
        deleted_count = FormResponse.objects(form=form).delete()
        return jsonify({"message": f"Deleted {deleted_count} responses"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

# -------------------- Toggle Public Access --------------------
@form_bp.route("/<form_id>/toggle-public", methods=["PATCH"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def toggle_form_public(form_id):
    try:
        form = Form.objects.get(id=form_id)
        form.is_public = not form.is_public
        form.save()
        return jsonify({"message": "Form public access toggled", "is_public": form.is_public}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

# -------------------- Count Responses for Form --------------------
@form_bp.route("/<form_id>/responses/count", methods=["GET"])
@jwt_required()
def count_responses(form_id):
    try:
        form = Form.objects.get(id=form_id)
        count = FormResponse.objects(form=form).count()
        return jsonify({"form_id": form_id, "response_count": count}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

# -------------------- Get Last Submission --------------------
@form_bp.route("/<form_id>/responses/last", methods=["GET"])
@jwt_required()
def last_response(form_id):
    try:
        form = Form.objects.get(id=form_id)
        response = FormResponse.objects(form=form).order_by("-submitted_at").first()
        if response:
            return jsonify(response.to_mongo().to_dict()), 200
        return jsonify({"message": "No responses found"}), 404
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

# -------------------- Duplicate Check for Response --------------------
@form_bp.route("/<form_id>/check-duplicate", methods=["POST"])
@jwt_required()
def check_duplicate_submission(form_id):
    data = request.get_json()
    submitted_by = str(get_jwt_identity())
    try:
        form = Form.objects.get(id=form_id)
        exists = FormResponse.objects(form=form, submitted_by=submitted_by, data=data.get("data")).first()
        return jsonify({"duplicate": exists is not None}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
