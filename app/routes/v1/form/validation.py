import json
import re
from datetime import datetime, timezone

def sanitize_uuid_for_eval(uuid_str):
    """
    Replaces dashes in UUID with underscores and adds a prefix to make it a valid identifier.
    Example: 123-456 -> v_123_456
    """
    return f"v_{uuid_str.replace('-', '_')}"

def prepare_eval_context(entries):
    """
    Creates a context dictionary where keys are sanitized UUIDs.
    Also keeps original keys just in case (as strings).
    """
    context = {}
    if entries:
        for entry in entries:
            for k, v in entry.items():
                # Add sanitized version
                safe_key = sanitize_uuid_for_eval(str(k))
                context[safe_key] = v
                # Add original version (quoted for string comparison if needed, though less likely for variable lookup)
                context[str(k)] = v
    return context

def evaluate_condition(condition, context, logger=None):
    """
    Evaluates a condition string against the context.
    Sanitizes UUIDs in the condition string to match sanitized context keys.
    """
    if not condition:
        return False
        
    try:
        # Regex to find UUID patterns
        uuid_pattern = r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
        
        def replace_uuid(match):
            return sanitize_uuid_for_eval(match.group(0))
            
        safe_condition = re.sub(uuid_pattern, replace_uuid, condition)
        
        if logger and safe_condition != condition:
            logger.debug(f"Sanitized condition: {condition} -> {safe_condition}")

        return eval(safe_condition, {"__builtins__": {}}, context)
    except Exception as err:
        if logger:
            logger.warning(f"Eval failed: {condition}, error={err}")
        return False

