# routes/user_routes.py

from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required
from app.routes.v1.form.helper import get_current_user
from app.schemas.user_schema import UserSchema
from app.utils.decorator import require_roles
from app.models.User import User, UserType, Role, MAX_OTP_RESENDS, PASSWORD_EXPIRATION_DAYS
from mongoengine.errors import NotUniqueError, ValidationError
from functools import wraps
from datetime import datetime, timedelta, timezone
import uuid

user_bp = Blueprint("user_bp", __name__)

# ─── Auth Endpoints ─────────────────────────────────────


@user_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    data = request.json or {}
    user = get_current_user()
    if not user.check_password(data.get("current_password", "")):
        return jsonify({"message": "Current password incorrect"}), 400
    user.set_password(data.get("new_password"))
    user.save()
    return jsonify({"message": "Password changed"}), 200


@user_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json or {}
    user = None
    if data.get("otp"):
        user = User.objects(mobile=data.get("mobile")).first()
        if not user or not user.verify_otp(data["otp"]):
            return jsonify({"message": "Invalid OTP"}), 400
    else:
        user = User.objects(id=data.get("user_id")).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    user.set_password(data.get("new_password"))
    user.save()
    return jsonify({"message": "Password reset"}), 200


@user_bp.route("/unlock", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def auth_unlock():
    data = request.json or {}
    user = User.objects(id=data.get("user_id")).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.unlock_account()
    return jsonify({"message": f"User {user.id} unlocked"}), 200


@user_bp.route("/status", methods=["GET"])
@jwt_required()
def auth_status():
    current_user = get_current_user()
    return jsonify({"user": UserSchema().dump(current_user)}), 200

# ─── CRUD Endpoints ─────────────────────────────────────


@user_bp.route("/users", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def list_users():
    q = User.objects
    return jsonify([u.to_dict() for u in q]), 200


@user_bp.route("/users/<user_id>", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def get_user(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user.to_dict()), 200


@user_bp.route("/users", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def create_user():
    data = request.json or {}
    try:
        user_data = {k: v for k, v in data.items() if k != "password"}
        user = User(**user_data)
        if data.get("password"):
            user.set_password(data["password"])
        user.save()
        return jsonify(user.to_dict()), 201
    except (NotUniqueError, ValidationError) as err:
        return jsonify({"message": str(err)}), 400


@user_bp.route("/users/<user_id>", methods=["PUT"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def update_user(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    data = request.json or {}
    user.modify(**data)
    user.save()
    return jsonify(user.to_dict()), 200


@user_bp.route("/users/<user_id>", methods=["DELETE"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def delete_user(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.delete()
    return jsonify({"message": "User deleted"}), 200


@user_bp.route("/users/<user_id>/lock", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def lock_user(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.lock_account()
    return jsonify({"message": f"User {user.id} locked"}), 200


@user_bp.route("/users/<user_id>/unlock", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def unlock_user(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.unlock_account()
    return jsonify({"message": f"User {user.id} unlocked"}), 200


@user_bp.route("/users/<user_id>/reset-otp-count", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def reset_otp_count(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.otp_resend_count = 0
    user.save()
    return jsonify({"message": f"OTP count reset for {user.id}"}), 200

# ─── Security Endpoints ─────────────────────────────────


@user_bp.route("/security/extend-password-expiry", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def extend_password_expiry():
    data = request.json or {}
    uid = data.get("user_id")
    days = data.get("days", PASSWORD_EXPIRATION_DAYS)
    user = User.objects(id=uid).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.password_expiration = datetime.now(
        timezone.utc) + timedelta(days=days)
    user.save()
    return jsonify({"message": "Password expiry extended"}), 200


@user_bp.route("/security/lock-status/<user_id>", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def lock_status(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"locked": user.is_locked()}), 200


@user_bp.route("/security/resend-otp", methods=["POST"])
def resend_otp():
    data = request.json or {}
    mobile = data.get("mobile")
    user = User.objects(mobile=mobile).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    if user.is_locked():
        return jsonify({"message": "Account locked"}), 403
    user.resend_otp()
    user.save()
    otp = user.otp
    return jsonify({"message": "OTP resent", "otp": otp}), 200
