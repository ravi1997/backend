
# -------------------- Helper --------------------
from flask_jwt_extended import get_jwt_identity

from app.models.User import User


def get_current_user():
    user_id = get_jwt_identity()
    return User.objects(id=user_id).first()


def has_form_permission(user, form, action):
    user_id_str = str(user.id)
    if user.is_superadmin_check():
        return True

    # Creator always has all permissions
    if str(form.created_by) == user_id_str:
        return True

    if action == "edit":
        return user_id_str in (form.editors or [])
    if action == "view":
        return user_id_str in (form.viewers or []) or user_id_str in (form.editors or [])
    if action == "submit":
        return user_id_str in (form.submitters or []) or form.is_public
    return False