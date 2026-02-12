# --- ENUMS ---
from enum import Enum

FORM_STATUS_CHOICES = ("draft", "published", "archived")
ui_TYPE_CHOICES = ("flex", "grid-cols-2", "tabbed", "custom")

FIELD_TYPE_CHOICES = (
    "input", "textarea", "select", "checkbox", "radio",
    "boolean", 
    "rating", "date", "file_upload", "api_search", "calculated",
    "file", "signature", "slider", "image", "divider", "spacer", "matrix_choice",
    "short_text", "paragraph", "number", "time", "dropdown", "checkboxes", "multiple_choice", "email", "mobile", "url"
)



FIELD_API_CALL_CHOICES = (
    "uhid",
    "employee_id",
    "form", 
    "otp",
    "custom"
)