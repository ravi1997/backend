import csv
import io
import json
from app.routes.v1.form.helper import get_current_user, has_form_permission
from app.routes.v1.form import form_bp
from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required
from mongoengine import DoesNotExist
from app.models import Form
from app.models.Form import Form, FormResponse

# -------------------- Export to CSV --------------------
@form_bp.route("/<form_id>/export/csv", methods=["GET"])
@jwt_required()
def export_responses_csv(form_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized to export"}), 403

        responses = FormResponse.objects(form=form)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["response_id", "submitted_by", "submitted_at", "data"])
        for r in responses:
            writer.writerow([r.id, r.submitted_by, r.submitted_at.isoformat(), r.data])

        output.seek(0)
        return Response(output.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": f"attachment;filename=form_{form_id}_responses.csv"})
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

@form_bp.route("/<form_id>/export/json", methods=["GET"])
@jwt_required()
def export_form_with_responses(form_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403

        responses = FormResponse.objects(form=form)
        data = {
            "form_metadata": {
                "id": str(form.id),
                "title": form.title,
                "slug": form.slug,
                "created_by": form.created_by,
                "created_at": str(form.created_at),
                "status": form.status,
                "is_public": form.is_public
            },
            "responses": [r.to_mongo().to_dict() for r in responses]
        }
        return Response(json.dumps(data, default=str), mimetype="application/json")
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404