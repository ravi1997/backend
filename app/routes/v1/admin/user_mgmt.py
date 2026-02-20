from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.User import User, Role
from app.utils.decorator import require_roles
from app.routes.v1.form.helper import get_current_user
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

user_mgmt_bp = Blueprint("user_mgmt", __name__)


# ─── List All Users ────────────────────────────────────────────────────────────

@user_mgmt_bp.route("/", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def list_users_admin():
    """
    List all users with their departments and roles.
    Supports optional ?department=<str>&role=<str>&status=active|inactive query params.
    """
    department = request.args.get("department")
    role_filter = request.args.get("role")
    status_filter = request.args.get("status")  # "active" | "inactive"

    q = User.objects()

    if department:
        q = q.filter(department=department)
    if role_filter:
        q = q.filter(roles=role_filter)
    if status_filter == "active":
        q = q.filter(is_active=True)
    elif status_filter == "inactive":
        q = q.filter(is_active=False)

    return jsonify([u.to_dict() for u in q]), 200


# ─── Get Single User ───────────────────────────────────────────────────────────

@user_mgmt_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def get_user_admin(user_id):
    """
    Return full profile of a single user (admin view).
    """
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200


# ─── Update Department ─────────────────────────────────────────────────────────

@user_mgmt_bp.route("/<user_id>/department", methods=["PATCH"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def update_user_department(user_id):
    """
    Update a specific user's department.
    """
    data = request.get_json()
    department = data.get("department")

    if department is None:
        return jsonify({"error": "Department is required"}), 400

    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.department = department
    user.save()

    return jsonify({
        "message": f"User {user.username} department updated to {department}",
        "user": user.to_dict()
    }), 200


# ─── Update Roles ──────────────────────────────────────────────────────────────

@user_mgmt_bp.route("/<user_id>/roles", methods=["PATCH"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def update_user_roles(user_id):
    """
    Replace the full roles list for a user.
    Body: { "roles": ["admin", "creator", ...] }
    """
    data = request.get_json()
    roles = data.get("roles")

    if roles is None or not isinstance(roles, list):
        return jsonify({"error": "roles must be a list"}), 400

    valid_roles = [r.value for r in Role]
    invalid = [r for r in roles if r not in valid_roles]
    if invalid:
        return jsonify({"error": f"Invalid roles: {invalid}. Valid: {valid_roles}"}), 400

    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.roles = roles
    user.save()

    logger.info(f"Roles for user {user_id} updated to {roles} by admin")
    return jsonify({
        "message": f"Roles updated for {user.username}",
        "user": user.to_dict()
    }), 200


# ─── Reset Password ────────────────────────────────────────────────────────────

@user_mgmt_bp.route("/<user_id>/reset-password", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def admin_reset_password(user_id):
    """
    Admin-force-reset a user's password.
    Body: { "new_password": string }
    """
    data = request.get_json()
    new_password = data.get("new_password")

    if not new_password or len(new_password) < 6:
        return jsonify({"error": "new_password must be at least 6 characters"}), 400

    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.set_password(new_password)
    user.failed_login_attempts = 0
    user.lock_until = None
    user.save()

    logger.info(f"Password force-reset for user {user_id} by admin")
    return jsonify({"message": f"Password reset for {user.username}"}), 200


# ─── Lock / Unlock ─────────────────────────────────────────────────────────────

@user_mgmt_bp.route("/<user_id>/lock", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def admin_lock_user(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.lock_account()
    logger.info(f"User {user_id} locked by admin")
    return jsonify({"message": f"User {user.username} locked", "user": user.to_dict()}), 200


@user_mgmt_bp.route("/<user_id>/unlock", methods=["POST"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def admin_unlock_user(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.unlock_account()
    logger.info(f"User {user_id} unlocked by admin")
    return jsonify({"message": f"User {user.username} unlocked", "user": user.to_dict()}), 200


# ─── Toggle Active Status ──────────────────────────────────────────────────────

@user_mgmt_bp.route("/<user_id>/status", methods=["PATCH"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def toggle_user_active(user_id):
    """
    Activate or deactivate a user.
    Body: { "is_active": bool }
    """
    data = request.get_json()
    if "is_active" not in data:
        return jsonify({"error": "is_active field is required"}), 400

    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_active = bool(data["is_active"])
    user.save()
    state = "activated" if user.is_active else "deactivated"
    logger.info(f"User {user_id} {state} by admin")
    return jsonify({"message": f"User {user.username} {state}", "user": user.to_dict()}), 200


# ─── Delete User ───────────────────────────────────────────────────────────────

@user_mgmt_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def delete_user_admin(user_id):
    """
    Permanently delete a user. Only superadmins should do this.
    """
    current_admin = get_current_user()

    # Prevent self-deletion
    if str(current_admin.id) == str(user_id):
        return jsonify({"error": "You cannot delete your own account"}), 403

    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    username = user.username
    user.delete()
    logger.warning(f"User {user_id} ({username}) deleted by admin {current_admin.id}")
    return jsonify({"message": f"User '{username}' permanently deleted"}), 200


# ─── Activity / Security Summary ──────────────────────────────────────────────

@user_mgmt_bp.route("/<user_id>/activity", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def get_user_activity(user_id):
    """
    Return a timeline of security-relevant events for a user.
    This is synthesised from stored fields; a proper audit log would need a
    dedicated collection. For now we surface what the model already tracks.
    """
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    def iso(dt):
        return dt.isoformat() if dt else None

    events = []

    if user.created_at:
        events.append({
            "type": "account_created",
            "label": "Account Created",
            "timestamp": iso(user.created_at),
            "icon": "person_add",
            "color": "blue",
        })

    if user.last_login:
        events.append({
            "type": "last_login",
            "label": "Last Login",
            "timestamp": iso(user.last_login),
            "icon": "login",
            "color": "green",
        })

    if user.lock_until:
        lock_until_aware = user.lock_until
        if lock_until_aware.tzinfo is None:
            lock_until_aware = lock_until_aware.replace(tzinfo=timezone.utc)
        is_currently_locked = datetime.now(timezone.utc) < lock_until_aware
        events.append({
            "type": "account_locked",
            "label": "Account Locked" if is_currently_locked else "Account Was Locked",
            "timestamp": iso(user.lock_until),
            "icon": "lock",
            "color": "red" if is_currently_locked else "orange",
            "detail": f"Lock expires: {iso(user.lock_until)}",
        })

    if user.password_expiration:
        pw_exp = user.password_expiration
        if pw_exp.tzinfo is None:
            pw_exp = pw_exp.replace(tzinfo=timezone.utc)
        expired = datetime.now(timezone.utc) > pw_exp
        events.append({
            "type": "password_expiry",
            "label": "Password Expired" if expired else "Password Expiry",
            "timestamp": iso(user.password_expiration),
            "icon": "key_off" if expired else "key",
            "color": "red" if expired else "gray",
        })

    if user.updated_at and user.updated_at != user.created_at:
        events.append({
            "type": "profile_updated",
            "label": "Profile Last Updated",
            "timestamp": iso(user.updated_at),
            "icon": "edit",
            "color": "purple",
        })

    # Sort newest first
    events.sort(key=lambda e: e["timestamp"] or "", reverse=True)

    return jsonify({
        "user_id": user_id,
        "username": user.username,
        "failed_login_attempts": user.failed_login_attempts,
        "otp_resend_count": user.otp_resend_count,
        "is_locked": user.is_locked(),
        "is_password_expired": user.is_password_expired(),
        "events": events,
    }), 200


# ─── List Departments ──────────────────────────────────────────────────────────

@user_mgmt_bp.route("/departments", methods=["GET"])
@jwt_required()
@require_roles(Role.ADMIN.value, Role.SUPERADMIN.value)
def list_departments():
    """
    List all unique departments currently assigned to users.
    """
    departments = User.objects.distinct("department")
    departments = [d for d in departments if d]
    return jsonify(departments), 200
