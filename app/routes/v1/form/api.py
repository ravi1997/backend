import json
import random
import traceback

import requests
from app.routes.v1.form.helper import get_current_user, has_form_permission
from app.routes.v1.form import form_bp
from flask import current_app, request, jsonify, url_for
from flask_jwt_extended import jwt_required
from mongoengine import DoesNotExist
from app.models import Form
from app.models.User import User
from app.models.User import Role
from app.schemas.form_schema import FormSchema, FormVersionSchema, SectionSchema
from app.utils.api_helper import send_OTP_sms, send_ehospital_uhid
from app.utils.decorator import require_roles


@form_bp.route("<string:form_id>/section/<string:section_id>/question/<string:question_id>/api", methods=["GET"])
@jwt_required()
def handleAPI(form_id, section_id, question_id):
    current_user = get_current_user()
    try:
        current_app.logger.info(f"User {current_user.username} (ID: {current_user.id}) is attempting to retrieve UHID")
        form = Form.objects.get(id=form_id)
        section = None
        for s in form["versions"][-1].sections:
            if str(s.id) == str(section_id):
                section = s
                break

        if not section:
            current_app.logger.error(f"Section with ID {section_id} not found in form {form_id} for user {current_user.username} (ID: {current_user.id})")
            return jsonify({"error": "Section not found"}), 404

        question = None
        for q in section["questions"]:
            if str(q.id) == str(question_id):
                question = q
                break

        if not question:
            current_app.logger.error(f"Question with ID {question_id} not found in section {section_id} of form {form_id} for user {current_user.username} (ID: {current_user.id})")
            return jsonify({"error": "Question not found"}), 404

        
        api = question.field_api_call

        if api == "uhid":
            current_app.logger.info(f"User {current_user.username} (ID: {current_user.id}) is calling eHospital UHID API")
            uhid = request.args.get("value")
            if not uhid:
                return jsonify({"error": "Missing 'uhid' parameter"}), 400
            data = send_ehospital_uhid(current_app, uhid)
            if data is None:
                current_app.logger.error(f"Failed to retrieve UHID for user {current_user.username} (ID: {current_user.id})")
                return jsonify({"error": "Failed to retrieve UHID"}), 500
            current_app.logger.warning(f"UHID found(ID: {uhid})")
            return jsonify({"data": data}), 200
        elif api == "otp":
            current_app.logger.info(f"User {current_user.username} (ID: {current_user.id}) is calling OTP API")
            mobile = request.args.get("value")
            if not mobile:
                return jsonify({"error": "Missing 'mobile' parameter"}), 400
            otp = random.randint(100000, 999999)  # Generate a random OTP
            if send_OTP_sms(current_app, mobile, otp):
                current_app.logger.info(f"OTP sent successfully to {mobile} for user {current_user.username} (ID: {current_user.id})")
                return jsonify({"message": "OTP sent successfully","data":{"otp":otp}}), 200
            else:
                current_app.logger.error(f"Failed to send OTP to {mobile} for user {current_user.username} (ID: {current_user.id})")
                return jsonify({"error": "Failed to send OTP"}), 500
        elif api == "form":
            current_app.logger.info(f"User {current_user.username} (ID: {current_user.id}) is calling Form API")
            
            payload = request.args.get("value")
            if not payload:
                return jsonify({"error": "Missing 'payload' parameter"}), 400
            

            # Construct the same payload as you would send in a real /responses/search POST
            search_payload = json.loads(payload)

            form_id = search_payload.get("form_id")
            if not form_id:
                current_app.logger.error(f"Form ID not provided in search payload for user {current_user.username} (ID: {current_user.id})")
                return jsonify({"error": "Form ID is required"}), 400
            

            try:
                form = Form.objects.get(id=form_id)
                headers = {
                    "Authorization": request.headers.get("Authorization")  # Forward the JWT
                }
                response = current_app.test_client().post(
                    f"/api/v1/form/{form_id}/responses/search",
                    data=json.dumps(search_payload),
                    content_type="application/json",
                    headers=headers
                )
                if response.status_code == 200:
                    current_app.logger.info(f"Form data retrieved successfully for user {current_user.username} (ID: {current_user.id})")
                    return jsonify({"data": response.json()["responses"]}), 200
                else:
                    current_app.logger.error(f"Failed to retrieve form data for user {current_user.username} (ID: {current_user.id}): {response.text}")
                    return jsonify({"error": "Failed to retrieve form data"}), response.status_code


            except DoesNotExist:
                current_app.logger.error(f"Form with ID {form_id} not found for user {current_user.username} (ID: {current_user.id})")
                return jsonify({"error": "Form not found"}), 404

            return jsonify({"data": ""}), 200
        elif api == "custom":
            current_app.logger.info(f"User {current_user.username} (ID: {current_user.id}) is calling Custom API")
            custom_script = question.custom_script
            if not custom_script:
                return jsonify({"error": "Custom script not defined"}), 400
            try:
                exec(custom_script)  # Execute the custom script
                return jsonify({"message": "Custom script executed successfully"}), 200
            except Exception as e:
                current_app.logger.error(f"Error executing custom script for user {current_user.username} (ID: {current_user.id}): {str(e)}")
                return jsonify({"error": "Error executing custom script"}), 500
        else:
            current_app.logger.error(f"Unsupported API call '{api}' for user {current_user.username} (ID: {current_user.id})")
            return jsonify({"error": "Unsupported API call"}), 400
        

    except DoesNotExist:
        current_app.logger.error(f"Form, section or question not found for user {current_user.username} (ID: {current_user.id})")
        return jsonify({"error": "Either form, section or question not found"}), 404
    except Exception as e:
        error_trace = traceback.format_exc()
        current_app.logger.error(f"Error retrieving UHID for user {current_user.username} (ID: {current_user.id}): {str(e)}\n{error_trace}")
        return jsonify({"error": "Something went wrong"}), 500
    
