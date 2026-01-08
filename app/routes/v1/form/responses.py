import json
from app.routes.v1.form.helper import get_current_user, has_form_permission
from app.routes.v1.form import form_bp
from flask import current_app, request, jsonify
from flask_jwt_extended import jwt_required
from mongoengine import DoesNotExist
from app.models import Form
from app.models.User import User
from app.models.User import Role
from app.utils.decorator import require_roles
from app.models.Form import Form, FormResponse, SavedSearch
from datetime import datetime, timezone
from mongoengine.queryset.visitor import Q
from app.utils.file_handler import save_uploaded_file
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
        if form.expires_at and datetime.now(timezone.utc) > form.expires_at.replace(tzinfo=timezone.utc):
            current_app.logger.warning(
                f"Attempted submission to expired form {form_id} (expired at: {form.expires_at})")
            return jsonify({"error": "Form has expired"}), 403

        current_user = get_current_user()
        current_app.logger.info(
            f"Current user: {current_user.id}, Form title: {form.title}")

        if not has_form_permission(current_user, form, "submit"):
            current_app.logger.warning(
                f"User {current_user.id} unauthorized to submit form {form_id}")
            return jsonify({"error": "Unauthorized to submit"}), 403

        validation_errors = []

        def safe_eval(expr, context):
            try:
                return eval(expr, {"__builtins__": {}}, context)
            except Exception as err:
                current_app.logger.warning(
                    f"Visibility eval failed: {expr}, context={context}, error={err}")
                return False

        for section in form.versions[-1].sections:
            sid = str(section.id)
            section_data = submitted_data.get(sid)
            current_app.logger.info(
                f"Processing section: {sid}, repeatable={section.is_repeatable_section}")

            if section.is_repeatable_section:
                if not isinstance(section_data, list) and section_data is not None:
                    msg = "Expected a list of entries for repeatable section"
                    validation_errors.append({"section_id": sid, "error": msg})
                    current_app.logger.warning(f"{sid}: {msg}")
                    continue

                if section.repeat_min and len(section_data) < section.repeat_min:
                    msg = f"At least {section.repeat_min} entries required"
                    validation_errors.append({"section_id": sid, "error": msg})
                    current_app.logger.warning(f"{sid}: {msg}")

                if section.repeat_max and len(section_data) > section.repeat_max:
                    msg = f"No more than {section.repeat_max} entries allowed"
                    validation_errors.append({"section_id": sid, "error": msg})
                    current_app.logger.warning(f"{sid}: {msg}")

                entries = section_data
            else:
                if not isinstance(section_data, dict):
                    current_app.logger.warning(
                        f"{sid}: Non-dict data in non-repeatable section, skipping.")
                    continue
                entries = [section_data]

            if entries is not None:
                for entry in entries:
                    for question in section.questions:
                        qid = str(question.id)
                        answer = entry.get(qid)
                        current_app.logger.debug(
                            f"Checking question {qid}, label={question.label}")

                        # Evaluate visibility
                        is_visible = True
                        if question.visibility_condition:
                            flat_context = {
                                k: repr(v) for e in entries for k, v in e.items()}
                            is_visible = safe_eval(
                                question.visibility_condition, flat_context)
                            current_app.logger.debug(
                                f"Visibility of {qid}: {is_visible}")

                        if not is_visible:
                            continue

                        # Checkbox normalization
                        if question.field_type == "checkbox" and not isinstance(answer, list):
                            answer = [answer] if answer else []

                        # Handle repeatable questions
                        if question.is_repeatable_question:
                            if not isinstance(answer, list) and answer is not None:
                                msg = "Expected list of answers for repeatable question"
                                validation_errors.append({"id": qid, "error": msg})
                                current_app.logger.warning(f"{qid}: {msg}")
                                continue
                            if question.repeat_min and len(answer) < question.repeat_min:
                                msg = f"At least {question.repeat_min} entries required"
                                validation_errors.append({"id": qid, "error": msg})
                                current_app.logger.warning(f"{qid}: {msg}")
                            if question.repeat_max and len(answer) > question.repeat_max:
                                msg = f"No more than {question.repeat_max} entries allowed"
                                validation_errors.append({"id": qid, "error": msg})
                                current_app.logger.warning(f"{qid}: {msg}")
                        else:
                            answer = [answer]

                        for val in answer:
                            if question.is_required and (val is None or val == ""):
                                msg = "Required field missing"
                                validation_errors.append({"id": qid, "error": msg})
                                current_app.logger.warning(f"{qid}: {msg}")
                                continue
                            if val in (None, ""):
                                continue

                            # Type checks
                            if question.field_type == "checkbox" and not isinstance(val, list):
                                msg = "Expected a list for checkbox"
                                validation_errors.append({"id": qid, "error": msg})
                                current_app.logger.warning(f"{qid}: {msg}")
                            elif question.field_type in ("text", "textarea") and not isinstance(val, str):
                                msg = "Expected a string for text/textarea"
                                validation_errors.append({"id": qid, "error": msg})
                                current_app.logger.warning(f"{qid}: {msg}")
                            elif question.field_type == "radio":
                                if not isinstance(val, str):
                                    msg = "Expected a string for radio"
                                    validation_errors.append(
                                        {"id": qid, "error": msg})
                                    current_app.logger.warning(f"{qid}: {msg}")
                                elif val not in [opt.option_value for opt in question.options]:
                                    msg = "Invalid option selected"
                                    validation_errors.append(
                                        {"id": qid, "error": msg})
                                    current_app.logger.warning(f"{qid}: {msg}")
                            elif question.field_type == "file_upload":
                                # For file uploads, validate that the uploaded file meets requirements
                                if isinstance(val, dict) and 'filepath' in val:
                                    # File was successfully uploaded, validation passes
                                    pass
                                elif isinstance(val, list):
                                    # Multiple files uploaded
                                    for file_info in val:
                                        if not isinstance(file_info, dict) or 'filepath' not in file_info:
                                            msg = "Invalid file upload"
                                            validation_errors.append({"id": qid, "error": msg})
                                            current_app.logger.warning(f"{qid}: {msg}")
                                else:
                                    msg = "Expected file upload for file_upload field type"
                                    validation_errors.append({"id": qid, "error": msg})
                                    current_app.logger.warning(f"{qid}: {msg}")

                            # Custom validation rules
                            if question.validation_rules:
                                try:
                                    rules = json.loads(question.validation_rules)
                                    if isinstance(val, str):
                                        if "min_length" in rules and len(val) < rules["min_length"]:
                                            msg = f"Minimum length is {rules['min_length']}"
                                            validation_errors.append(
                                                {"id": qid, "error": msg})
                                            current_app.logger.warning(
                                                f"{qid}: {msg}")
                                        if "max_length" in rules and len(val) > rules["max_length"]:
                                            msg = f"Maximum length is {rules['max_length']}"
                                            validation_errors.append(
                                                {"id": qid, "error": msg})
                                            current_app.logger.warning(
                                                f"{qid}: {msg}")
                                    if question.field_type == "checkbox" and isinstance(val, list):
                                        if "min_selections" in rules and len(val) < rules["min_selections"]:
                                            msg = f"Select at least {rules['min_selections']} options"
                                            validation_errors.append(
                                                {"id": qid, "error": msg})
                                            current_app.logger.warning(
                                                f"{qid}: {msg}")
                                        if "max_selections" in rules and len(val) > rules["max_selections"]:
                                            msg = f"Select no more than {rules['max_selections']} options"
                                            validation_errors.append(
                                                {"id": qid, "error": msg})
                                            current_app.logger.warning(
                                                f"{qid}: {msg}")
                                except Exception as ve:
                                    msg = f"Invalid validation rules: {str(ve)}"
                                    validation_errors.append(
                                        {"id": qid, "error": msg})
                                    current_app.logger.error(f"{qid}: {msg}")

        if validation_errors:
            current_app.logger.warning(
                f"Validation failed with errors: {validation_errors}")
            return jsonify({"error": "Validation failed", "details": validation_errors}), 422

        response = FormResponse(
            form=form,
            submitted_by=str(current_user.id),
            data=submitted_data,
            submitted_at=datetime.now(timezone.utc)
        )
        response.save()
        current_app.logger.info(f"Submission saved: response_id={response.id}")
        return jsonify({"message": "Response submitted", "response_id": response.id}), 201

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

        responses = FormResponse.objects(form=form)
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

        response = FormResponse.objects.get(id=response_id, form=form)
        return jsonify(response.to_mongo().to_dict()), 200
    except DoesNotExist:
        return jsonify({"error": "Response not found"}), 404

# -------------------- Update Submission --------------------
@form_bp.route("/<form_id>/responses/<response_id>", methods=["PUT"])
@jwt_required()
def update_submission(form_id, response_id):
    data = request.get_json()
    try:
        form = Form.objects.get(id=form_id)
        response = FormResponse.objects.get(id=response_id, form=form)
        current_user = get_current_user()
        if response.submitted_by != str(current_user.id):
            return jsonify({"error": "Unauthorized to update this submission"}), 403
        response.update(**data)
        return jsonify({"message": "Response updated"}), 200
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
        response = FormResponse.objects.get(id=response_id, form=form)
        current_user = get_current_user()
        if not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized to delete response"}), 403
        response.delete()
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
        responses = FormResponse.objects(form=form).skip(skip).limit(limit)
        total = FormResponse.objects(form=form).count()
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
        response = FormResponse.objects.get(id=response_id, form=form)
        current_user = get_current_user()
        if response.submitted_by != str(current_user.id) and not has_form_permission(current_user, form, "edit"):
            return jsonify({"error": "Unauthorized to archive this response"}), 403
        response.update(set__status="archived")
        return jsonify({"message": "Response archived"}), 200
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

        base_query = Q(form=form)

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
