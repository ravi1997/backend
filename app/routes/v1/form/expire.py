
from datetime import datetime, timezone
from app.models.User import Role
from app.routes.v1.form.helper import get_current_user, has_form_permission
from app.routes.v1.form import form_bp
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from mongoengine import DoesNotExist
from app.models import Form
from app.utils.decorator import require_roles
from app.models.Form import Form

# -------------------- Schedule Form Expiration --------------------
@form_bp.route("/<form_id>/expire", methods=["PATCH"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def set_form_expiration(form_id):
    data = request.get_json()
    try:
        form = Form.objects.get(id=form_id)
        expiration_date = data.get("expires_at")
        if not expiration_date:
            return jsonify({"error": "Expiration date is required"}), 400
        form.update(set__expires_at=expiration_date)
        return jsonify({"message": "Form expiration updated"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_bp.route("/expired", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def list_expired_forms():
    now = datetime.now(timezone.utc)
    expired_forms = Form.objects(expires_at__lt=now)
    return jsonify([f.to_mongo().to_dict() for f in expired_forms]), 200