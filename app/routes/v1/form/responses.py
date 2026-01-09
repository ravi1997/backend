import json
from app.routes.v1.form.helper import get_current_user, has_form_permission
from app.routes.v1.form import form_bp
from flask import current_app, request, jsonify
from flask_jwt_extended import jwt_required
from mongoengine import DoesNotExist
from app.models.User import User
from app.models.User import Role
from app.utils.decorator import require_roles
from app.models.Form import Form, FormResponse, SavedSearch, ResponseHistory, ResponseComment
from datetime import datetime, timezone
import uuid
from mongoengine.queryset.visitor import Q
from app.utils.file_handler import save_uploaded_file
from app.utils.webhooks import trigger_webhooks
from app.utils.email_helper import send_email_notification
from app.models.Workflow import FormWorkflow
from app.utils.script_engine import execute_safe_script

# -------------------- Responses --------------------


@form_bp.route("/<form_id>/responses", methods=["POST"])
@jwt_required()
def submit_response(form_id):
    current_app.logger.info(f"Received submission for form_id: {form_id}")

    # Check if the request contains file uploads
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle multipart form data (with file uploads)
        submitted_data = {}
        
        # Process regular form data
        for key, value in request.form.items():
            # Try to parse as JSON if possible, otherwise use as string
            try:
                submitted_data[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                submitted_data[key] = value
        
        # Process file uploads
        for key, file_list in request.files.lists():
            if isinstance(file_list, list) and len(file_list) > 0:
                if len(file_list) == 1:
                    # Single file upload
                    file_info = save_uploaded_file(file_list[0], form_id, key)
                    submitted_data[key] = file_info
                else:
                    # Multiple file uploads for the same question
                    files_info = []
                    for file in file_list:
                        file_info = save_uploaded_file(file, form_id, key)
                        if file_info:
                            files_info.append(file_info)
                    submitted_data[key] = files_info
    else:
        # Handle regular JSON data
        try:
            data = request.get_json(force=True)
            submitted_data = data.get("data", {})
            current_app.logger.info(f"Parsed JSON submission: {submitted_data}")
        except Exception as e:
            current_app.logger.warning(
                f"Failed JSON parse, falling back to form data. Error: {str(e)}")
            data = request.form or {}

            form_data = data.to_dict(flat=False)
            json_ready = {}
            for key, values in form_data.items():
                json_ready[key] = values[0] if len(values) == 1 else values
            submitted_data = json_ready
            current_app.logger.info(
                f"Parsed form data submission: {submitted_data}")

    try:
        form = Form.objects.get(id=form_id)

        # Check if form is published
        if form.status != "published":
            current_app.logger.warning(
                f"Attempted submission to non-published form {form_id} (status: {form.status})")
            return jsonify({"error": f"Form is {form.status}, not accepting submissions"}), 403

        # Check if form has expired
        now = datetime.now(timezone.utc)
        if form.expires_at and now > form.expires_at.replace(tzinfo=timezone.utc):
            current_app.logger.warning(
                f"Attempted submission to expired form {form_id} (expired at: {form.expires_at})")
            return jsonify({"error": "Form has expired"}), 403

        # Check if form is scheduled for future
        if form.publish_at and now < form.publish_at.replace(tzinfo=timezone.utc):
            current_app.logger.warning(
                f"Attempted submission to future scheduled form {form_id} (publish at: {form.publish_at})")
            return jsonify({"error": "Form is not yet available"}), 403

        current_user = get_current_user()
        current_app.logger.info(
            f"Current user: {current_user.id}, Form title: {form.title}")

        if not has_form_permission(current_user, form, "submit"):
            current_app.logger.warning(
                f"User {current_user.id} unauthorized to submit form {form_id}")
            return jsonify({"error": "Unauthorized to submit"}), 403

        from app.routes.v1.form.validation import validate_form_submission
        is_draft = request.args.get("draft", "false").lower() == "true"
        
        validation_errors, cleaned_data = validate_form_submission(form, submitted_data, current_app.logger, is_draft=is_draft)

        if validation_errors:
            current_app.logger.warning(
                f"Validation failed with errors: {validation_errors}")
            return jsonify({"error": "Validation failed", "details": validation_errors}), 422

        response = FormResponse(
            form=form.id,
            submitted_by=str(current_user.id),
            data=cleaned_data,
            submitted_at=datetime.now(timezone.utc),
            version=form.active_version or (form.versions[-1].version if form.versions else "1.0"),
            is_draft=is_draft
        )
        response.save()
        current_app.logger.info(f"Submission saved: response_id={response.id}, is_draft={is_draft}")
        
        # 📜 History Tracking: Record Creation
        ResponseHistory(
            response_id=response.id,
            form_id=form.id,
            data_before=None,
            data_after=cleaned_data,
            changed_by=str(current_user.id),
            change_type="create",
            version=response.version
        ).save()
        
        # Prepare clean data for history and triggers
        clean_response_dict = {
            "id": str(response.id),
            "form_id": str(form.id),
            "data": cleaned_data,
            "is_draft": is_draft,
            "submitted_by": response.submitted_by,
            "submitted_at": response.submitted_at.isoformat() if response.submitted_at else None,
            "version": response.version,
            "status": response.status
        }
        
        if not is_draft:
            # Trigger Webhook
            trigger_webhooks(form, "submitted", clean_response_dict)
            
            # Trigger Email Notification
            if form.notification_emails:
                subject = f"New Submission: {form.title}"
                body = f"<h3>New response for {form.title}</h3><p>Submitted by: {current_user.username} ({current_user.email})</p><p>Response ID: {response.id}</p>"
                send_email_notification(form.notification_emails, subject, body)
        
        msg = "Draft saved" if is_draft else "Response submitted"
        
        # -------------------- Workflow Evaluation --------------------
        workflow_action = None
        if not is_draft:
            try:
                # 1. Find active workflows for this form
                fid_str = str(form.id)
                workflows = FormWorkflow.objects(trigger_form_id=fid_str, is_active=True)
                
                # Flatten cleaned_data for easier access in scripts (merging all sections)
                flat_answers = {}
                for sid, s_val in cleaned_data.items():
                    if isinstance(s_val, dict):
                        flat_answers.update(s_val)
                    # Note: We skip repeatable sections/lists for now in simple global context
                
                for wf in workflows:
                    try:
                        # Evaluate condition
                        condition = wf.trigger_condition
                        if not condition or condition.strip() == "":
                             condition = "True"
                        
                        if condition != "True":
                            # Wrap condition to result
                            script = f"result = {condition}"
                            context = {"answers": flat_answers, "data": flat_answers}
                            
                            res = execute_safe_script(script, input_data=flat_answers, additional_globals=context)
                            
                            if res.get('result'):
                                # Match
                                actions_payload = []
                                for act in wf.actions:
                                    action_data = {
                                        "type": act.type,
                                        "target_form_id": act.target_form_id,
                                        "data_mapping": act.data_mapping,
                                        "assign_to_user_field": act.assign_to_user_field
                                    }
                                    actions_payload.append(action_data)
                                    
                                workflow_action = {
                                    "workflow_id": str(wf.id),
                                    "workflow_name": wf.name,
                                    "actions": actions_payload
                                }
                                break
                        else:
                             # Condition is True (default) -> Match
                             actions_payload = []
                             for act in wf.actions:
                                action_data = {
                                    "type": act.type,
                                    "target_form_id": act.target_form_id,
                                    "data_mapping": act.data_mapping,
                                    "assign_to_user_field": act.assign_to_user_field
                                }
                                actions_payload.append(action_data)
                                
                             workflow_action = {
                                "workflow_id": str(wf.id),
                                "workflow_name": wf.name,
                                "actions": actions_payload
                             }
                             break

                    except Exception as e:
                        current_app.logger.warning(f"Workflow condition failed: {e}")
                        
            except Exception as e:
                current_app.logger.error(f"Error evaluating workflows: {e}")

        response_payload = {"message": msg, "response_id": response.id}
        if workflow_action:
            response_payload["workflow_action"] = workflow_action
            
        return jsonify(response_payload), 201

    except DoesNotExist:
        current_app.logger.error(f"Form {form_id} not found.")
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        current_app.logger.error(
            f"Error submitting response: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

@form_bp.route("/<form_id>/responses", methods=["GET"])
@jwt_required()
def list_responses(form_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized to view responses"}), 403

        is_draft_filter = request.args.get("is_draft", "false").lower() == "true"
        responses = FormResponse.objects(form=form.id, deleted=False, is_draft=is_draft_filter)
        return jsonify([r.to_mongo().to_dict() for r in responses]), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404


@form_bp.route("/<form_id>/responses/<response_id>", methods=["GET"])
@jwt_required()
def get_response(form_id, response_id):
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized to view this response"}), 403

        response = FormResponse.objects.get(id=response_id, form=form.id)
        return jsonify(response.to_mongo().to_dict()), 200
    except DoesNotExist:
        return jsonify({"error": "Response not found"}), 404

# -------------------- Get History --------------------
@form_bp.route("/<form_id>/responses/<response_id>/history", methods=["GET"])
@jwt_required()
def get_response_history(form_id, response_id):
    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403
            
        history = ResponseHistory.objects(response_id=response_id).order_by("-changed_at")
        return jsonify([h.to_mongo().to_dict() for h in history]), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

# -------------------- Update Submission --------------------
@form_bp.route("/<form_id>/responses/<response_id>", methods=["PUT"])
@jwt_required()
def update_submission(form_id, response_id):
    data = request.get_json()
    
    try:
        current_user = get_current_user()
    except DoesNotExist:
        current_app.logger.error(f"User not found for token")
        return jsonify({"error": "User not found"}), 404

    try:
        current_app.logger.info(f"Updating submission form={form_id} resp={response_id}")
        form = Form.objects.get(id=form_id)
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

    try:
        response = FormResponse.objects.get(id=response_id, form=form_id)
    except DoesNotExist:
        return jsonify({"error": "Response not found"}), 404

    try:
        if response.submitted_by != str(current_user.id):
            return jsonify({"error": "Unauthorized to update this submission"}), 403
            
        # 📜 History Tracking: Before
        data_before = response.to_mongo().to_dict()

        # Validation Logic
        is_draft_param = request.args.get("draft")
        is_target_draft = False
        if is_draft_param is not None:
            is_target_draft = is_draft_param.lower() == "true"
        
        from app.routes.v1.form.validation import validate_form_submission
        submitted_data = data.get("data", data)
        validation_errors, cleaned_data = validate_form_submission(form, submitted_data, current_app.logger, is_draft=is_target_draft)

        if validation_errors:
            return jsonify({"error": "Validation failed", "details": validation_errors}), 422

        was_draft = response.is_draft
        
        # Update response
        response.update(
            set__data=cleaned_data,
            set__is_draft=is_target_draft,
            set__updated_at=datetime.now(timezone.utc),
            set__updated_by=str(current_user.id)
        )
        
        # Prepare clean data for history and triggers without dereferencing everything
        # We use a mix of local variables and existing response data
        clean_response_dict = {
            "id": str(response.id),
            "form_id": str(form.id),
            "data": cleaned_data,
            "is_draft": is_target_draft,
            "submitted_by": response.submitted_by,
            "submitted_at": response.submitted_at.isoformat() if response.submitted_at else None,
            "version": response.version,
            "status": response.status
        }

        # 📜 History Tracking: Record
        ResponseHistory(
            response_id=response.id,
            form_id=form.id,
            data_before=data_before.get("data"),
            data_after=cleaned_data,
            changed_by=str(current_user.id),
            change_type="update",
            version=response.version
        ).save()

        # 🔔 Triggers: Transition from Draft to Submitted
        if was_draft and not is_target_draft:
            trigger_webhooks(form, "submitted", clean_response_dict)
            if form.notification_emails:
                subject = f"New Submission (from draft): {form.title}"
                body = f"<h3>New response for {form.title}</h3><p>Submitted by: {current_user.username}</p><p>Response ID: {response.id}</p>"
                send_email_notification(form.notification_emails, subject, body)
        elif not is_target_draft:
            # Normal update trigger
            trigger_webhooks(form, "updated", clean_response_dict)
        return jsonify({"message": "Response updated", "is_draft": is_target_draft}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating submission: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

# -------------------- Update Response Status --------------------
@form_bp.route("/<form_id>/responses/<response_id>/status", methods=["PATCH"])
@jwt_required()
def update_response_status(form_id, response_id):
    data = request.get_json()
    new_status = data.get("status")
    comment = data.get("comment", "")
    
    if new_status not in ["pending", "approved", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    try:
        current_user = get_current_user()
        form = Form.objects.get(id=form_id)
        
        # Only editors or creators (who are editors) can approve/reject
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized to change status"}), 403

        response = FormResponse.objects.get(id=response_id, form=form.id)
        
        # 📜 History Tracking: Before
        data_before = response.to_mongo().to_dict()

        # Update status
        log_entry = {
            "status": new_status,
            "changed_by": str(current_user.id),
            "changed_at": datetime.now(timezone.utc),
            "comment": comment
        }
        
        response.update(
            set__status=new_status,
            push__status_log=log_entry,
            set__updated_at=datetime.now(timezone.utc),
            set__updated_by=str(current_user.id)
        )
        
        # Reload for history recording
        response = FormResponse.objects.get(id=response.id)

        # 📜 History Tracking: Record (Status Change)
        ResponseHistory(
            response_id=response.id,
            form_id=form.id,
            data_before=data_before.get("data"), # Data didn't change, but keep context
            data_after=response.data,
            changed_by=str(current_user.id),
            change_type="update",
            version=response.version
        ).save()
        
        # 🔔 Webhook
        trigger_webhooks(form, "status_updated", {
            "response_id": str(response.id), 
            "status": new_status,
            "comment": comment
        })

        # 📧 Email Notification for Status Change
        if form.notification_emails:
            subject = f"Response Status Updated: {new_status.capitalize()}"
            body = f"""
            <h3>Submission status changed for {form.title}</h3>
            <p><b>Status:</b> {new_status.capitalize()}</p>
            <p><b>Comment:</b> {comment or "No comment provided"}</p>
            <p><b>Response ID:</b> {response.id}</p>
            <p><b>Changed by:</b> {current_user.username}</p>
            """
            send_email_notification(form.notification_emails, subject, body)

        return jsonify({"message": f"Response status updated to {new_status}"}), 200

    except DoesNotExist:
        return jsonify({"error": "Form or response not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -------------------- Delete Individual Response --------------------
@form_bp.route("/<form_id>/responses/<response_id>", methods=["DELETE"])
@jwt_required()
def delete_response(form_id, response_id):
    try:
        form = Form.objects.get(id=form_id)
        response = FormResponse.objects.get(id=response_id, form=form.id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized to delete response"}), 403
        # 📜 History Tracking: Before
        data_before = response.to_mongo().to_dict()

        response.update(
            set__deleted=True, 
            set__deleted_at=datetime.now(timezone.utc),
            set__deleted_by=str(current_user.id)
        )
        
        # 📜 History Tracking: Record
        ResponseHistory(
            response_id=response.id,
            form_id=form.id,
            data_before=data_before.get("data"),
            data_after=None,
            changed_by=str(current_user.id),
            change_type="delete",
            version=response.version
        ).save()

        # 🔔 Webhook
        trigger_webhooks(form, "deleted", {"response_id": str(response.id), "deleted_by": str(current_user.id)})

        return jsonify({"message": "Response deleted"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form or response not found"}), 404

# -------------------- Paginate Responses --------------------
@form_bp.route("/<form_id>/responses/paginated", methods=["GET"])
@jwt_required()
def list_paginated_responses(form_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403

        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        skip = (page - 1) * limit
        is_draft_filter = request.args.get("is_draft", "false").lower() == "true"
        responses = FormResponse.objects(form=form.id, deleted=False, is_draft=is_draft_filter).skip(skip).limit(limit)
        query = FormResponse.objects(form=form.id, deleted=False, is_draft=is_draft_filter)
        total = query.count()
        return jsonify({
            "total": total,
            "page": page,
            "responses": [r.to_mongo().to_dict() for r in responses]
        }), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404


# -------------------- Archive Specific Response --------------------
@form_bp.route("/<form_id>/responses/<response_id>/archive", methods=["PATCH"])
@jwt_required()
def archive_response(form_id, response_id):
    try:
        form = Form.objects.get(id=form_id)
        response = FormResponse.objects.get(id=response_id, form=form.id)
        current_user = get_current_user()
        if response.submitted_by != str(current_user.id) and not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized to archive this response"}), 403
        response.update(
            set__deleted=True, 
            set__deleted_at=datetime.now(timezone.utc),
            set__deleted_by=str(current_user.id)
        )
        return jsonify({"message": "Response archived"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form or response not found"}), 404


# -------------------- Restore Specific Response --------------------
@form_bp.route("/<form_id>/responses/<response_id>/restore", methods=["PATCH"])
@jwt_required()
def restore_response(form_id, response_id):
    try:
        form = Form.objects.get(id=form_id)
        response = FormResponse.objects.get(id=response_id, form=form.id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized to restore this response"}), 403
        response.update(
            set__deleted=False,
            unset__deleted_at=True,
            unset__deleted_by=True
        )

        # 📜 History Tracking: Record Restore
        ResponseHistory(
            response_id=response.id,
            form_id=form.id,
            data_before=None, # Or we could fetch previous data but it didn't change 'data' itself
            data_after=response.data,
            changed_by=str(current_user.id),
            change_type="restore",
            version=response.version
        ).save()

        return jsonify({"message": "Response restored"}), 200
    except DoesNotExist:
        return jsonify({"error": "Form or response not found"}), 404


@form_bp.route("/<form_id>/responses/search", methods=["POST"])
@jwt_required()
def search_responses(form_id):
    try:
        current_user = get_current_user()
        current_app.logger.info(
            f"User {current_user.username} (ID: {current_user.id}) is searching responses for form ID: {form_id}")

        form = Form.objects.get(id=form_id)
        filters = request.get_json(force=True)
        current_app.logger.debug(f"Received filters: {filters}")

        if "saved_search_id" in filters:
            saved = SavedSearch.objects.get(
                id=filters["saved_search_id"], form=form)
            filters.update(saved.filters)
            current_app.logger.debug(
                f"Injected saved search filters: {saved.filters}")

        sort_by = filters.get("sort_by", "submitted_at")
        sort_order = filters.get("sort_order", "desc")
        sort_prefix = "-" if sort_order == "desc" else ""
        limit = int(filters.get("limit", 10))
        direction = filters.get("direction", "next")
        cursor = filters.get("cursor")

        is_draft_val = filters.get("is_draft", False)
        base_query = Q(form=form.id, deleted=False, is_draft=is_draft_val)

        # 🔁 Build question_id → section_id map
        qid_to_sid = {
            str(q.id): str(s.id)
            for s in form.versions[-1].sections
            for q in s.questions
        }

        # 🧠 Data Filters
        data_filters = filters.get("data", {})
        for question_id, condition in data_filters.items():
            current_app.logger.debug(
                f"Applying filter on question ID {question_id}: {condition}")
            section_id = qid_to_sid.get(question_id)
            if not section_id:
                continue  # skip invalid question ID

            key = f"data__{section_id}__{question_id}"

            if isinstance(condition, dict) and "value" in condition:
                value = condition["value"]
                data_type = condition.get("type")
                op = condition.get("op", "eq")
                fuzzy = condition.get("fuzzy", False)

                if data_type == "number":
                    value = float(value)
                elif data_type == "date":
                    value = datetime.fromisoformat(value)

                if op.startswith("$"):
                    op = op[1:]

                if data_type == "string" and fuzzy:
                    base_query &= Q(**{f"{key}__icontains": value})
                elif op != "eq":
                    base_query &= Q(**{f"{key}__{op}": value})
                else:
                    base_query &= Q(**{key: value})
            else:
                base_query &= Q(**{key: condition})

        if "submitted_by" in filters:
            base_query &= Q(submitted_by=filters["submitted_by"])

        if "date_range" in filters:
            start = filters["date_range"].get("start")
            end = filters["date_range"].get("end")
            if start:
                base_query &= Q(
                    submitted_at__gte=datetime.fromisoformat(start))
            if end:
                base_query &= Q(submitted_at__lte=datetime.fromisoformat(end))

        # 🔁 Nested logical filters
        def build_q(condition):
            if "$or" in condition:
                return Q.__or__(*[build_q(sub) for sub in condition["$or"]])
            elif "$and" in condition:
                return Q.__and__(*[build_q(sub) for sub in condition["$and"]])
            elif "$not" in condition:
                try:
                    return ~build_q(condition["$not"])
                except Exception as e:
                    current_app.logger.warning(
                        f"Invalid $not block: {condition['$not']}, error: {str(e)}")
                    return Q()
            else:
                k, v = list(condition.items())[0]
                k = k.replace(".", "__")
                if isinstance(v, dict):
                    op_key = list(v.keys())[0]
                    if op_key.startswith("$"):
                        op = op_key.lstrip("$")
                        return Q(**{f"{k}__{op}": v[op_key]})
                return Q(**{k: v})

        if "where" in filters:
            base_query &= build_q(filters["where"])

        if cursor:
            cursor_dt = datetime.fromisoformat(cursor)
            op_key = "gt" if sort_order == "asc" else "lt"
            if direction == "prev":
                op_key = "lt" if sort_order == "asc" else "gt"
            base_query &= Q(**{f"{sort_by}__{op_key}": cursor_dt})

        results = (
            FormResponse.objects(base_query)
            .order_by(f"{sort_prefix}{sort_by}")
            .limit(limit)
        )

        results_list = list(results)
        if direction == "prev":
            results_list.reverse()

        next_cursor = prev_cursor = None
        if results_list:
            first_item = results_list[0]
            last_item = results_list[-1]
            next_cursor = last_item.submitted_at.isoformat()
            prev_cursor = first_item.submitted_at.isoformat()

        include = filters.get("include", {})
        allowed_sections = set(include.get("sections", []))
        allowed_questions = set(include.get("questions", []))

        # 🧠 Map: question → section
        question_to_section = {}
        for section in form.versions[-1].sections:
            sid = str(section.id)
            for question in section.questions:
                question_to_section[str(question.id)] = sid


        def filter_response_data(response_obj):
            raw = response_obj.to_mongo().to_dict()
            full_data = raw.get("data", {})
            filtered_data = {}

            for sid, secdata in full_data.items():
                if isinstance(secdata, dict):
                    filtered_data[sid] = {
                        qid: val for qid, val in secdata.items()
                        if (not allowed_sections or sid in allowed_sections)
                        and (not allowed_questions or qid in allowed_questions)
                    }
                elif isinstance(secdata, list):  # handle repeatable sections
                    filtered_data[sid] = []
                    for row in secdata:
                        if isinstance(row, dict):
                            filtered_row = {
                                qid: val for qid, val in row.items()
                                if (not allowed_sections or sid in allowed_sections)
                                and (not allowed_questions or qid in allowed_questions)
                            }
                            filtered_data[sid].append(filtered_row)

            raw["data"] = filtered_data
            return raw


        return jsonify({
            "next_cursor": next_cursor,
            "prev_cursor": prev_cursor,
            "limit": limit,
            "responses": [filter_response_data(r) for r in results_list]
        }), 200

    except DoesNotExist:
        return jsonify({"error": "Form or SavedSearch not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# -------------------- Saved Searches --------------------

@form_bp.route("/<form_id>/saved-search", methods=["POST"])
@jwt_required()
def create_saved_search(form_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403
            
        data = request.get_json()
        saved = SavedSearch(
            user_id=str(current_user.id),
            form=form.id,
            name=data.get("name"),
            filters=data.get("filters")
        )
        saved.save()
        return jsonify({"message": "Saved search created", "id": str(saved.id)}), 201
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@form_bp.route("/<form_id>/saved-search", methods=["GET"])
@jwt_required()
def list_saved_searches(form_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403
            
        searches = SavedSearch.objects(form=form, user_id=str(current_user.id))
        return jsonify([{
            "id": str(s.id), 
            "name": s.name, 
            "filters": s.filters, 
            "created_at": s.created_at.isoformat()
        } for s in searches]), 200
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404


@form_bp.route("/<form_id>/saved-search/<search_id>", methods=["DELETE"])
@jwt_required()
def delete_saved_search(form_id, search_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        saved = SavedSearch.objects.get(id=search_id, form=form, user_id=str(current_user.id))
        saved.delete()
        return jsonify({"message": "Saved search deleted"}), 200
    except DoesNotExist:
        return jsonify({"error": "Saved search not found"}), 404

# -------------------- Comments --------------------

@form_bp.route("/<form_id>/responses/<response_id>/comments", methods=["GET"])
@jwt_required()
def get_response_comments(form_id, response_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403
            
        # Ensure response belongs to form
        try:
            response = FormResponse.objects.get(id=response_id, form=form.id)
        except DoesNotExist:
            return jsonify({"error": "Response not found"}), 404
            
        comments = ResponseComment.objects(response=response).order_by("created_at")
        
        return jsonify([json.loads(c.to_json()) for c in comments]), 200
        
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

@form_bp.route("/<form_id>/responses/<response_id>/comments", methods=["POST"])
@jwt_required()
def add_response_comment(form_id, response_id):
    try:
        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        
        # 'view' permission is enough to comment for internal collaborators
        if not has_form_permission(current_user, form, "view"):
            return jsonify({"error": "Unauthorized"}), 403
            
        try:
            response = FormResponse.objects.get(id=response_id, form=form.id)
        except DoesNotExist:
            return jsonify({"error": "Response not found"}), 404
            
        data = request.get_json()
        content = data.get("content")
        
        if not content:
            return jsonify({"error": "Content required"}), 400
            
        comment = ResponseComment(
            response=response,
            user_id=str(current_user.id),
            user_name=current_user.username or "Unknown",
            content=content
        )
        comment.save()
        
        # Log if needed? Or just return
        return jsonify(json.loads(comment.to_json())), 201
        
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

# -------------------- Preview / Validation --------------------
@form_bp.route("/<form_id>/preview", methods=["POST"])
@jwt_required()
def preview_submission(form_id):
    """
    Validate submission data without saving it.
    Useful for testing forms or 'Preview Mode'.
    """
    current_app.logger.info(f"Received preview/validation request for form_id: {form_id}")
    
    # Parse Data
    submitted_data = {}
    if request.is_json:
        data = request.get_json()
        submitted_data = data.get("data", data)
    else:
        # Fallback for form-data
        data = request.form or {}
        form_data = data.to_dict(flat=False)
        for key, values in form_data.items():
            submitted_data[key] = values[0] if len(values) == 1 else values

    try:
        form = Form.objects.get(id=form_id)
    except DoesNotExist:
        return jsonify({"error": "Form not found"}), 404

    current_user = get_current_user()
    
    # Preview allowed for anyone who can view (editor or viewer)
    # Creator is usually an editor.
    if not has_form_permission(current_user, form, "view"):
        return jsonify({"error": "Unauthorized to preview form"}), 403

    from app.routes.v1.form.validation import validate_form_submission
    
    try:
        # We pass the logger from current_app
        validation_errors, cleaned_data = validate_form_submission(form, submitted_data, current_app.logger)
        
        if validation_errors:
            return jsonify({
                "valid": False,
                "errors": validation_errors,
                "message": "Validation failed"
            }), 200
        
        return jsonify({
            "valid": True,
            "data": cleaned_data,
            "message": "Validation successful"
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error during preview validation: {str(e)}")
        return jsonify({"error": str(e)}), 400

@form_bp.route("/<form_id>/responses/merge", methods=["POST"])
@jwt_required()
def merge_responses(form_id):
    """
    Combine multiple responses into one.
    """
    try:
        data = request.get_json()
        source_ids = data.get("source_response_ids", [])
        target_id = data.get("target_response_id")
        delete_sources = data.get("delete_sources", True)

        if not source_ids:
            return jsonify({"error": "Missing source_response_ids"}), 400

        form = Form.objects.get(id=form_id)
        current_user = get_current_user()
        
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized"}), 403

        # Fetch all candidate responses
        query_ids = list(set(source_ids + ([target_id] if target_id else [])))
        all_resps = FormResponse.objects(id__in=query_ids, form=form.id, deleted=False)
        resp_map = {str(r.id): r for r in all_resps}

        sources = [resp_map[sid] for sid in source_ids if sid in resp_map]
        if not sources:
            return jsonify({"error": "No valid source responses found"}), 404

        target = resp_map.get(target_id) if target_id else None

        # Build merged data
        merged_data = {}
        # We'll use the target's data as base if it exists
        if target:
            merged_data = json.loads(json.dumps(target.data)) # Deep copy

        for src in sources:
            if target and str(src.id) == str(target.id):
                continue
                
            for sid, sec_data in src.data.items():
                if sid not in merged_data:
                    merged_data[sid] = sec_data
                else:
                    # Merge Logic
                    if isinstance(sec_data, dict) and isinstance(merged_data[sid], dict):
                        for k, v in sec_data.items():
                            if v is not None:
                                merged_data[sid][k] = v
                    elif isinstance(sec_data, list) and isinstance(merged_data[sid], list):
                        # Append entries (repeatable sections)
                        merged_data[sid].extend(sec_data)
                    elif sec_data is not None:
                        # Overwrite if source has value
                        merged_data[sid] = sec_data

        if not target:
            target = FormResponse(
                form=form.id,
                submitted_by=str(current_user.id),
                data=merged_data,
                submitted_at=datetime.now(timezone.utc),
                version=form.active_version or (form.versions[-1].version if form.versions else "1.0")
            )
        else:
            target.data = merged_data
            target.updated_at = datetime.now(timezone.utc)
            target.updated_by = str(current_user.id)

        target.save()

        # History
        ResponseHistory(
            response_id=target.id,
            form_id=form.id,
            data_after=merged_data,
            changed_by=str(current_user.id),
            change_type="merge", # 'merge' is also fine but let's stick to base types
            version=target.version,
            metadata={"merged_from": [str(s.id) for s in sources if str(s.id) != str(target.id)]}
        ).save()

        # Delete sources
        history_entries = []
        for src in sources:
            if str(src.id) == str(target.id):
                continue
            if delete_sources:
                src.update(set__deleted=True, set__deleted_at=datetime.now(timezone.utc), set__deleted_by=str(current_user.id))
                history_entries.append(ResponseHistory(
                    response_id=src.id,
                    form_id=form.id,
                    data_before=src.data,
                    changed_by=str(current_user.id),
                    change_type="delete",
                    metadata={"merged_into": str(target.id)}
                ))
        
        if history_entries:
            ResponseHistory.objects.insert(history_entries)

        return jsonify({
            "message": "Responses merged", 
            "target_id": str(target.id),
            "merged_count": len(sources)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Merge error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400
@form_bp.route("/<form_id>/responses/<response_id>/approve", methods=["POST"])
@jwt_required()
def approve_response_step(form_id, response_id):
    """
    Approve the current step in the multi-step workflow.
    """
    try:
        data = request.get_json() or {}
        comment = data.get("comment", "")
        
        form = Form.objects.get(id=form_id)
        response = FormResponse.objects.get(id=response_id, form=form.id)
        current_user = get_current_user()
        
        if not form.approval_enabled or not form.approval_steps:
            return jsonify({"error": "Approval workflow not enabled for this form"}), 400
            
        if response.status != "pending":
             return jsonify({"error": f"Cannot approve response in status: {response.status}"}), 400

        # Current step
        idx = response.current_approval_step_index
        if idx >= len(form.approval_steps):
            return jsonify({"error": "All approval steps already completed"}), 400
            
        current_step = form.approval_steps[idx]
        
        # Check permission: User must have the required role OR be an admin
        if current_step.required_role not in current_user.roles and 'admin' not in current_user.roles:
             return jsonify({"error": f"Unauthorized. Required role: {current_step.required_role}"}), 403

        # Record approval
        log_entry = {
            "step_id": str(current_step.id),
            "step_name": current_step.name,
            "approved_by": str(current_user.id),
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "status": "approved",
            "comment": comment
        }
        
        new_idx = idx + 1
        final_status = "pending"
        if new_idx >= len(form.approval_steps):
            final_status = "approved"

        response.update(
            set__current_approval_step_index=new_idx,
            push__approval_history=log_entry,
            set__status=final_status,
            set__updated_at=datetime.now(timezone.utc),
            set__updated_by=str(current_user.id)
        )
        
        # History
        ResponseHistory(
            response_id=response.id,
            form_id=form.id,
            data_after=response.data,
            changed_by=str(current_user.id),
            change_type="update",
            metadata={"approval_step": current_step.name, "action": "approved"}
        ).save()

        return jsonify({
            "message": f"Step '{current_step.name}' approved",
            "status": final_status,
            "completed_steps": new_idx,
            "total_steps": len(form.approval_steps)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Approval error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

@form_bp.route("/<form_id>/responses/<response_id>/reject", methods=["POST"])
@jwt_required()
def reject_response_step(form_id, response_id):
    """
    Reject the response at the current approval step.
    """
    try:
        data = request.get_json() or {}
        comment = data.get("comment", "")
        
        form = Form.objects.get(id=form_id)
        response = FormResponse.objects.get(id=response_id, form=form.id)
        current_user = get_current_user()
        
        if not form.approval_enabled or not form.approval_steps:
            return jsonify({"error": "Approval workflow not enabled"}), 400

        idx = response.current_approval_step_index
        if idx >= len(form.approval_steps):
            return jsonify({"error": "Approval already finalized"}), 400

        current_step = form.approval_steps[idx]

        if current_step.required_role not in current_user.roles and 'admin' not in current_user.roles:
             return jsonify({"error": f"Unauthorized. Required role: {current_step.required_role}"}), 403

        log_entry = {
            "step_id": str(current_step.id),
            "step_name": current_step.name,
            "rejected_by": str(current_user.id),
            "rejected_at": datetime.now(timezone.utc).isoformat(),
            "status": "rejected",
            "comment": comment
        }

        response.update(
            push__approval_history=log_entry,
            set__status="rejected",
            set__updated_at=datetime.now(timezone.utc),
            set__updated_by=str(current_user.id)
        )

        ResponseHistory(
            response_id=response.id,
            form_id=form.id,
            data_after=response.data,
            changed_by=str(current_user.id),
            change_type="update",
            metadata={"approval_step": current_step.name, "action": "rejected"}
        ).save()

        return jsonify({"message": f"Rejected at step '{current_step.name}'"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
