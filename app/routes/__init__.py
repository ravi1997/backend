from app.routes.v1.form import form_bp
from app.routes.v1.auth_route import auth_bp
from app.routes.v1.form.routes import *
from app.routes.v1.view_route import view_bp
from app.routes.v1.user_route import user_bp
from app.routes.v1.form.ai import ai_bp
from app.routes.v1.form.library import library_bp
from app.routes.v1.form.permissions import permissions_bp
from app.routes.v1.dashboard_route import dashboard_bp 
from app.routes.v1.workflow_route import workflow_bp

def register_blueprints(app):
    app.register_blueprint(form_bp, url_prefix='/form/api/v1/form')
    app.register_blueprint(library_bp, url_prefix='/form/api/v1/field-library')
    app.register_blueprint(permissions_bp, url_prefix='/form/api/v1/form')
    app.register_blueprint(view_bp, url_prefix='/form/')
    app.register_blueprint(user_bp, url_prefix='/form/api/v1/user')
    app.register_blueprint(auth_bp, url_prefix='/form/api/v1/auth')
    app.register_blueprint(ai_bp, url_prefix='/form/api/v1/ai')
    app.register_blueprint(dashboard_bp, url_prefix='/form/api/v1/dashboards')
    app.register_blueprint(workflow_bp, url_prefix='/form/api/v1/workflows')
    app.logger.info("Blueprints registered: form, user, auth, ai, dashboards, workflows")