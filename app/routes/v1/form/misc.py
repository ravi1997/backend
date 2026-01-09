
from datetime import datetime, timezone
from app.routes.v1.form.helper import get_current_user, has_form_permission
from app.routes.v1.form import form_bp
from flask import current_app, request, jsonify
from flask_jwt_extended import jwt_required
from mongoengine import DoesNotExist
from app.models import Form
from app.utils.decorator import require_roles
from app.models.Form import Form, FormResponse
from flask import json
from app.utils.webhooks import trigger_webhooks
from app.utils.email_helper import send_email_notification


# -------------------- Form Analytics --------------------
@form_bp.route("/<form_id>/analytics", methods=["GET"])
@jwt_required()
def get_form_analytics(form_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403

        responses = FormResponse.objects(form=form.id).order_by("-submitted_at")
        total = responses.count()
        latest = responses.first().submitted_at if total > 0 else None

        return jsonify({"total_responses": total, "latest_submission": latest}), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

# -------------------- Public Anonymous Submission --------------------
@form_bp.route("/<form_id>/public-submit", methods=["POST"])
def submit_public_response(form_id):
    data = request.get_json()
    try:
        form = Form.objects.get(id=form_id)

        # Check if form is published
        if form.status != "published":
            current_app.logger.warning(
                f"Attempted public submission to non-published form {form_id} (status: {form.status})")
            return jsonify({"error": f"Form is {form.status}, not accepting submissions"}), 403

        # Check if form has expired
        if form.expires_at and datetime.now(timezone.utc) > form.expires_at.replace(tzinfo=timezone.utc):
            current_app.logger.warning(
                f"Attempted public submission to expired form {form_id} (expired at: {form.expires_at})")
            return jsonify({"error": "Form has expired"}), 403

        # Check if form is scheduled for future
        now = datetime.now(timezone.utc)
        if form.publish_at and now < form.publish_at.replace(tzinfo=timezone.utc):
            current_app.logger.warning(
                f"Attempted public submission to future scheduled form {form_id} (publish at: {form.publish_at})")
            return jsonify({"error": "Form is not yet available"}), 403

        if not form.is_public:
            return jsonify({"error": "Form is not public"}), 403

        from app.routes.v1.form.validation import validate_form_submission
        submitted_data = data.get("data", {})
        validation_errors, cleaned_data = validate_form_submission(form, submitted_data, current_app.logger)

        if validation_errors:
            current_app.logger.warning(
                f"Public validation failed: {validation_errors}")
            return jsonify({"error": "Validation failed", "details": validation_errors}), 422

        response = FormResponse(
            form=form.id,
            submitted_by="anonymous",
            data=cleaned_data,
            submitted_at=datetime.now(timezone.utc),
            version=form.versions[-1].version if form.versions else "1.0"
        )
        response.save()
        
        # Trigger Webhook
        trigger_webhooks(form, "submitted", response.to_mongo().to_dict())

        # Trigger Email Notification
        if form.notification_emails:
            subject = f"New Public Submission: {form.title}"
            body = f"<h3>New public response for {form.title}</h3><p>Submitted by: Anonymous</p><p>Response ID: {response.id}</p>"
            send_email_notification(form.notification_emails, subject, body)
        
        return jsonify({"message": "Response submitted anonymously", "response_id": response.id}), 201
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@form_bp.route("/<string:form_id>/history", methods=["GET"])
@jwt_required()
def form_submission_history(form_id):
    current_user = get_current_user()
    try:
        question_id = request.args.get("question_id")
        primary_value = request.args.get("primary_value")
        auth = request.headers.get("Authorization")
        if not auth:
            token = request.cookies.get("access_token_cookie")
            if token:
                auth = f"Bearer {token}"


        if not question_id or not primary_value:
            return jsonify({"error": "Missing 'question_id' or 'primary_value' parameter"}), 400

        current_app.logger.info(
            f"User {current_user.username} is requesting submission history for form {form_id}, question {question_id} with value '{primary_value}'"
        )

        # Construct the search payload
        search_payload = {
            "data": {
                question_id: {
                    "value": primary_value,
                    "type": "string",
                    "fuzzy": True
                }
            },
            "limit": 100,
            "sort_by": "submitted_at",
            "sort_order": "asc",
            "include": {
                "questions": [],
                "sections": []
            }
        }

        # Forward the JWT token
        headers = {
            "Authorization": auth,
        }

        url = f"/form/api/v1/form/{form_id}/responses/search"
        current_app.logger.debug(f"Internal search URL: {url}, Payload: {search_payload}, Headers: {headers}")
        # Call the internal search route using requests
        response = current_app.test_client().post(
            url,
            data=json.dumps(search_payload),
            content_type="application/json",
            headers=headers
        )

        if response.status_code == 200:
            full_data = response.get_json().get("responses", [])
            result = [{"_id": r["_id"], "submitted_at": r["submitted_at"]} for r in full_data]
            return jsonify({"data": result}), 200
        else:
            current_app.logger.error(f"Search call failed for form {form_id}, question {question_id} with value '{primary_value}': {response.text}")
            return jsonify({"error": "Search call failed", "details": response.get_json()}), response.status_code

    except Exception as e:
        current_app.logger.error(f"Error fetching form submission history: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
