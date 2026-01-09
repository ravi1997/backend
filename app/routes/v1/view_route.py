from flask import Blueprint, current_app, render_template, request, jsonify
from app.routes.v1.form.helper import apply_translations
from app.config import Config
from app.models import Form
from app.models.User import User
from app.models.TokenBlocklist import TokenBlocklist
from app.schemas.user_schema import UserSchema
from flask_jwt_extended import (
    create_access_token, jwt_required,
    get_jwt, set_access_cookies, unset_jwt_cookies
)
from app.utils.decorator import require_roles
from mongoengine import DoesNotExist
view_bp = Blueprint('view_bp', __name__)



# -------------------- index --------------------
@view_bp.route("/", methods=["GET"])
def index():
    try:
        return render_template("login.html")
    except DoesNotExist:
        return "Form not found", 404



@view_bp.route("/<id>", methods=["GET"])
def view_form(id):
    try:
        form = Form.objects.get(id=id)
        lang = request.args.get("lang")
        form_dict = form.to_mongo().to_dict()
        if lang:
            form_dict = apply_translations(form_dict, lang)
        return render_template("view.html", form=form_dict)
    except DoesNotExist:
        return "Form not found", 404