def validate_form_submission(form, submitted_data, logger):
    """
    Validates submitted data against form structure and rules.
    Returns a list of validation errors.
    """
    validation_errors = []
    
    # Get the latest version
    if not form.versions:
        return [{"error": "Form has no versions defined"}]
    
    latest_version = form.versions[-1]
    
    for section in latest_version.sections:
        sid = str(section.id)
        section_data = submitted_data.get(sid)
        
        logger.info(f"Processing section: {sid}, repeatable={section.is_repeatable_section}")

        if section.is_repeatable_section:
            if section_data is None:
                # If required, should have at least some entries? 
                # This depends on business logic, but usually if it's repeatable and required, repeat_min > 0
                if section.repeat_min and section.repeat_min > 0:
                    msg = f"At least {section.repeat_min} entries required"
                    validation_errors.append({"section_id": sid, "error": msg})
                continue
                
            if not isinstance(section_data, list):
                msg = "Expected a list of entries for repeatable section"
                validation_errors.append({"section_id": sid, "error": msg})
                logger.warning(f"{sid}: {msg}")
                continue

            if section.repeat_min and len(section_data) < section.repeat_min:
                msg = f"At least {section.repeat_min} entries required"
                validation_errors.append({"section_id": sid, "error": msg})
                logger.warning(f"{sid}: {msg}")

            if section.repeat_max and len(section_data) > section.repeat_max:
                msg = f"No more than {section.repeat_max} entries allowed"
                validation_errors.append({"section_id": sid, "error": msg})
                logger.warning(f"{sid}: {msg}")

            entries = section_data
        else:
            if section_data is None:
                # Non-repeatable sections might be optional overall? 
                # But usually they are present.
                entries = [{}] 
            elif not isinstance(section_data, dict):
                logger.warning(f"{sid}: Non-dict data in non-repeatable section, skipping.")
                continue
            else:
                entries = [section_data]

        for entry in entries:
            # Context for visibility/required conditions
            # For non-repeatable, context is the current entry.
            # For repeatable, context is also the current entry (standard behavior)
            context = prepare_eval_context(entries if isinstance(entries, list) else [entry])
            # Wait, the context should be for the current entry row if referencing siblings, 
            # OR typically one can reference any field in the same row.
            # In the original code: context = {str(k): repr(v) for k, v in entry.items()} 
            # It only included the current entry. Let's stick to that.
            context = prepare_eval_context([entry])

            for question in section.questions:
                qid = str(question.id)
                val = entry.get(qid) if entry else None
                logger.debug(f"Checking question {qid}, label={question.label}")

                # 1. Evaluate visibility
                is_visible = True
                if question.visibility_condition:
                    is_visible = evaluate_condition(question.visibility_condition, context, logger)
                    logger.debug(f"Visibility of {qid}: {is_visible}")

                if not is_visible:
                    continue

                # 2. Evaluate Conditional Required
                is_required = question.is_required
                if not is_required and hasattr(question, 'required_condition') and question.required_condition:
                    is_required = evaluate_condition(question.required_condition, context, logger)
                    if is_required:
                        logger.debug(f"Field {qid} is mandatory due to condition: {question.required_condition}")

                # Checkbox normalization (replicated from original logic)
                if question.field_type == "checkbox" and val is not None and not isinstance(val, list):
                    val = [val] if val else []

                # Handle repeatable questions
                if question.is_repeatable_question:
                    if not isinstance(val, list) and val is not None:
                        msg = "Expected list of answers for repeatable question"
                        validation_errors.append({"id": qid, "error": msg})
                        logger.warning(f"{qid}: {msg}")
                        continue
                    
                    if is_required and (val is None or len(val) == 0):
                        msg = "Required field missing"
                        validation_errors.append({"id": qid, "error": msg})
                        logger.warning(f"{qid}: {msg}")
                        continue

                    if val:
                        if question.repeat_min and len(val) < question.repeat_min:
                            msg = f"At least {question.repeat_min} entries required"
                            validation_errors.append({"id": qid, "error": msg})
                            logger.warning(f"{qid}: {msg}")
                        if question.repeat_max and len(val) > question.repeat_max:
                            msg = f"No more than {question.repeat_max} entries allowed"
                            validation_errors.append({"id": qid, "error": msg})
                            logger.warning(f"{qid}: {msg}")
                    
                    answers_to_check = val if val else []
                else:
                    answers_to_check = [val]

                for ans in answers_to_check:
                    if is_required and (ans is None or ans == ""):
                        msg = "Required field missing"
                        validation_errors.append({"id": qid, "error": msg})
                        logger.warning(f"{qid}: {msg}")
                        continue
                    
                    if ans in (None, ""):
                        continue

                    # Type checks
                    if question.field_type == "checkbox" and not isinstance(ans, list):
                        msg = "Expected a list for checkbox"
                        validation_errors.append({"id": qid, "error": msg})
                        logger.warning(f"{qid}: {msg}")
                    elif question.field_type in ("text", "textarea") and not isinstance(ans, str):
                        msg = "Expected a string for text/textarea"
                        validation_errors.append({"id": qid, "error": msg})
                        logger.warning(f"{qid}: {msg}")
                    elif question.field_type == "radio":
                        if not isinstance(ans, str):
                            msg = "Expected a string for radio"
                            validation_errors.append({"id": qid, "error": msg})
                            logger.warning(f"{qid}: {msg}")
                        elif val not in [opt.option_value for opt in question.options]:
                            msg = "Invalid option selected"
                            validation_errors.append({"id": qid, "error": msg})
                            logger.warning(f"{qid}: {msg}")
                    elif question.field_type == "file_upload":
                        if isinstance(ans, dict) and 'filepath' in ans:
                            pass
                        elif isinstance(ans, list):
                            for file_info in ans:
                                if not isinstance(file_info, dict) or 'filepath' not in file_info:
                                    msg = "Invalid file upload"
                                    validation_errors.append({"id": qid, "error": msg})
                                    logger.warning(f"{qid}: {msg}")
                        else:
                            msg = "Expected file upload for file_upload field type"
                            validation_errors.append({"id": qid, "error": msg})
                            logger.warning(f"{qid}: {msg}")

                    # Custom validation rules
                    if question.validation_rules:
                        try:
                            rules = json.loads(question.validation_rules)
                            if isinstance(ans, str):
                                if "min_length" in rules and len(ans) < rules["min_length"]:
                                    msg = f"Minimum length is {rules['min_length']}"
                                    validation_errors.append({"id": qid, "error": msg})
                                if "max_length" in rules and len(ans) > rules["max_length"]:
                                    msg = f"Maximum length is {rules['max_length']}"
                                    validation_errors.append({"id": qid, "error": msg})
                            if question.field_type == "checkbox" and isinstance(ans, list):
                                if "min_selections" in rules and len(ans) < rules["min_selections"]:
                                    msg = f"Select at least {rules['min_selections']} options"
                                    validation_errors.append({"id": qid, "error": msg})
                                if "max_selections" in rules and len(ans) > rules["max_selections"]:
                                    msg = f"Select no more than {rules['max_selections']} options"
                                    validation_errors.append({"id": qid, "error": msg})
                        except Exception as ve:
                            msg = f"Invalid validation rules: {str(ve)}"
                            validation_errors.append({"id": qid, "error": msg})
                            logger.error(f"{qid}: {msg}")
    
    return validation_errors
