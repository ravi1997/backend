from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.SystemSettings import SystemSettings
from app.models.User import Role
from app.utils.decorator import require_roles
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

system_settings_bp = Blueprint("system_settings", __name__)

# ── Allowed fields and their types for validation ──────────────────────────────

INT_FIELDS = {
    'jwt_access_token_expires_minutes',
    'jwt_refresh_token_expires_days',
    'max_failed_login_attempts',
    'account_lock_duration_hours',
    'password_expiration_days',
    'otp_expiration_minutes',
    'max_otp_resends',
    'max_upload_size_mb',
    'cache_default_ttl_seconds',
    'cache_form_schema_ttl_seconds',
    'cache_user_session_ttl_seconds',
    'cache_query_result_ttl_seconds',
    'cache_dashboard_widget_ttl_seconds',
    'cache_api_response_ttl_seconds',
    'ollama_pool_size',
    'ollama_pool_timeout_seconds',
    'ollama_connection_timeout_seconds',
    'redis_port',
    'redis_db',
    'redis_max_connections',
    'redis_socket_timeout_seconds',
    'rate_limit_requests_per_minute',
}

BOOL_FIELDS = {
    'cache_enabled',
    'cors_enabled',
    'debug_mode',
    'rate_limit_enabled',
}

STR_FIELDS = {
    'allowed_upload_extensions',
    'llm_provider',
    'llm_api_url',
    'llm_model',
    'ollama_api_url',
    'ollama_embedding_model',
    'redis_host',
}

ALL_EDITABLE = INT_FIELDS | BOOL_FIELDS | STR_FIELDS


# ── GET /api/v1/admin/system-settings/ ────────────────────────────────────────

@system_settings_bp.route("/", methods=["GET"])
@jwt_required()
@require_roles(Role.SUPERADMIN.value)
def get_settings():
    """
    Return the current system settings document (superadmin only).
    Creates the default document on first call.
    """
    settings = SystemSettings.get_or_create_default()
    return jsonify(settings.to_dict()), 200


# ── PATCH /api/v1/admin/system-settings/ ──────────────────────────────────────

@system_settings_bp.route("/", methods=["PATCH"])
@jwt_required()
@require_roles(Role.SUPERADMIN.value)
def update_settings():
    """
    Update one or more system settings fields.
    Body: { "field_name": value, ... }

    Only fields in the allow-list can be updated; unknown keys are ignored.
    """
    data = request.get_json(silent=True) or {}
    admin_id = get_jwt_identity()

    settings = SystemSettings.get_or_create_default()
    updated_keys = []
    errors = []

    for key, value in data.items():
        if key not in ALL_EDITABLE:
            continue  # silently ignore non-editable keys

        if key in INT_FIELDS:
            try:
                value = int(value)
                if value < 0:
                    errors.append(f"{key}: must be a non-negative integer")
                    continue
            except (TypeError, ValueError):
                errors.append(f"{key}: expected integer, got {type(value).__name__}")
                continue

        elif key in BOOL_FIELDS:
            if not isinstance(value, bool):
                errors.append(f"{key}: expected boolean")
                continue

        elif key in STR_FIELDS:
            if not isinstance(value, str):
                errors.append(f"{key}: expected string")
                continue

        setattr(settings, key, value)
        updated_keys.append(key)

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    if not updated_keys:
        return jsonify({"message": "No valid fields to update"}), 200

    settings.updated_by = admin_id
    settings.save()

    logger.info(f"System settings updated by admin {admin_id}: {updated_keys}")

    # Apply JWT expiry dynamically to current app config so new tokens pick it up
    try:
        new_access_minutes = settings.jwt_access_token_expires_minutes
        new_refresh_days = settings.jwt_refresh_token_expires_days
        current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=new_access_minutes)
        current_app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=new_refresh_days)
        logger.info(
            f"JWT token expiry updated in app config: "
            f"access={new_access_minutes}m, refresh={new_refresh_days}d"
        )
    except Exception as e:
        logger.warning(f"Could not apply JWT expiry to app config: {e}")

    return jsonify({
        "message": f"Updated {len(updated_keys)} setting(s)",
        "updated_keys": updated_keys,
        "settings": settings.to_dict(),
    }), 200


# ── POST /api/v1/admin/system-settings/reset ──────────────────────────────────

@system_settings_bp.route("/reset", methods=["POST"])
@jwt_required()
@require_roles(Role.SUPERADMIN.value)
def reset_settings():
    """
    Reset all system settings to their factory defaults.
    """
    admin_id = get_jwt_identity()
    settings = SystemSettings.get_or_create_default()
    settings.delete()

    # Re-create fresh default doc
    settings = SystemSettings.get_or_create_default()
    settings.updated_by = admin_id
    settings.save()

    logger.warning(f"System settings RESET to defaults by admin {admin_id}")
    return jsonify({
        "message": "Settings reset to factory defaults",
        "settings": settings.to_dict(),
    }), 200
