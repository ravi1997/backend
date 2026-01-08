# --- ENUMS ---
from enum import Enum

FORM_STATUS_CHOICES = ("draft", "published", "archived")
ui_TYPE_CHOICES = ("flex", "grid-cols-2", "tabbed", "custom")

FIELD_TYPE_CHOICES = (
    "input", "textarea", "select", "checkbox", "radio",
    "boolean", 
    "rating", "date", "file_upload", "api_search", "calculated",
    "file"
)



FIELD_API_CALL_CHOICES = (
    "uhid",
    "employee_id",
    "form", 
    "otp",
    "custom"
)