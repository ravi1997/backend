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
import logging
import uuid
from mongoengine import DoesNotExist

view_bp = Blueprint('view_bp', __name__)
logger = logging.getLogger(__name__)



# -------------------- index --------------------
@view_bp.route("/", methods=["GET"])
def index():
    logger.info("--- View Index branch started ---")
    try:
        return render_template("login.html")
    except DoesNotExist:
        logger.error("Login template not found (DoesNotExist)")
        return "Form not found", 404



@view_bp.route("/<id>", methods=["GET"])
def view_form(id):
    logger.info(f"--- View Form branch started for id: {id} ---")
    try:
        form = Form.objects.get(id=id)
        lang = request.args.get("lang")
        form_dict = form.to_mongo().to_dict()
        if lang:
            logger.info(f"Applying translations for language: {lang}")
            form_dict = apply_translations(form_dict, lang)
        else:
            logger.debug("No language specified, using default")
        return render_template("view.html", form=form_dict)
    except DoesNotExist:
        logger.warning(f"View Form failed: ID {id} not found")
        return "Form not found", 404