
# -------------------- Helper --------------------
from flask_jwt_extended import get_jwt_identity

from app.models.User import User


def get_current_user():
    user_id = get_jwt_identity()
    return User.objects(id=user_id).first()


def has_form_permission(user, form, action):
    if user.is_superadmin_check():
        return True
    if action == "edit":
        return user.id in form.editors
    if action == "view":
        return user.id in form.viewers or user.id in form.editors
    if action == "submit":
        return user.id in form.submitters or form.is_public