
# -------------------- Helper --------------------
from flask_jwt_extended import get_jwt_identity

from app.models.User import User


def get_current_user():
    user_id = get_jwt_identity()
    return User.objects(id=user_id).first()


def has_form_permission(user, form, action):
    user_id_str = str(user.id)
    if user.is_superadmin_check():
        return True

    # Creator always has all permissions
    if str(form.created_by) == user_id_str:
        return True

    if action == "edit":
        return user_id_str in (form.editors or [])
    if action == "view":
        return user_id_str in (form.viewers or []) or user_id_str in (form.editors or []) or form.is_public
    if action == "submit":
        return user_id_str in (form.submitters or []) or form.is_public
    return False

def apply_translations(form_dict, lang_code):
    """
    Applies translations to a form dictionary based on the provided language code.
    If translations for lang_code don't exist, returns the original dict.
    """
    if "versions" not in form_dict or not form_dict["versions"]:
        return form_dict
        
    latest_version = form_dict["versions"][-1]
    translations = latest_version.get("translations", {})
    
    if lang_code not in translations:
        return form_dict
        
    lang_translations = translations[lang_code]
    
    # Translate Top-level Form title/description
    if "title" in lang_translations:
        form_dict["title"] = lang_translations["title"]
    if "description" in lang_translations:
        form_dict["description"] = lang_translations["description"]
        
    # Translate Sections
    section_translations = lang_translations.get("sections", {})
    for section in latest_version.get("sections", []):
        sid = str(section.get("id") or section.get("_id"))
        if sid in section_translations:
            if "title" in section_translations[sid]:
                section["title"] = section_translations[sid]["title"]
            if "description" in section_translations[sid]:
                section["description"] = section_translations[sid]["description"]
                
        # Translate Questions
        question_translations = lang_translations.get("questions", {})
        for question in section.get("questions", []):
            qid = str(question.get("id") or question.get("_id"))
            if qid in question_translations:
                q_trans = question_translations[qid]
                if "label" in q_trans:
                    question["label"] = q_trans["label"]
                if "help_text" in q_trans:
                    question["help_text"] = q_trans["help_text"]
                if "placeholder" in q_trans:
                    question["placeholder"] = q_trans["placeholder"]
                
                # Translate Options
                if "options" in q_trans and "options" in question:
                    option_translations = q_trans["options"]
                    for option in question.get("options", []):
                        oid = str(option.get("id") or option.get("_id"))
                        if oid in option_translations:
                            option["option_label"] = option_translations[oid]

    return form_dict