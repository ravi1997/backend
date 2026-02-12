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
import logging

user_bp = Blueprint("user_bp", __name__)
logger = logging.getLogger(__name__)

# ─── Auth Endpoints ─────────────────────────────────────


@user_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    logger.info("--- Change Password branch started ---")
    data = request.json or {}
    user = get_current_user()
    if not user.check_password(data.get("current_password", "")):
        logger.warning(f"Change password failed: Current password incorrect for user: {user.id}")
        return jsonify({"message": "Current password incorrect"}), 400
    user.set_password(data.get("new_password"))
    user.save()
    logger.info(f"Password changed successfully for user: {user.id}")
    return jsonify({"message": "Password changed"}), 200


@user_bp.route("/reset-password", methods=["POST"])
def reset_password():
    logger.info("--- Reset Password branch started ---")
    data = request.json or {}
    user = None
    if data.get("otp"):
        logger.debug(f"Attempting password reset via OTP for mobile: {data.get('mobile')}")
        user = User.objects(mobile=data.get("mobile")).first()
        if not user or not user.verify_otp(data["otp"]):
            logger.warning(f"Reset password failed: Invalid OTP/User not found for mobile {data.get('mobile')}")
            return jsonify({"message": "Invalid OTP"}), 400
        logger.info(f"OTP verified for user: {user.id}")
    else:
        logger.debug(f"Attempting password reset via user_id: {data.get('user_id')}")
        user = User.objects(id=data.get("user_id")).first()
        if not user:
            logger.warning(f"Reset password failed: User ID {data.get('user_id')} not found")
            return jsonify({"message": "User not found"}), 404

    user.set_password(data.get("new_password"))
    user.save()
    logger.info(f"Password reset successfully for user: {user.id}")
    return jsonify({"message": "Password reset"}), 200


@user_bp.route("/unlock", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def auth_unlock():
    logger.info("--- Auth Unlock branch started ---")
    data = request.json or {}
    user = User.objects(id=data.get("user_id")).first()
    if not user:
        logger.warning(f"Unlock failed: User ID {data.get('user_id')} not found")
        return jsonify({"message": "User not found"}), 404
    user.unlock_account()
    logger.info(f"User {user.id} account unlocked via admin")
    return jsonify({"message": f"User {user.id} unlocked"}), 200


@user_bp.route("/status", methods=["GET"])
@jwt_required()
def auth_status():
    logger.info("--- Auth Status branch started ---")
    current_user = get_current_user()
    logger.info(f"Returning status for user: {current_user.id}")
    return jsonify({"user": UserSchema().dump(current_user)}), 200

# ─── CRUD Endpoints ─────────────────────────────────────


@user_bp.route("/users", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def list_users():
    logger.info("--- List Users branch started ---")
    q = User.objects
    logger.info(f"Listing all users, count: {q.count()}")
    return jsonify([u.to_dict() for u in q]), 200


@user_bp.route("/users/<user_id>", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def get_user(user_id):
    logger.info(f"--- Get User branch started for id: {user_id} ---")
    user = User.objects(id=user_id).first()
    if not user:
        logger.warning(f"Get User failed: ID {user_id} not found")
        return jsonify({"message": "User not found"}), 404
    logger.info(f"Returning details for user: {user_id}")
    return jsonify(user.to_dict()), 200


@user_bp.route("/users", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def create_user():
    logger.info("--- Create User branch started ---")
    data = request.json or {}
    try:
        user_data = {k: v for k, v in data.items() if k != "password"}
        user = User(**user_data)
        if data.get("password"):
            logger.debug(f"Setting password for new user: {user.username}")
            user.set_password(data["password"])
        user.save()
        logger.info(f"User created successfully: {user.username} (ID: {user.id})")
        return jsonify(user.to_dict()), 201
    except (NotUniqueError, ValidationError) as err:
        logger.warning(f"Create User failed: Validation/Unique constraint error: {err}")
        return jsonify({"message": str(err)}), 400


@user_bp.route("/users/<user_id>", methods=["PUT"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def update_user(user_id):
    logger.info(f"--- Update User branch started for id: {user_id} ---")
    user = User.objects(id=user_id).first()
    if not user:
        logger.warning(f"Update User failed: ID {user_id} not found")
        return jsonify({"message": "User not found"}), 404
    data = request.json or {}
    logger.info(f"Updating user {user_id} with data: {data}")
    user.modify(**data)
    user.save()
    logger.info(f"User {user_id} updated successfully")
    return jsonify(user.to_dict()), 200


@user_bp.route("/users/<user_id>", methods=["DELETE"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def delete_user(user_id):
    logger.info(f"--- Delete User branch started for id: {user_id} ---")
    user = User.objects(id=user_id).first()
    if not user:
        logger.warning(f"Delete User failed: ID {user_id} not found")
        return jsonify({"message": "User not found"}), 404
    user.delete()
    logger.info(f"User {user_id} deleted successfully")
    return jsonify({"message": "User deleted"}), 200


@user_bp.route("/users/<user_id>/lock", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def lock_user(user_id):
    logger.info(f"--- Lock User branch started for id: {user_id} ---")
    user = User.objects(id=user_id).first()
    if not user:
        logger.warning(f"Lock User failed: ID {user_id} not found")
        return jsonify({"message": "User not found"}), 404
    user.lock_account()
    logger.info(f"User {user_id} account locked successfully")
    return jsonify({"message": f"User {user.id} locked"}), 200


@user_bp.route("/users/<user_id>/unlock", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def unlock_user(user_id):
    logger.info(f"--- Unlock User branch started for id: {user_id} ---")
    user = User.objects(id=user_id).first()
    if not user:
        logger.warning(f"Unlock User failed: ID {user_id} not found")
        return jsonify({"message": "User not found"}), 404
    user.unlock_account()
    logger.info(f"User {user_id} account unlocked successfully")
    return jsonify({"message": f"User {user.id} unlocked"}), 200


@user_bp.route("/users/<user_id>/reset-otp-count", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def reset_otp_count(user_id):
    logger.info(f"--- Reset OTP Count branch started for id: {user_id} ---")
    user = User.objects(id=user_id).first()
    if not user:
        logger.warning(f"Reset OTP Count failed: ID {user_id} not found")
        return jsonify({"message": "User not found"}), 404
    user.otp_resend_count = 0
    user.save()
    logger.info(f"OTP resend count reset successfully for user: {user_id}")
    return jsonify({"message": f"OTP count reset for {user.id}"}), 200

# ─── Security Endpoints ─────────────────────────────────


@user_bp.route("/security/extend-password-expiry", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def extend_password_expiry():
    logger.info("--- Extend Password Expiry branch started ---")
    data = request.json or {}
    uid = data.get("user_id")
    days = data.get("days", PASSWORD_EXPIRATION_DAYS)
    user = User.objects(id=uid).first()
    if not user:
        logger.warning(f"Extend Password Expiry failed: User ID {uid} not found")
        return jsonify({"message": "User not found"}), 404
    user.password_expiration = datetime.now(
        timezone.utc) + timedelta(days=days)
    user.save()
    logger.info(f"Password expiry extended by {days} days for user: {uid}")
    return jsonify({"message": "Password expiry extended"}), 200


@user_bp.route("/security/lock-status/<user_id>", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def lock_status(user_id):
    logger.info(f"--- Lock Status Check branch started for id: {user_id} ---")
    user = User.objects(id=user_id).first()
    if not user:
        logger.warning(f"Lock Status Check failed: ID {user_id} not found")
        return jsonify({"message": "User not found"}), 404
    status = user.is_locked()
    logger.info(f"Lock status for user {user_id}: {status}")
    return jsonify({"locked": status}), 200


@user_bp.route("/security/resend-otp", methods=["POST"])
def resend_otp():
    logger.info("--- Resend OTP branch started ---")
    data = request.json or {}
    mobile = data.get("mobile")
    user = User.objects(mobile=mobile).first()
    if not user:
        logger.warning(f"Resend OTP failed: Mobile {mobile} not found")
        return jsonify({"message": "User not found"}), 404
    if user.is_locked():
        logger.warning(f"Resend OTP failed: User account {mobile} is locked")
        return jsonify({"message": "Account locked"}), 403
    logger.info(f"Resending OTP for user: {user.id}")
    user.resend_otp()
    user.save()
    otp = user.otp
    logger.info("OTP resent successfully")
    return jsonify({"message": "OTP resent", "otp": otp}), 200
